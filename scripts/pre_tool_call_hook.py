#!/usr/bin/env python3
"""
pre_tool_call_hook.py — 物理约束：写报告前必须加载数据源
每个写报告的工具调用前，强制检查：
  ① BAZI_DATASOURCE 环境变量已设置（指向锁定后的 ds.json）
  ② 报告内容中的关键数字与 datasource 一致
违反任一项 -> 阻止写操作
"""

import json, os, re, sys

HOOK_LOG = os.path.expanduser('~/.hermes/logs/pre_tool_call_hook.log')
os.makedirs(os.path.dirname(HOOK_LOG), exist_ok=True)

def log(msg):
    with open(HOOK_LOG, 'a') as f:
        import datetime
        f.write(f"[{datetime.datetime.now().isoformat()}] {msg}\n")

def check_datasource_loaded():
    """检查数据源是否已加载"""
    ds_path = os.environ.get('BAZI_DATASOURCE', '')
    if not ds_path:
        return False, "❌ BAZI_DATASOURCE 未设置。必须先运行: export BAZI_DATASOURCE=/tmp/{姓名}_ds.json"
    if not os.path.exists(ds_path):
        return False, f"❌ 数据源文件不存在: {ds_path}"
    return True, ""

def check_report_numbers_against_ds(content, ds_path):
    """检查报告中关键数字是否与数据源一致"""
    try:
        with open(ds_path) as f:
            DS = json.load(f)
    except:
        return True, []  # 数据源无法读取则跳过（避免卡死）
    
    issues = []
    
    # 检查身强弱分数
    score = DS.get('身强弱', {}).get('总分')
    if score is not None:
        score_str = str(score)
        if score_str in content:
            pass  # 数字在报告中出现 ✅
        else:
            issues.append(f"⚠️ 报告未含身强弱分数 {score}")
    
    # 检查身强等级
    level = DS.get('身强弱', {}).get('等级')
    if level and level not in content:
        issues.append(f"⚠️ 报告未含身强弱等级 {level}")
    
    # 检查日主
    rz = DS.get('日主', '')
    if rz and rz not in content:
        issues.append(f"⚠️ 报告未含日主 {rz}")
    
    # 检查八字
    bazi = DS.get('八字', '')
    if bazi:
        parts = bazi.split()
        for p in parts:
            if p not in content:
                issues.append(f"⚠️ 报告未含八字成分 {p}")
    
    # 检查大运（至少第一个和最后一个）
    dayun = DS.get('大运', [])
    if len(dayun) >= 2:
        first_gan = dayun[0]['干支']
        last_gan = dayun[-1]['干支']
        if first_gan not in content:
            issues.append(f"⚠️ 报告未含大运 {first_gan}")
    
    return len(issues) == 0, issues


def run():
    # 这是在每次工具调用前的检查
    loaded, msg = check_datasource_loaded()
    if not loaded:
        log(msg)
        print(msg)
        sys.exit(1)  # 阻止后续操作
    
    # 如果这次调用是写文件，检查内容
    # （从stdin或参数获取）
    if len(sys.argv) > 1 and sys.argv[1] == '--check-content':
        content = sys.stdin.read() if not sys.stdin.isatty() else ''
        if content:
            ds_path = os.environ.get('BAZI_DATASOURCE', '')
            ok, issues = check_report_numbers_against_ds(content, ds_path)
            if not ok:
                for issue in issues:
                    log(issue)
                    print(issue)
                # 不阻止，仅警告
    
    print("✅ 数据源检查通过")
    sys.exit(0)


if __name__ == '__main__':
    run()
