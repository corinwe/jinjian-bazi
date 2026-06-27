"""规则引擎调用封装（独立进程subprocess）"""

import json
import os
import subprocess

from api.config import ENGINE_PIPELINE, ENGINE_TIMEOUT


def call_engine(
    name: str,
    gender: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    lunar_month=None,
    lunar_day=None,
) -> dict:
    """
    调用规则引擎进行完整分析
    返回引擎输出的JSON字典
    """
    if not os.path.exists(ENGINE_PIPELINE):
        raise FileNotFoundError(f"引擎入口不存在: {ENGINE_PIPELINE}")

    cmd = [
        "python3",
        ENGINE_PIPELINE,
        "--name",
        name,
        "--gender",
        gender,
        "--year",
        str(year),
        "--month",
        str(month),
        "--day",
        str(day),
        "--hour",
        str(hour),
        "--minute",
        str(minute),
        "--json",
    ]

    if lunar_month is not None:
        cmd.extend(["--lunar-month", str(lunar_month)])
    if lunar_day is not None:
        cmd.extend(["--lunar-day", str(lunar_day)])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=ENGINE_TIMEOUT)

        if result.returncode != 0:
            error_msg = result.stderr[:500] if result.stderr else "未知错误"
            return {"success": False, "error": error_msg, "stderr": result.stderr}

        data = json.loads(result.stdout)
        data["success"] = True
        return data

    except subprocess.TimeoutExpired:
        return {"success": False, "error": "引擎超时（超过30秒）"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"引擎输出非JSON: {e}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
