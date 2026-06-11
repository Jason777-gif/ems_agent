from typing import Any, Dict, List, Optional
import aiohttp
import json

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VLLMClient:
    """vLLM模型客户端"""

    def __init__(self):
        self.api_base = settings.VLLM_API_BASE
        self.model = settings.VLLM_MODEL
        logger.info(f"VLLM Client initialized with model: {self.model}")

    async def chat_completion(self, messages: List[Dict],
                              temperature: float = 0.7,
                              max_tokens: int = 2000) -> str:
        """调用vLLM完成对话"""
        url = f"{self.api_base}/v1/chat/completions"

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }

        headers = {
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers, timeout=60) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error("vLLM API call failed",
                                     status=response.status,
                                     error=error_text)
                        raise Exception(f"vLLM API Error: {response.status} - {error_text}")
        except Exception as e:
            logger.error("vLLM request exception", error=str(e))
            raise


llm_client = VLLMClient()
