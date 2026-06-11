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
                      energy_type: str = "generation",
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      time_range: Optional[int] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """执行能耗查询"""
        logger.info("Executing energy query",
                    device_id=device_id,
                    energy_type=energy_type)

        try:
            if not start_time or not end_time:
                end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                start_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

            # 构建能耗查询请求
            metric_map = {
                "generation": "发电量",  # 发电量
                "consumption": "用电量",  # 用电量
                "efficiency": "能效"  # 能效
            }

            metric = metric_map.get(energy_type, "energy_generation")

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
                    energy_type=energy_type,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=time_range,
                    request_headers=request_headers
                )

            return {
                "success": True,
                "data": data,
                "energy_type": energy_type,
                "message": f"成功查询到{energy_type}能耗数据"
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

    async def execute(self, data: List[Dict],
                      chart_type: str = "line",
                      title: str = "",
                      x_field: str = "timestamp",
                      y_fields: List[str] = None) -> Dict:
        """生成图表配置"""
        logger.info("Generating chart",
                    chart_type=chart_type,
                    title=title)

        chart_config = {
            "type": chart_type,
            "title": title,
            "data": data,
            "xAxis": {
                "field": x_field,
                "label": "时间"
            },
            "yAxis": {
                "fields": y_fields or [],
                "label": "数值"
            },
            "series": []
        }

        if y_fields:
            for field in y_fields:
                chart_config["series"].append({
                    "field": field,
                    "label": field,
                    "type": "line"
                })

        return {
            "success": True,
            "chart_config": chart_config,
            "message": "图表配置生成成功"
        }
