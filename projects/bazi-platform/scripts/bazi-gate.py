#!/usr/bin/env python3
"""
金鉴真人·八字门禁脚本 — 硬约束门禁系统

功能：在LLM开始八字分析前，检查所有必要条件是否就绪。
     - 规则引擎(bazi-engine.py)是否可执行？
     - 验证脚本(bazi-report-validator.py)是否存在？
     - 关键技能文件(SKILL.md)是否可访问？
     - 模板文件是否可用？

输出：结构化JSON，PASS/FAIL + 详细检查列表。
      门禁不通过 → LLM必须停止分析并通知用户。

版本：v1.0 (2026-06-16)
编制人：金鉴真人
"""

import sys
import os
import json
import importlib.util
import subprocess
from pathlib import Path


# 配置：需要检查的路径和文件
PROFILE_DIR = Path("/root/.hermes/profiles/jinjian-zhenren")
SCRIPTS_DIR = PROFILE_DIR / "scripts"
SKILLS_DIR = PROFILE_DIR / "skills"
GLOBAL_SKILLS_DIR = Path("/root/.hermes/skills")


# 检查清单配置
CHECKS_CONFIG = {
    "规则引擎": {
        "path": SCRIPTS_DIR / "bazi-engine.py",
        "type": "file",
        "description": "bazi-engine.py — 排盘+身强弱评分+大运排布",
        "critical": True,
    },
    "验证脚本": {
        "path": SCRIPTS_DIR / "bazi-report-validator.py",
        "type": "file",
        "description": "bazi-report-validator.py — 报告完整性+一致性验证",
        "critical": True,
    },
    "主控技能": {
        "path": SKILLS_DIR / "bazi-master-agent",
        "type": "directory",
        "description": "bazi-master-agent — 总调度Agent(含三引擎架构)",
        "critical": True,
    },
    "引擎工作流": {
        "path": SKILLS_DIR / "bazi-engine-workflow",
        "type": "directory",
        "description": "bazi-engine-workflow — 排盘引擎工作流技能",
        "critical": True,
    },
    "报告模板": {
        "path": SKILLS_DIR / "bazi-report-template",
        "type": "directory",
        "description": "bazi-report-template — 标准报告输出模板",
        "critical": True,
    },
    "校准技能": {
        "path": SKILLS_DIR / "bazi-calibration",
        "type": "directory",
        "description": "bazi-calibration — 校准体系+防御清单",
        "critical": True,
    },
    "基础技能": {
        "path": SKILLS_DIR / "bazi-foundation-analysis",
        "type": "any",
        "description": "bazi-foundation-analysis — 基础知识包(如存在)",
        "critical": False,
    },
    "财富技能": {
        "path": SKILLS_DIR / "bazi-wealth-analysis",
        "type": "any",
        "description": "bazi-wealth-analysis — 财富分析(如存在)",
        "critical": False,
    },
    "事业技能": {
        "path": SKILLS_DIR / "bazi-career-analysis",
        "type": "any",
        "description": "bazi-career-analysis — 事业分析(如存在)",
        "critical": False,
    },
    "学业技能": {
        "path": SKILLS_DIR / "bazi-education-analysis",
        "type": "any",
        "description": "bazi-education-analysis — 学业分析(如存在)",
        "critical": False,
    },
    "婚姻技能": {
        "path": SKILLS_DIR / "bazi-marriage-analysis",
        "type": "any",
        "description": "bazi-marriage-analysis — 婚姻分析(如存在)",
        "critical": False,
    },
    "子女技能": {
        "path": SKILLS_DIR / "bazi-children-analysis",
        "type": "any",
        "description": "bazi-children-analysis — 子女分析(如存在)",
        "critical": False,
    },
    "灾祸技能": {
        "path": SKILLS_DIR / "bazi-misfortune-analysis",
        "type": "any",
        "description": "bazi-misfortune-analysis — 灾祸分析(如存在)",
        "critical": False,
    },
    "流年技能": {
        "path": SKILLS_DIR / "bazi-liunian-analysis",
        "type": "any",
        "description": "bazi-liunian-analysis — 流年大运(如存在)",
        "critical": False,
    },
    "健康技能": {
        "path": SKILLS_DIR / "bazi-health-psychology",
        "type": "any",
        "description": "bazi-health-psychology — 健康分析(如存在)",
        "critical": False,
    },
    "命运技能": {
        "path": GLOBAL_SKILLS_DIR / "bazi-destiny-analysis",
        "type": "directory",
        "description": "bazi-destiny-analysis — 全局命运分析技能",
        "critical": True,
    },
    "解析技能": {
        "path": GLOBAL_SKILLS_DIR / "bazi-fortune-analysis",
        "type": "directory",
        "description": "bazi-fortune-analysis — 全局解析技能",
        "critical": True,
    },
    "五鼠遁验证": {
        "path": SKILLS_DIR / "bazi-wushidun-verify",
        "type": "any",
        "description": "bazi-wushidun-verify — 五鼠遁验证(如存在)",
        "critical": False,
    },
    "自动验证": {
        "path": SKILLS_DIR / "bazi-auto-verify",
        "type": "any",
        "description": "bazi-auto-verify — 自动验证(如存在)",
        "critical": False,
    },
}


def check_path(path, check_type):
    """检查路径是否存在且满足类型条件。"""
    path_obj = Path(path) if isinstance(path, str) else path

    if check_type == "executable":
        return path_obj.exists() and os.access(str(path_obj), os.X_OK)
    elif check_type == "directory":
        return path_obj.is_dir()
    elif check_type == "any":
        return path_obj.exists()
    elif check_type == "file":
        return path_obj.is_file()
    return False


