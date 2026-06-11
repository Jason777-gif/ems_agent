from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    def __init__(self):
        self.engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_size=10,
            max_overflow=20
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        logger.info("Database service initialized")

    @asynccontextmanager
    async def get_session(self):
        """获取数据库会话"""
        async with self.SessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error("Database transaction error", error=str(e))
                raise
            finally:
                await session.close()

    async def execute_query(self, query: str, params: Dict[str, Any] = None) -> List[Dict]:
        """执行原生SQL查询"""
        async with self.engine.connect() as conn:
            result = await conn.execute(query, params or {})
            columns = result.keys()
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]


db_service = DatabaseService()
