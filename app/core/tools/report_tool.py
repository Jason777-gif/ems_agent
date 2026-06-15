
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.services.data_api import data_api_service
from app.core.llm.client import llm_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReportGeneratorTool:
    """报告生成工具"""

    name = "report_generator"
    description = "根据用户需求生成综合分析报告"

    async def execute(self, report_type: str = "daily",
                      device_id: Optional[str] = None,
                      start_time: Optional[str] = None,
                      end_time: Optional[str] = None,
                      time_range: Optional[int] = None,
                      metric: Optional[str] = None,
                      metrics: Optional[List[str]] = None,
                      request_headers: Optional[Dict] = None) -> Dict:
        """生成报告"""
        logger.info("Generating report",
                    report_type=report_type,
                    device_id=device_id,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=time_range,
                    metrics=metrics)

        if not metrics and metric:
            metrics = [metric]

        try:
            report_data = {}

            if report_type == "daily":
                report_data = await self._generate_daily_report(
                    device_id, start_time, end_time, metrics, request_headers
                )
            elif report_type == "energy":
                report_data = await self._generate_energy_report(
                    device_id, start_time, end_time, time_range, request_headers
                )
            elif report_type == "alarm":
                report_data = await self._generate_alarm_report(
                    device_id, start_time, end_time, request_headers
                )
            elif report_type == "comprehensive":
                report_data = await self._generate_comprehensive_report(
                    device_id, start_time, end_time, time_range, metrics, request_headers
                )
            else:
                report_data = await self._generate_daily_report(
                    device_id, start_time, end_time, metrics, request_headers
                )

            return {
                "success": True,
                "report_data": report_data,
                "message": "报告生成成功"
            }

        except Exception as e:
            logger.error("Report generation failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "message": "报告生成失败"
            }

    async def _generate_daily_report(self, device_id: Optional[str],
                                     start_time: Optional[str],
                                     end_time: Optional[str],
                                     metrics: Optional[List[str]],
                                     request_headers: Optional[Dict]) -> Dict:
        """生成日报"""
        now = datetime.now()

        if not start_time or not end_time:
            start_time = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")

        report_sections = []

        default_metrics = metrics or ["发电量", "功率", "电压", "电流"]

        for metric in default_metrics:
            try:
                data = await data_api_service.get_device_data(
                    device_id=device_id or "",
                    metric=metric,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=0,
                    request_headers=request_headers
                )

                if data:
                    section = await self._summarize_metric(metric, data)
                    report_sections.append(section)
            except Exception as e:
                logger.warning(f"Failed to get {metric} data", error=str(e))

        summary = await self._generate_report_summary(report_sections, "日报")

        return {
            "type": "daily",
            "title": f"设备运行日报 ({start_time[:10]} - {end_time[:10]})",
            "period": {
                "start": start_time,
                "end": end_time
            },
            "device_id": device_id,
            "sections": report_sections,
            "summary": summary,
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    async def _generate_energy_report(self, device_id: Optional[str],
                                      start_time: Optional[str],
                                      end_time: Optional[str],
                                      time_range: Optional[int],
                                      request_headers: Optional[Dict]) -> Dict:
        """生成能耗报告"""
        now = datetime.now()

        if not start_time or not end_time:
            start_time = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")

        energy_data = await data_api_service.get_energy_statistics(
            metric="发电量",
            start_time=start_time,
            end_time=end_time,
            time_range=time_range or 0,
            request_headers=request_headers
        )

        summary = await self._generate_energy_summary(energy_data)

        return {
            "type": "energy",
            "title": f"能耗统计报告 ({start_time[:10]} - {end_time[:10]})",
            "period": {
                "start": start_time,
                "end": end_time
            },
            "device_id": device_id,
            "energy_data": energy_data,
            "summary": summary,
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    async def _generate_alarm_report(self, device_id: Optional[str],
                                     start_time: Optional[str],
                                     end_time: Optional[str],
                                     request_headers: Optional[Dict]) -> Dict:
        """生成告警报告"""
        alarms = await data_api_service.get_alarms(
            device_id=device_id,
            request_headers=request_headers
        )

        alarm_stats = self._analyze_alarms(alarms)
        summary = await self._generate_alarm_summary(alarms, alarm_stats)

        now = datetime.now()

        return {
            "type": "alarm",
            "title": "设备告警报告",
            "period": {
                "start": start_time or "",
                "end": end_time or ""
            },
            "device_id": device_id,
            "total_alarms": len(alarms),
            "alarm_statistics": alarm_stats,
            "recent_alarms": alarms[:10] if alarms else [],
            "summary": summary,
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    async def _generate_comprehensive_report(self, device_id: Optional[str],
                                             start_time: Optional[str],
                                             end_time: Optional[str],
                                             time_range: Optional[int],
                                             metrics: Optional[List[str]],
                                             request_headers: Optional[Dict]) -> Dict:
        """生成综合报告"""
        now = datetime.now()

        if not start_time or not end_time:
            start_time = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            end_time = now.strftime("%Y-%m-%d %H:%M:%S")

        sections = {}

        try:
            energy_data = await data_api_service.get_energy_statistics(
                metric="发电量",
                start_time=start_time,
                end_time=end_time,
                time_range=time_range or 0,
                request_headers=request_headers
            )
            sections["energy"] = energy_data
        except Exception as e:
            logger.warning("Failed to get energy data", error=str(e))

        device_metrics = metrics or ["功率", "电压", "电流"]
        device_data = {}
        for metric in device_metrics:
            try:
                data = await data_api_service.get_device_data(
                    device_id=device_id or "",
                    metric=metric,
                    start_time=start_time,
                    end_time=end_time,
                    time_range=time_range or 0,
                    request_headers=request_headers
                )
                device_data[metric] = data
            except Exception as e:
                logger.warning(f"Failed to get {metric} data", error=str(e))

        sections["device_data"] = device_data

        try:
            alarms = await data_api_service.get_alarms(
                device_id=device_id,
                request_headers=request_headers
            )
            sections["alarms"] = alarms
        except Exception as e:
            logger.warning("Failed to get alarm data", error=str(e))

        summary = await self._generate_comprehensive_summary(sections)

        return {
            "type": "comprehensive",
            "title": f"综合运行报告 ({start_time[:10]} - {end_time[:10]})",
            "period": {
                "start": start_time,
                "end": end_time
            },
            "device_id": device_id,
            "sections": sections,
            "summary": summary,
            "generated_at": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    async def _summarize_metric(self, metric_name: str, data: Dict) -> Dict:
        """总结单个指标数据"""
        prompt = f"""请分析以下{metric_name}数据，用简洁的中文总结关键信息：

数据：{str(data)}

请提供：
1. 平均值/总量
2. 最大值和最小值
3. 整体趋势或异常情况
4. 简短的评价（正常/异常/需要注意）

请用JSON格式返回：
{{
    "metric": "{metric_name}",
    "average": "平均值描述",
    "max_min": "最大最小值描述",
    "trend": "趋势描述",
    "status": "状态评价"
}}"""

        try:
            response = await llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )
            import json
            return json.loads(response)
        except Exception as e:
            logger.error("Failed to summarize metric", error=str(e))
            return {
                "metric": metric_name,
                "average": "数据不可用",
                "max_min": "数据不可用",
                "trend": "无法分析",
                "status": "未知"
            }

    async def _generate_report_summary(self, sections: List[Dict],
                                       report_type: str) -> str:
        """生成报告总体摘要"""
        prompt = f"""基于以下{report_type}的各个指标数据，请生成一段150字以内的专业总结：

{str(sections)}

要求：
1. 概括整体运行情况
2. 指出关键发现或问题
3. 给出简要建议
4. 使用专业但易懂的语言"""

        try:
            response = await llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=200
            )
            return response
        except Exception as e:
            logger.error("Failed to generate summary", error=str(e))
            return "报告生成完成，详细数据请查看各章节。"

    async def _generate_energy_summary(self, energy_data: Dict) -> str:
        """生成能耗总结"""
        prompt = f"""基于以下能耗统计数据，请生成一段100字以内的总结：

{str(energy_data)}

请包含总发电量、效率评价等关键信息。"""

        try:
            response = await llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            return response
        except Exception as e:
            logger.error("Failed to generate energy summary", error=str(e))
            return "能耗数据统计完成。"

    def _analyze_alarms(self, alarms: List[Dict]) -> Dict:
        """分析告警数据"""
        if not alarms:
            return {"total": 0, "by_level": {}, "by_type": {}}

        by_level = {}
        by_type = {}

        for alarm in alarms:
            level = alarm.get("level", "未知")
            alarm_type = alarm.get("type", "未知")

            by_level[level] = by_level.get(level, 0) + 1
            by_type[alarm_type] = by_type.get(alarm_type, 0) + 1

        return {
            "total": len(alarms),
            "by_level": by_level,
            "by_type": by_type
        }

    async def _generate_alarm_summary(self, alarms: List[Dict],
                                      stats: Dict) -> str:
        """生成告警总结"""
        prompt = f"""基于以下告警统计信息，请生成一段100字以内的总结：

总告警数：{stats['total']}
按级别分布：{str(stats['by_level'])}
按类型分布：{str(stats['by_type'])}

请评估系统健康状况并给出建议。"""

        try:
            response = await llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=150
            )
            return response
        except Exception as e:
            logger.error("Failed to generate alarm summary", error=str(e))
            return f"共检测到 {stats['total']} 条告警。"

    async def _generate_comprehensive_summary(self, sections: Dict) -> str:
        """生成综合报告总结"""
        prompt = f"""基于以下综合数据，请生成一段200字以内的专业总结：

能源数据：{str(sections.get('energy', {}))}
设备数据：{str(sections.get('device_data', {}))}
告警数据：{str(sections.get('alarms', []))}

要求：
1. 综合评价系统运行状况
2. 指出关键问题和亮点
3. 给出改进建议"""

        try:
            response = await llm_client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=250
            )
            return response
        except Exception as e:
            logger.error("Failed to generate comprehensive summary", error=str(e))
            return "综合报告生成完成，详细数据请查看各章节。"
