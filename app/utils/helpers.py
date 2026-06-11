from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta


def parse_time_range(time_str: str) -> tuple[str, str]:
    """解析时间范围字符串"""
    now = datetime.now()

    if not time_str or time_str in ["今天", "今日"]:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif "昨天" in time_str:
        yesterday = now - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
        end = yesterday.replace(hour=23, minute=59, second=59)
    elif "本周" in time_str:
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now
    elif "本月" in time_str:
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end = now

    elif "最近一小时" in time_str or "近一小时" in time_str:
        start = now - timedelta(hours=1)
        end = now
    elif "最近一天" in time_str or "近一天" in time_str:
        start = now - timedelta(days=1)
        end = now
    else:
        # 默认最近一小时
        start = now - timedelta(hours=1)
        end = now

    return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")


def format_number(value: float, decimals: int = 2) -> str:
    """格式化数字"""
    if value >= 1e9:
        return f"{value / 1e9:.{decimals}f}G"
    elif value >= 1e6:
        return f"{value / 1e6:.{decimals}f}M"
    elif value >= 1e3:
        return f"{value / 1e3:.{decimals}f}K"
    else:
        return f"{value:.{decimals}f}"


def extract_device_id(text: str) -> Optional[str]:
    """从文本中提取设备ID"""
    import re

    patterns = [
        r'(\d+)号逆变器',
        r'逆变器\s*(\d+)',
        r'设备\s*(\d+)',
        r'#(\d+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return f"inverter_{match.group(1)}"

    return None


def extract_metric_type(text: str) -> Optional[str]:
    """从文本中提取指标类型"""
    metric_map = {
        '功率': 'power',
        '电压': 'voltage',
        '电流': 'current',
        '温度': 'temperature',
        '发电量': 'energy_generation',
        '效率': 'efficiency'
    }

    for keyword, metric in metric_map.items():
        if keyword in text:
            return metric

    return None
