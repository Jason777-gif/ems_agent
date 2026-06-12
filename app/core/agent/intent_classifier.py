from enum import Enum
from typing import Dict, List, Optional
import json
import re
from datetime import datetime, timedelta
from app.core.llm.client import llm_client
from app.utils.logger import get_logger
from app.utils.helpers import extract_device_id, extract_metric_type, parse_time_range

logger = get_logger(__name__)


class IntentType(Enum):
    QUERY_DEVICE_DATA = "query_device_data"  # 查询设备数据
    QUERY_ALARM = "query_alarm"  # 查询告警
    QUERY_ENERGY = "query_energy"  # 查询能耗
    GENERATE_CHART = "generate_chart"  # 生成图表
    GENERATE_REPORT = "generate_report"
    UNKNOWN = "unknown"  # 未知意图


class IntentClassifier:
    """意图识别器"""

    SYSTEM_PROMPT = """你是一个新能源平台的意图识别助手。请分析用户的问题，判断其意图类型。
已知当前时间为""" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """。
可用的意图类型：
1. query_device_data - 查询设备数据（电压、电流、功率、温度等）
2. query_alarm - 查询告警信息
3. query_energy - 查询发电量、能耗等统计信息
4. generate_chart - 生成图表（趋势图、柱状图等）
5. generate_report - 生成报告
6. unknown - 无法识别的意图


请以JSON格式返回结果，包含：
- intent: 意图类型
- confidence: 置信度(0-1)
- entities: 提取的实体（device: 设备标识, metric: 指标类型, start_time: 开始时间（时间格式是:%Y-%m-%d %H:%M:%S）, end_time: 结束时间（时间格式是:%Y-%m-%d %H:%M:%S）, time: 日期类型,0:日 1:月 2：年 3:自定义, chart_type: 图表类型,0:折线 1:柱状）

示例：
用户："查询逆变器1今天的电压"
返回：{"intent": "query_device_data", "confidence": 0.95, "entities": {"device": "逆变器1", "metric": "电压", "start_time": "2026-06-10 00:00:00", "end_time": "2026-06-10 23:59:59", time:0}}

用户："查询逆变器1这个月的电压"
返回：{"intent": "query_device_data", "confidence": 0.95, "entities": {"device": "逆变器1", "metric": "电压", "start_time": "2026-06-01 00:00:00", "end_time": "2026-06-30 23:59:59", time:1}}

用户："查询逆变器1今年的电压"
返回：{"intent": "query_device_data", "confidence": 0.95, "entities": {"device": "逆变器1", "metric": "电压", "start_time": "2026-01-01 00:00:00", "end_time": "2026-12-31 23:59:59", time:2}}

用户："查询逆变器1从6月3日到6月6日的电压"
返回：{"intent": "query_device_data", "confidence": 0.95, "entities": {"device": "逆变器1", "metric": "电压", "start_time": "2026-06-03 00:00:00", "end_time": "2026-06-06 23:59:59", time:3}}

用户："查看逆变器5昨天的电压"
返回：{"intent": "query_device_data", "confidence": 0.92, "entities": {"device": "逆变器5", "metric": "电压", "start_time": "2026-06-09 00:00:00", "end_time": "2026-06-09 23:59:59", time:0}}
"""

    async def classify(self, user_input: str,
                       conversation_history: List[Dict] = None) -> Dict:
        """分类用户意图"""
        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        if conversation_history:
            messages.extend(conversation_history[:])

        messages.append({"role": "user", "content": user_input})

        try:
            response = await llm_client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=500
            )

            result = json.loads(response)

            # 后处理：补充提取的实体
            entities = result.get("entities", {})

            # 如果 LLM 没有提取到 device，尝试从文本中提取
            if not entities.get("device"):
                device_id = extract_device_id(user_input)
                if device_id:
                    entities["device"] = device_id

            # 如果 LLM 没有提取到 metric，尝试从文本中提取
            if not entities.get("metric"):
                metric = extract_metric_type(user_input)
                if metric:
                    entities["metric"] = metric

            # 如果 LLM 没有提取到 time，默认为"今天"
            if not entities.get("time"):
                entities["time"] = 0
            if not entities.get("start_time"):
                entities["start_time"] = (datetime.now() - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
                entities["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # 如果 LLM 没有提取到 chart_type，尝试从文本中提取
            if not entities.get("chart_type"):
                entities["chart_type"] = 0
            logger.info("Intent classified",
                        intent=result.get("intent"),
                        confidence=result.get("confidence"),
                        entities=entities)

            result["entities"] = entities
            return result

        except Exception as e:
            logger.error("Intent classification failed", error=str(e))
            return {
                "intent": IntentType.UNKNOWN.value,
                "confidence": 0.0,
                "entities": {}
            }


intent_classifier = IntentClassifier()
