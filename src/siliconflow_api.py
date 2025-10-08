"""
硅基流动API支持模块 - DeepSeek备选方案
"""

import os
import logging
from typing import Dict, Any
import litellm


logger = logging.getLogger(__name__)


class SiliconFlowAPI:
    """硅基流动API封装"""
    
    def __init__(self):
        """初始化硅基流动API"""
        self.api_key = os.getenv("SILICONFLOW_API_KEY")
        self.base_url = "https://api.siliconflow.cn/v1"
        
        if not self.api_key:
            logger.warning("硅基流动API密钥未配置，DeepSeek备选方案不可用")
            return
            
        # 配置litellm使用硅基流动
        self._configure_litellm()
        
    def _configure_litellm(self):
        """配置litellm使用硅基流动API"""
        try:
            # 设置环境变量供litellm使用
            os.environ["SILICONFLOW_API_KEY"] = self.api_key
            logger.info("硅基流动API配置完成")
        except Exception as e:
            logger.error(f"配置硅基流动API时出错: {e}")
    
    def is_available(self) -> bool:
        """检查硅基流动API是否可用"""
        return bool(self.api_key)
    
    def get_model_name(self) -> str:
        """获取DeepSeek模型名称"""
        return "openai/deepseek-ai/DeepSeek-V3"
    
    def test_connection(self) -> bool:
        """测试API连接"""
        if not self.is_available():
            return False
            
        try:
            # 发送简单测试请求
            response = litellm.completion(
                model=self.get_model_name(),
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5,
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            if response and response.choices:
                logger.info("硅基流动API连接测试成功")
                return True
            else:
                logger.error("硅基流动API连接测试失败：无有效响应")
                return False
                
        except Exception as e:
            logger.error(f"硅基流动API连接测试失败: {e}")
            return False


# 全局实例
siliconflow_api = SiliconFlowAPI()