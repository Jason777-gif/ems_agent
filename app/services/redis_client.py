import json
from typing import Any, Dict, Optional

import redis.asyncio as aioredis

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RedisService:
    def __init__(self):
        self.redis = None
        self._initialized = False

        # 延迟初始化，在第一次使用时才连接
        logger.info("Redis service created (lazy initialization)")

    async def _ensure_initialized(self):
        """确保 Redis 已初始化"""
        if not self._initialized:
            try:
                redis_url = settings.REDIS_URL
                logger.info("Initializing Redis connection", url=redis_url)

                self.redis = aioredis.from_url(
                    redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

                # 测试连接
                await self.redis.ping()
                self._initialized = True
                logger.info("Redis connection established successfully")

            except Exception as e:
                logger.error("Failed to initialize Redis",
                             error=str(e),
                             redis_url=redis_url)
                self.redis = None
                self._initialized = True  # 标记为已尝试，避免重复尝试

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """获取会话上下文"""
        await self._ensure_initialized()

        if not self.redis:
            return None

        try:
            data = await self.redis.get(f"session:{session_id}")
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning("Redis get_session failed", error=str(e))
            return None

    async def save_session(self, session_id: str, data: Dict, ttl: int = 3600):
        """保存会话上下文"""
        await self._ensure_initialized()

        if not self.redis:
            return

        try:
            await self.redis.setex(
                f"session:{session_id}",
                ttl,
                json.dumps(data, ensure_ascii=False)
            )
        except Exception as e:
            logger.warning("Redis save_session failed", error=str(e))

    async def delete_session(self, session_id: str):
        """删除会话"""
        await self._ensure_initialized()

        if not self.redis:
            return

        try:
            await self.redis.delete(f"session:{session_id}")
        except Exception as e:
            logger.warning("Redis delete_session failed", error=str(e))

    async def cache_data(self, key: str, data: Any, ttl: int = 300):
        """缓存数据"""
        await self._ensure_initialized()

        if not self.redis:
            return

        try:
            await self.redis.setex(key, ttl, json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.warning("Redis cache_data failed", error=str(e))

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        await self._ensure_initialized()

        if not self.redis:
            return None

        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.warning("Redis get_cached_data failed", error=str(e))
            return None


redis_service = RedisService()
