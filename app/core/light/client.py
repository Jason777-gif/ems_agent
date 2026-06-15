from typing import Any, Dict, List, Optional
import aiohttp
import json
from LightAgent import LightAgent
from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class LightClient:
    """vLLM模型客户端"""

    def __init__(self):
        self.api_base = settings.VLLM_API_BASE
        self.model = settings.VLLM_MODEL
        logger.info(f"VLLM Client initialized with model: {self.model}")

    async def chat_completion(self, content : str,
                              history: Optional[List[Dict]] = None,
                              role: str = "user",
                              instructions: str  = "You are a helpful assistant.",
                              tools: Optional[List[Any]] = None) -> str:
        """调用vLLM完成对话"""

        url = f"{self.api_base}/v1"

        # 初始化 Agent
        agent = LightAgent(instructions= instructions,role = role,model=self.model, api_key="none", base_url=url, tools=tools)

        # 运行 Agent
        run = agent.run(query=content, history=history)
        print( run)
        return run

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


light_client = LightClient()
