"""
配置加载模块
"""
import yaml
import os
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> dict:
    """
    加载配置文件
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置字典
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config
