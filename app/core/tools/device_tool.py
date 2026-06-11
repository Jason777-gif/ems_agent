from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from app.services.data_api import data_api_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DeviceQueryTool:
    """设备数据查询工具"""

    name = "device_query"
    description = "查询设备的实时数据或历史数据"

    async def execute(self, device_id: str, metric: str,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      time_range: Optional[int] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """执行设备数据查询"""
        logger.info("Executing device query",
                    device_id=device_id,
                    metric=metric)

        try:
            if not start_time or not end_time:
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_time = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

            data = await data_api_service.get_device_data(
                device_id=device_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range,
                request_headers=request_headers
            )

            return {
                "success": True,
                "data": data,
                "message": f"成功查询到{device_id}的{metric}数据"
            }
        except Exception as e:
            logger.error("Device query failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "查询失败"
            }


class EnergyQueryTool:
    """能耗查询工具"""

    name = "energy_query"
    description = "查询发电量、用电量等能耗统计信息"

    async def execute(self, device_id: Optional[str] = None,
                      metric: str = "generation",
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      time_range: Optional[int] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """执行能耗查询"""
        logger.info("Executing energy query",
                    device_id=device_id,
                    metric=metric)

        try:
            if not start_time or not end_time:
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

            if device_id:
                # 查询特定设备的能耗
                data = await data_api_service.get_device_data(
                    device_id=device_id,
                    metric=metric,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=time_range,
                    request_headers=request_headers
                )
            else:
                # 查询总体能耗统计
                data = await data_api_service.get_energy_statistics(
                    metric=metric,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=time_range,
                    request_headers=request_headers
                )

            return {
                "success": True,
                "data": data,
                "metric": metric,
                "message": f"成功查询到{metric}能耗数据"
            }
        except Exception as e:
            logger.error("Energy query failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "查询失败"
            }


class AlarmQueryTool:
    """告警查询工具"""

    name = "alarm_query"
    description = "查询设备告警信息"

    async def execute(self, device_id: Optional[str] = None,
                      level: Optional[str] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """执行告警查询"""
        logger.info("Executing alarm query",
                    device_id=device_id,
                    level=level)

        try:
            alarms = await data_api_service.get_alarms(
                device_id=device_id,
                level=level,
                request_headers=request_headers
            )

            return {
                "success": True,
                "data": alarms,
                "count": len(alarms),
                "message": f"查询到{len(alarms)}条告警"
            }
        except Exception as e:
            logger.error("Alarm query failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "查询失败"
            }


class ChartGeneratorTool:
    """图表生成工具"""

    name = "chart_generator"
    description = "根据数据生成图表配置（前端渲染用）"

    async def execute(self, device_id: str, metric: str,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      time_range: Optional[int] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """生成图表配置"""
        logger.info("Generating chart config",
                    device_id=device_id,
                    metric=metric,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=time_range,
                    request_headers=request_headers
                    )
        try:
            chart_config = await data_api_service.get_device_chart(
                device_id=device_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range,
                request_headers=request_headers
            )
            return {
                "success": True,
                "chart_config": chart_config,
                "message": "图表配置生成成功"
            }

        except Exception as e:
            logger.error("chart_generator failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "图表配置生成失败"
            }


