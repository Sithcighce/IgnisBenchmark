#!/usr/bin/env python3
"""
Model Fallback Manager
Handles multi-model fallback and concurrent request management
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import random

class ModelProvider(Enum):
    GEMINI = "gemini"
    SILICONFLOW = "siliconflow"
    LM_STUDIO = "lm_studio"

@dataclass
class ModelConfig:
    model: str
    provider: ModelProvider
    priority: int
    max_retries: int = 2
    timeout: int = 120

class ModelFallbackManager:
    """Manages model fallback and concurrent request handling"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Parse model configurations
        self.generation_models = self._parse_model_configs(
            config.get('generation_models', [])
        )
        self.answering_models = self._parse_model_configs(
            config.get('answering_models', [])
        )
        self.grading_models = self._parse_model_configs(
            config.get('grading_models', [])
        )
        
        # Concurrency settings
        self.max_concurrent = config.get('max_concurrent_requests', 10)
        self.rate_limit_delay = config.get('rate_limit_delay', 0.5)
        self.retry_delay = config.get('retry_delay', 1)
        self.fallback_enabled = config.get('fallback_enabled', True)
        
        # Request semaphore for concurrency control
        self.request_semaphore = asyncio.Semaphore(self.max_concurrent)
        
        # Model usage statistics
        self.model_stats = {}
    
    def _parse_model_configs(self, model_list: List[Dict]) -> List[ModelConfig]:
        """Parse model configuration list"""
        configs = []
        for model_data in model_list:
            provider_str = model_data.get('provider', 'gemini')
            try:
                provider = ModelProvider(provider_str)
            except ValueError:
                self.logger.warning(f"Unknown provider: {provider_str}, defaulting to gemini")
                provider = ModelProvider.GEMINI
                
            config = ModelConfig(
                model=model_data['model'],
                provider=provider,
                priority=model_data.get('priority', 999),
                max_retries=self.config.get('retry_attempts', 2),
                timeout=self.config.get('timeout_seconds', 120)
            )
            configs.append(config)
        
        # Sort by priority
        return sorted(configs, key=lambda x: x.priority)
    
    async def call_with_fallback(
        self, 
        model_type: str, 
        call_function, 
        *args, 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """
        Call a function with model fallback support
        
        Args:
            model_type: 'generation', 'answering', or 'grading'
            call_function: The function to call (should accept model config as first arg)
            *args, **kwargs: Arguments to pass to the function
        """
        
        # Get appropriate model list
        if model_type == 'generation':
            models = self.generation_models
        elif model_type == 'answering':
            models = self.answering_models
        elif model_type == 'grading':
            models = self.grading_models
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        if not models:
            raise ValueError(f"No models configured for {model_type}")
        
        # Try each model in priority order
        for model_config in models:
            try:
                result = await self._call_with_retries(
                    call_function, model_config, *args, **kwargs
                )
                if result is not None:
                    # Record successful usage
                    self._record_usage(model_config, True)
                    return result
                    
            except Exception as e:
                self.logger.warning(
                    f"Model {model_config.model} failed: {e}"
                )
                self._record_usage(model_config, False)
                
                if not self.fallback_enabled:
                    raise
                    
                continue
        
        # All models failed
        self.logger.error(f"All {model_type} models failed")
        return None
    
    async def _call_with_retries(
        self, 
        call_function, 
        model_config: ModelConfig, 
        *args, 
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Call function with retries for a specific model"""
        
        for attempt in range(model_config.max_retries + 1):
            try:
                async with self.request_semaphore:
                    # Add rate limiting
                    if attempt > 0 or self.rate_limit_delay > 0:
                        await asyncio.sleep(
                            self.rate_limit_delay + (attempt * self.retry_delay)
                        )
                    
                    # Call the function with timeout
                    result = await asyncio.wait_for(
                        call_function(model_config, *args, **kwargs),
                        timeout=model_config.timeout
                    )
                    return result
                    
            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Timeout for {model_config.model} (attempt {attempt + 1})"
                )
            except Exception as e:
                self.logger.warning(
                    f"Error with {model_config.model} (attempt {attempt + 1}): {e}"
                )
                
                # Don't retry on certain errors
                if "rate limit" in str(e).lower() or "quota" in str(e).lower():
                    if attempt < model_config.max_retries:
                        await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    else:
                        break
        
        return None
    
    def _record_usage(self, model_config: ModelConfig, success: bool):
        """Record model usage statistics"""
        model_key = f"{model_config.provider.value}:{model_config.model}"
        
        if model_key not in self.model_stats:
            self.model_stats[model_key] = {
                'total_calls': 0,
                'successful_calls': 0,
                'failed_calls': 0,
                'success_rate': 0.0
            }
        
        stats = self.model_stats[model_key]
        stats['total_calls'] += 1
        
        if success:
            stats['successful_calls'] += 1
        else:
            stats['failed_calls'] += 1
            
        stats['success_rate'] = stats['successful_calls'] / stats['total_calls']
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model usage statistics"""
        return self.model_stats.copy()
    
    def get_best_model(self, model_type: str) -> Optional[ModelConfig]:
        """Get the best performing model for a given type"""
        if model_type == 'generation':
            models = self.generation_models
        elif model_type == 'answering':
            models = self.answering_models
        elif model_type == 'grading':
            models = self.grading_models
        else:
            return None
        
        if not models:
            return None
            
        # Find model with best success rate
        best_model = None
        best_rate = -1
        
        for model in models:
            model_key = f"{model.provider.value}:{model.model}"
            stats = self.model_stats.get(model_key, {})
            success_rate = stats.get('success_rate', 0)
            
            if success_rate > best_rate or (success_rate == best_rate and best_model is None):
                best_model = model
                best_rate = success_rate
        
        return best_model or models[0]  # Fallback to first model


class ConcurrentBatchProcessor:
    """Handles concurrent processing of multiple batches/rounds"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Concurrency settings
        self.rounds_concurrency = config.get('rounds_concurrency', 3)
        self.round_internal_concurrency = config.get('round_internal_concurrency', 5)
        self.questions_per_round = config.get('questions_per_round', 10)
        
        # Create semaphores
        self.rounds_semaphore = asyncio.Semaphore(self.rounds_concurrency)
        self.internal_semaphore = asyncio.Semaphore(self.round_internal_concurrency)
        
    async def process_rounds_concurrently(
        self, 
        total_rounds: int,
        round_processor_func,
        progress_callback=None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple rounds concurrently
        
        Args:
            total_rounds: Number of rounds to process
            round_processor_func: Async function to process a single round
            progress_callback: Optional callback for progress updates
        """
        
        # Create tasks for all rounds
        tasks = []
        for round_num in range(1, total_rounds + 1):
            task = asyncio.create_task(
                self._process_single_round(
                    round_num, round_processor_func, progress_callback
                )
            )
            tasks.append(task)
        
        # Wait for all rounds to complete
        results = []
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                results.append(result)
                
                if progress_callback:
                    await progress_callback(len(results), total_rounds)
                    
            except Exception as e:
                self.logger.error(f"Round processing failed: {e}")
                results.append({'error': str(e)})
        
        return results
    
    async def _process_single_round(
        self, 
        round_num: int, 
        processor_func, 
        progress_callback=None
    ) -> Dict[str, Any]:
        """Process a single round with concurrency control"""
        
        async with self.rounds_semaphore:
            try:
                self.logger.info(f"Starting round {round_num}")
                
                result = await processor_func(
                    round_num, 
                    self.questions_per_round,
                    self.internal_semaphore
                )
                
                self.logger.info(f"Completed round {round_num}")
                return {
                    'round_num': round_num,
                    'success': True,
                    'result': result
                }
                
            except Exception as e:
                self.logger.error(f"Round {round_num} failed: {e}")
                return {
                    'round_num': round_num,
                    'success': False,
                    'error': str(e)
                }
    
    async def process_questions_in_round(
        self, 
        questions: List[Any],
        question_processor_func
    ) -> List[Dict[str, Any]]:
        """Process questions within a round concurrently"""
        
        tasks = []
        for i, question in enumerate(questions):
            task = asyncio.create_task(
                self._process_single_question(
                    i, question, question_processor_func
                )
            )
            tasks.append(task)
        
        # Wait for all questions to be processed
        results = []
        for completed_task in asyncio.as_completed(tasks):
            try:
                result = await completed_task
                results.append(result)
            except Exception as e:
                self.logger.error(f"Question processing failed: {e}")
                results.append({'error': str(e)})
        
        return results
    
    async def _process_single_question(
        self, 
        question_index: int, 
        question: Any, 
        processor_func
    ) -> Dict[str, Any]:
        """Process a single question with concurrency control"""
        
        async with self.internal_semaphore:
            try:
                result = await processor_func(question)
                return {
                    'index': question_index,
                    'success': True,
                    'result': result
                }
            except Exception as e:
                self.logger.error(f"Question {question_index} failed: {e}")
                return {
                    'index': question_index,
                    'success': False,
                    'error': str(e)
                }