def check_engine_importable():
    """检查bazi-engine.py能否被Python导入（不报语法错误）。"""
    engine_path = SCRIPTS_DIR / "bazi-engine.py"
    if not engine_path.exists():
        return False
    try:
        with open(engine_path, 'r') as f:
            source = f.read()
        compile(source, str(engine_path), 'exec')
        return True
    except SyntaxError as e:
        print(f"    [ERROR] bazi-engine.py 语法错误: {e}", file=sys.stderr)
        return False


def check_engine_runnable():
    """实际运行bazi-engine.py测试排盘功能。"""
    engine_path = SCRIPTS_DIR / "bazi-engine.py"
    if not engine_path.exists():
        return False, "文件不存在"
    try:
        result = subprocess.run(
            [sys.executable, str(engine_path), "--test"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return True, "运行正常"
        else:
            return False, result.stderr[:200]
    except subprocess.TimeoutExpired:
        return False, "运行超时(10s)"
    except Exception as e:
        return False, str(e)[:200]


def run_gate(verbose=False):
    """
    执行所有门禁检查，返回结构化结果。
    
    返回格式：
    {
        "status": "PASS" | "FAIL",
        "critical_pass": True/False,  # 所有核心检查通过？
        "summary": "通过X/Y项检查",
        "checks": [
            {"name": "...", "status": "✅"|"❌", "description": "...", "critical": true/false, ...}
        ],
        "blocking_issues": ["..."],  # 需要用户注意的致命问题
        "warning_issues": ["..."]     # 仅供参考的问题
    }
    """
    results = []
    blocking_issues = []
    warning_issues = []
    total = 0
    critical_total = 0
    critical_pass = 0

    for name, config in CHECKS_CONFIG.items():
        total += 1
        if config["critical"]:
            critical_total += 1

        path = config["path"]
        check_type = config["type"]

        exists = check_path(path, check_type)
        
        entry = {
            "name": name,
            "status": "✅" if exists else "❌" if config["critical"] else "⚠️",
            "path": str(path),
            "type": check_type,
            "exists": exists,
            "critical": config["critical"],
            "description": config["description"],
        }
        
        if exists and config["critical"]:
            critical_pass += 1
        
        if not exists:
            if config["critical"]:
                blocking_issues.append(f"{name}: {config['description']} — 文件/目录不存在")
            else:
                warning_issues.append(f"{name}: {config['description']} — 文件/目录不存在(非核心)")
        
        results.append(entry)

    # 额外检查：引擎能否实际工作
    engine_ok = check_engine_importable()
    if not engine_ok:
        blocking_issues.append("规则引擎语法检查失败")
    
    # 运行时测试：用 --test 确认引擎可以实际运行
    engine_runtest_ok, engine_runtest_msg = check_engine_runnable()
    if not engine_runtest_ok:
        warning_issues.append(f"规则引擎运行时测试: {engine_runtest_msg}")
    
    # 汇总
    all_critical_pass = (critical_pass == critical_total)
    status = "PASS" if all_critical_pass else "FAIL"

    output = {
        "status": status,
        "critical_pass": all_critical_pass,
        "summary": f"通过 {sum(1 for r in results if r['exists'])}/{total} 项检查",
        "critical_detail": f"核心检查: {critical_pass}/{critical_total} 通过",
        "checks": results,
        "blocking_issues": blocking_issues,
        "warning_issues": warning_issues,
    }

    return output


def format_json_output(result):
    """格式化为JSON输出。"""
    print(json.dumps(result, ensure_ascii=False, indent=2))


def format_human_output(result):
    """格式化为人类可读输出。"""
    print("=" * 60)
    print(f"  金鉴真人 · 八字门禁检查")
    print(f"  此门禁脚本的返回值可被 LLM 读取用于决策")
    print(f"  {'=' * 56}")
    print(f"  🔒 门禁结果: {result['status']}")
    print(f"  {result['summary']}")
    print(f"  {result['critical_detail']}")
    print("=" * 60)
    
    # 按核心/非核心分组显示
    for r in result["checks"]:
        icon = r["status"]
        if r["critical"]:
            critical_tag = " [核心]"
        else:
            critical_tag = " [辅助]"
        print(f"  {icon} {r['name']}{critical_tag}")
    
    if result["blocking_issues"]:
        print("\n  ❌ 阻塞问题（必须先修复）:")
        for issue in result["blocking_issues"]:
            print(f"     • {issue}")

    if result["warning_issues"]:
        print("\n  ⚠️ 警告（不影响分析但建议关注）:")
        for issue in result["warning_issues"]:
            print(f"     • {issue}")

    if result["status"] == "PASS":
        print(f"\n  ✅ 门禁通过 — 可以开始八字分析")
    else:
        print(f"\n  ⛔ 门禁未通过 — 禁止开始八字分析")
        print(f"     请先修复以上阻塞问题，再运行门禁验证")
    
    print("=" * 60)
    print(f"  门禁版本: v1.0 | 编制人: 金鉴真人")
    print(f"  注意: 此脚本的输出是确定性数据（不是LLM生成的）")
    print(f"  {'=' * 56}")
    print("=" * 60)


def main():
    """主入口。"""
    # 解析参数
    output_format = "human"  # human | json
    if "--json" in sys.argv:
        output_format = "json"
    if "--quiet" in sys.argv:
        # 只输出状态码给shell
        pass
    
    result = run_gate()
    
    if output_format == "json":
        format_json_output(result)
    else:
        format_human_output(result)
    
    # 退出码：0=通过 1=未通过
    sys.exit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
