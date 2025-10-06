"""
Prompt管理模块 - 从docs目录加载所有prompt
"""

import os
import logging


logger = logging.getLogger(__name__)


class PromptManager:
    """Prompt管理器，负责加载和提供所有prompt模板"""
    
    def __init__(self, prompts_dir: str = "./docs/prompts"):
        """
        初始化Prompt管理器
        
        Args:
            prompts_dir: prompts文件所在目录
        """
        self.prompts_dir = prompts_dir
        self._prompts = {}
        self._load_prompts()
    
    def _load_prompts(self):
        """加载所有prompt文件"""
        prompt_files = {
            "generation": "生成题Prompt.md",
            "grading": "判题Prompt.md",
            "answering": "解题Prompt.md"
        }
        
        for key, filename in prompt_files.items():
            filepath = os.path.join(self.prompts_dir, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # 移除markdown代码块标记
                    content = content.replace('```markdown', '').replace('```', '').strip()
                    self._prompts[key] = content
                logger.info(f"成功加载prompt: {filename}")
            except Exception as e:
                logger.error(f"加载prompt文件失败 {filename}: {e}")
                self._prompts[key] = ""
    
    def get_generation_prompt(self) -> str:
        """获取题目生成prompt模板"""
        return self._prompts.get("generation", "")
    
    def get_grading_prompt(self) -> str:
        """获取判题prompt模板"""
        return self._prompts.get("grading", "")
    
    def get_answering_prompt(self) -> str:
        """获取解题prompt模板"""
        return self._prompts.get("answering", "")
