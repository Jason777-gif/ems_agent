from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    """聊天消息请求"""
    message: str = Field(..., description="用户消息", min_length=1, max_length=2000)
    session_id: Optional[str] = Field(None, description="会话ID")


class DeviceQueryRequest(BaseModel):
    """设备查询请求"""
    device_id: str = Field(..., description="设备ID")
    metric: str = Field(..., description="指标类型")
    start_time: Optional[str] = Field(None, description="开始时间")
    end_time: Optional[str] = Field(None, description="结束时间")


class ChartGenerateRequest(BaseModel):
    """图表生成请求"""
    data: List[Dict] = Field(..., description="图表数据")
    chart_type: str = Field("line", description="图表类型")
    title: str = Field("", description="图表标题")
    x_field: str = Field("timestamp", description="X轴字段")
    y_fields: List[str] = Field([], description="Y轴字段列表")
