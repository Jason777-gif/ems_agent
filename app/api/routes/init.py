"""API routes"""
from app.api.routes.chat import router as chat_router
from app.api.routes.device import router as device_router

__all__ = ["chat_router", "device_router"]
