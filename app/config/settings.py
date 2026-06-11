import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "EMS AI Agent"
    DEBUG: bool = False

    DATABASE_URL: str = "postgresql://postgres:025@SMts@113.44.214.114:5432/agent_db"
    REDIS_URL: str = "redis://:025@SMts@113.44.214.114:6379/4"

    DATA_API_BASE: str = "http://113.44.214.114:9010/api"
    DATA_API_KEY: str = ""

    VLLM_API_BASE: str = "http://dev.xmsmts.com:48000"
    VLLM_MODEL: str = "Qwen32b"

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"


settings = Settings()
