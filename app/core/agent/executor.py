from datetime import datetime
from typing import Any, Dict, List, Optional

from django.contrib.messages import SUCCESS

# from jsonschema.benchmarks.contains import end

from app.core.agent.intent_classifier import intent_classifier, IntentType
from app.core.tools.device_tool import DeviceQueryTool, AlarmQueryTool, ChartGeneratorTool,EnergyQueryTool
from app.core.llm.client import llm_client
from app.core.tools.report_tool import ReportGeneratorTool
from app.services.redis_client import redis_service
from app.utils.logger import get_logger
from app.utils.helpers import parse_time_range, extract_device_id, extract_metric_type

logger = get_logger(__name__)


class AgentExecutor:
    """Agent执行器"""

    def __init__(self):
        self.tools = {
            "device_query": DeviceQueryTool(),
            "energy_query": EnergyQueryTool(),
            "alarm_query": AlarmQueryTool(),
            "chart_generator": ChartGeneratorTool(),
            "report_generator": ReportGeneratorTool()
        }
        logger.info("Agent executor initialized")

    async def execute(self, user_input: str,
                      session_id: str,
                      conversation_history: List[Dict] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """执行Agent流程"""
        logger.info("Agent execution started",
                    session_id=session_id,
                    user_input=user_input)

        try:
            step1_start = datetime.now()
            intent_result = await intent_classifier.classify(
                user_input,
                conversation_history
            )
            step1_end = datetime.now()

            intent = intent_result.get("intent")
            entities = intent_result.get("entities", {})

            step2_start = datetime.now()
            result = await self._execute_intent(intent, entities, request_headers)
            step2_end = datetime.now()

            step3_start = datetime.now()
            final_response = await self._generate_response(
                user_input,
                result,
                conversation_history
            )
            step3_end = datetime.now()

            response = {
                "success": True,
                "session_id": session_id,
                "intent": intent,
                "response": final_response,
                "data": result.get("data"),
                "chart": result.get("chart_config"),
                "metadata": {
                    "processing_times": {
                        "intent_classification": (step1_end - step1_start).total_seconds(),
                        "tool_execution": (step2_end - step2_start).total_seconds(),
                        "response_generation": (step3_end - step3_start).total_seconds()
                    }
                }
            }

            await redis_service.save_session(
                session_id,
                {
                    "history": (conversation_history or []) + [
                        {"role": "user", "content": user_input},
                        {"role": "assistant", "content": final_response}
                    ]
                }
            )

            logger.info("Agent execution completed",
                        session_id=session_id,
                        intent=intent)

            return response

        except Exception as e:
            logger.error("Agent execution failed",
                         session_id=session_id,
                         error=str(e))
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，处理您的请求时出现错误"
            }

    async def _execute_intent(self, intent: str, entities: Dict,
                              request_headers: Optional[Dict] = None) -> Dict:
        """根据意图执行对应操作"""
        if intent == IntentType.QUERY_DEVICE_DATA.value:
            device_id = entities.get("device", "")
            metric = entities.get("metric", "")
            time_range = entities.get("time", 0)

            # 解析时间范围
            start_time = entities.get("start_time", "")
            end_time = entities.get("end_time", "")

            logger.info("Parsed time range",
                        time_range=time_range,
                        start_time=start_time,
                        end_time=end_time)

            tool = self.tools["device_query"]
            return await tool.execute(
                device_id=device_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range,
                request_headers=request_headers
            )

        elif intent == IntentType.QUERY_ENERGY.value:
            metric = entities.get("metric", "")
            device_id = entities.get("device")
            time_range = entities.get("time", 0)

            start_time = entities.get("start_time", "")
            end_time = entities.get("end_time", "")

            logger.info("Energy query params",
                        energy_type=metric,
                        device_id=device_id,
                        time_range=time_range,
                        start_time=start_time,
                        end_time=end_time)

            tool = self.tools["energy_query"]
            return await tool.execute(
                device_id=device_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range,
                request_headers=request_headers
            )

        elif intent == IntentType.QUERY_ALARM.value:
            device_id = entities.get("device")
            level = entities.get("level")

            tool = self.tools["alarm_query"]
            return await tool.execute(
                device_id=device_id,
                level=level,
                request_headers=request_headers
            )

        elif intent == IntentType.GENERATE_CHART.value:
            device_id = entities.get("device", "")
            metric = entities.get("metric", "")
            time_range = entities.get("time", 0)
            chart_type  = entities.get("chart_type", 0)
            # 解析时间范围
            start_time = entities.get("start_time", "")
            end_time = entities.get("end_time", "")

            logger.info("chart_generator",
                        time_range=time_range,
                        metric=metric,
                        device_id=device_id,
                        start_time=start_time,
                        end_time=end_time,
                        chart_type = chart_type)

            tool = self.tools["chart_generator"]
            return await tool.execute(
                device_id=device_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range,
                chart_type=chart_type,
                request_headers=request_headers
             )
        elif intent == IntentType.GENERATE_REPORT.value:
            report_type = entities.get("report_type", "")
            device_id = entities.get("device", "")
            metric = entities.get("metric", "")
            start_time = entities.get("start_time", "")
            end_time = entities.get("end_time", "")
            time_range = entities.get("time", 0)

            logger.info("report_generator",
                        report_type=report_type,
                        device_id=device_id,
                        metric=metric,
                        start_time=start_time,
                        end_time=end_time,
                        time_range=time_range)

            tool = self.tools["report_generator"]
            return await tool.execute(
                device_id=device_id,
                metric=metric,
                start_time=start_time,
                end_time=end_time,
                time_range=time_range,
                report_type=report_type,
                request_headers=request_headers
            )

        else:
            return {
                "success": False,
                "message": "无法识别的意图"
            }

    async def _generate_response(self, user_input: str,
                                 tool_result: Dict,
                                 history: List[Dict]) -> str:
        """生成自然语言回复"""
        system_prompt = """你是一个新能源平台的智能助手。根据工具返回的结果，用简洁、专业的语言回答用户问题。

        如果工具有数据返回，请用中文总结关键信息。
        如果有图表配置，提示用户可以在前端查看可视化图表。
        如果有报告数据，请简要介绍报告的主要内容和结论，告知用户报告的详细信息已准备好。
        如果查询失败，友好地告知用户并给出建议。"""

        messages = [{"role": "system", "content": system_prompt}]

        if history:
            messages.extend(history[-3:])

        messages.append({"role": "user", "content": user_input})
        messages.append({
            "role": "user",
            "content": f"工具返回结果：{str(tool_result)}"
        })

        response = await llm_client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        return response


agent_executor = AgentExecutor()
