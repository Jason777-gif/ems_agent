from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.services.data_api import data_api_service
from app.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])


class DeviceListRequest(BaseModel):
    status: Optional[str] = None
    type: Optional[str] = None


class DeviceMetricRequest(BaseModel):
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class AlarmRequest(BaseModel):
    device_id: Optional[str] = None
    level: Optional[str] = None


@router.post("/list")
async def get_device_list(
        request: Request,
        device_request: DeviceListRequest
):
    """获取设备列表（POST）"""
    try:
        filters = {}
        if device_request.status:
            filters["status"] = device_request.status
        if device_request.type:
            filters["type"] = device_request.type

        # 从请求头获取 Authorization
        request_headers = dict(request.headers)

        devices = await data_api_service.get_device_list(filters, request_headers)
        return {
            "success": True,
            "data": devices,
            "count": len(devices)
        }
    except Exception as e:
        logger.error("Get device list failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{device_id}/metrics/{metric}")
async def get_device_metric(
        request: Request,
        device_id: str,
        metric: str,
        metric_request: DeviceMetricRequest
):
    """获取设备指标数据（POST）"""
    try:
        from datetime import datetime, timedelta

        start_time = metric_request.start_time
        end_time = metric_request.end_time

        if not start_time or not end_time:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            start_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

        # 从请求头获取 Authorization
        request_headers = dict(request.headers)

        data = await data_api_service.get_device_data(
            device_id=device_id,
            metric=metric,
            start_time=start_time,
            end_time=end_time,
            request_headers=request_headers
        )

        return {
            "success": True,
            "data": data,
            "device_id": device_id,
            "metric": metric
        }
    except Exception as e:
        logger.error("Get device metric failed",
                     device_id=device_id,
                     metric=metric,
                     error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/alarms")
async def get_alarms(
        request: Request,
        alarm_request: AlarmRequest
):
    """获取告警信息（POST）"""
    try:
        # 从请求头获取 Authorization
        request_headers = dict(request.headers)

        alarms = await data_api_service.get_alarms(
            device_id=alarm_request.device_id,
            level=alarm_request.level,
            request_headers=request_headers
        )

        return {
            "success": True,
            "data": alarms,
            "count": len(alarms)
        }
    except Exception as e:
        logger.error("Get alarms failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
