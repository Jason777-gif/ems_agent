import logging
import sys
from datetime import datetime
from uuid import uuid4

import structlog
from structlog.stdlib import ProcessorFormatter

from app.config.settings import settings


def setup_logging():
    """配置结构化日志"""

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = ProcessorFormatter(
        processor=structlog.dev.ConsoleRenderer(),
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.addHandler(file_handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))


def get_logger(name: str = __name__) -> structlog.BoundLogger:
    """获取带上下文的logger"""
    return structlog.get_logger(name).bind(request_id=str(uuid4()))
