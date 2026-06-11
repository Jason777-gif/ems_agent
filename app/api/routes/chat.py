from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.core.agent.executor import agent_executor
from app.services.redis_client import redis_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    success: bool
    session_id: str
    response: str
    data: Optional[Dict] = None
    chart: Optional[Dict] = None
    metadata: Optional[Dict] = None


@router.post("", response_model=ChatResponse)
async def chat(request: Request, chat_request: ChatRequest):
    """AI对话接口"""
    session_id = chat_request.session_id or str(uuid4())

    try:
        session_data = await redis_service.get_session(session_id)
        conversation_history = session_data.get("history", []) if session_data else []

        # 从请求头获取 Authorization
        request_headers = dict(request.headers)

        result = await agent_executor.execute(
            user_input=chat_request.message,
            session_id=session_id,
            conversation_history=conversation_history,
            request_headers=request_headers
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))

        return ChatResponse(**result)

    except Exception as e:
        logger.error("Chat API error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """获取会话历史"""
    session_data = await redis_service.get_session(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "history": session_data.get("history", [])
    }


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """删除会话"""
    await redis_service.delete_session(session_id)
    return {"message": "Session deleted"}
