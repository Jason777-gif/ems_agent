from typing import Any, Dict, List, Optional
import aiohttp

from app.config.settings import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DataAPIService:
    def __init__(self):
        self.base_url = settings.DATA_API_BASE  # 从配置或环境变量获取
        logger.info("Data API service initialized")

    async def _get_headers(self, request_headers: Optional[Dict] = None) -> Dict:
        """从请求头中获取 Authorization"""
        headers = {
            "Content-Type": "application/json"
        }

        # 如果传入了请求头，提取 Authorization
        if request_headers:
            auth = request_headers.get("Authorization") or request_headers.get("authorization")
            if auth:
                headers["Authorization"] = auth

        return headers

    async def get_device_data(self, device_id: str, metric: str,
                              start_time: str, end_time: str,
                              time_range: int,
                              request_headers: Optional[Dict] = None) -> Dict:
        """获取设备数据（POST）"""
        url = f"{self.base_url}/energyGeneration/count"
        if metric == "发电量":
            url = f"{self.base_url}/energyGeneration/count"
        elif metric == "功率" or metric == "实时功率":
            url = f"{self.base_url}/energyGeneration/countPower"
        elif metric == "电流":
            url = f"{self.base_url}/energyGeneration/countCurrent"
        elif metric == "电压":
            url = f"{self.base_url}/energyGeneration/countVoltage"
        elif metric == "温度":
            url = f"{self.base_url}/energyGeneration/countTemperature"
        elif metric == "功率因数":
            url = f"{self.base_url}/energyGeneration/countPowerFactor"
        elif metric == "状态" or metric == "运行状态":
            url = f"{self.base_url}/energyGeneration/countStatus"
        elif metric == "效率":
            url = f"{self.base_url}/energyGeneration/countEfficiency"

        payload = {
            "iedName": device_id,
            "startDate": start_time,
            "endDate": end_time,
            "timeRange": time_range
        }

        headers = await self._get_headers(request_headers)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error("API request failed",
                                 status=response.status,
                                 url=url)
                    raise Exception(f"API Error: {response.status}")

    async def get_device_chart(self, device_id: str, metric: str,
                              start_time: str, end_time: str,
                              time_range: int,
                               chart_type: int,
                              request_headers: Optional[Dict] = None) -> Dict:
        """获取设备数据（POST）"""
        url = f"{self.base_url}/energyGeneration/chart"
        if metric == "发电量":
            url = f"{self.base_url}/energyGeneration/chart"


        payload = {
            "iedName": device_id,
            "startDate": start_time,
            "endDate": end_time,
            "timeRange": time_range
        }

        headers = await self._get_headers(request_headers)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    # 如果result的data返回的是列表，最外层添加 chartType；如果是字典，直接添加
                    if isinstance(result, dict):
                        result["chartType"] = chart_type
                    return result
                else:
                    logger.error("API request failed",
                                 status=response.status,
                                 url=url)
                    raise Exception(f"API Error: {response.status}")

    async def get_energy_statistics(self, metric: str,
                                    start_time: str, end_time: str,
                                    time_range: int,
                                    request_headers: Optional[Dict] = None) -> Dict:
        """获取能耗统计（POST）"""
        url = f"{self.base_url}/energy/statistics"

        payload = {
            "metric": metric,
            "start_time": start_time,
            "end_time": end_time,
            "timeRange": time_range
        }
        headers = await self._get_headers(request_headers)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error("Energy statistics request failed",
                                 status=response.status,
                                 url=url)
                    raise Exception(f"API Error: {response.status}")

    async def get_device_list(self, filters: Dict = None,
                              request_headers: Optional[Dict] = None) -> List[Dict]:
        """获取设备列表（POST）"""
        url = f"{self.base_url}/devices"

        headers = await self._get_headers(request_headers)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=filters or {}) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")

    async def get_alarms(self, device_id: Optional[str] = None,
                         level: Optional[str] = None,
                         request_headers: Optional[Dict] = None) -> List[Dict]:
        """获取告警信息（POST）"""
        url = f"{self.base_url}/alarms"

        payload = {}
        if device_id:
            payload["device_id"] = device_id
        if level:
            payload["level"] = level

        headers = await self._get_headers(request_headers)

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")


data_api_service = DataAPIService()
