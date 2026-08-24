#!/usr/bin/env python3
"""
verify-pipeline-sig.py — 产物溯源签名验证器 v1.0
=================================================
强制5法之「产物溯源」：校验报告头部的 PIPELINE-SIG 是否与引擎JSON一致。

用法:
  python3 verify-pipeline-sig.py <报告.md> <引擎JSON>
  退出码: 0=通过 | 1=签名缺失或不匹配

原理:
  机制链生成器从引擎JSON确定性计算 sha256(八字+身强弱+格局+喜用+财星+最佳大运)
  写入报告头部 `# PIPELINE-SIG: <hash>`。
  本脚本用同一算法重新计算，与报告中的hash比对：
    - 一致 → 报告确由该引擎JSON生成（可溯源）
    - 不一致/缺失 → 报告可能绕过流水线手写或数据被篡改
"""
import sys, re, json, hashlib


def compute_sig(d: dict) -> str:
    """与 mechanism-chain-generator.py 完全相同的签名算法"""
    bazi = d.get('paipan', {}).get('bazi', '') or d.get('result', {}).get('sec_1_overview', {}).get('bazi', '')
    sq = d.get('analysis', {}).get('shen_qiang_ruo', {})
    gj = d.get('analysis', {}).get('ge_ju', {})
    xys = d.get('analysis', {}).get('xi_yong_shen', {})
    cx = d.get('analysis', {}).get('cai_xing', {})
    s1 = d.get('result', {}).get('sec_1_overview', {})
    sig_src = json.dumps({
        'bazi': bazi,
        'shen_qiang': f"{sq.get('label','')}{sq.get('score','')}",
        'ge_ju': gj.get('main', ''),
        'xi': xys.get('xi', []),
        'ji': xys.get('ji', []),
        'cai': cx.get('total', 0),
        'best_da_yun': s1.get('best_da_yun', ''),
    }, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(sig_src.encode('utf-8')).hexdigest()


def extract_sig(report: str) -> str:
    """从报告头部提取 PIPELINE-SIG"""
    m = re.search(r'# PIPELINE-SIG:\s*([a-fA-F0-9]{64})', report)
    return m.group(1) if m else ''


def main():
    if len(sys.argv) < 3:
        print("用法: python3 verify-pipeline-sig.py <报告.md> <引擎JSON>")
        sys.exit(1)
    report_path, json_path = sys.argv[1], sys.argv[2]

    try:
        with open(report_path, encoding='utf-8') as f:
            report = f.read()
    except Exception as e:
        print(f"❌ 报告读取失败: {e}")
        sys.exit(1)

    try:
        with open(json_path, encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        print(f"❌ 引擎JSON读取失败: {e}")
        sys.exit(1)

    # 1. 报告必须带签名
    sig_in_report = extract_sig(report)
    if not sig_in_report:
        print("❌ 报告缺少 PIPELINE-SIG 签名（产物溯源失败）")
        print("   运行: python3 mechanism-chain-generator.py <engine.json> --out <chain.txt>")
        print("   然后将机制链（含签名）粘贴到报告头部")
        sys.exit(1)

    # 2. 报告必须带机制链注入标记
    if '【机制链注入】' not in report:
        print("❌ 报告缺少【机制链注入】标记（入口收敛失败）")
        sys.exit(1)

    # 3. 签名必须匹配
    expected = compute_sig(d)
    if sig_in_report.lower() == expected.lower():
        print(f"✅ 产物溯源通过: PIPELINE-SIG 匹配 ({expected[:16]}...)")
        sys.exit(0)
    else:
        print(f"❌ 产物溯源失败: 签名不匹配")
        print(f"   报告中:   {sig_in_report[:32]}...")
        print(f"   引擎计算: {expected[:32]}...")
        print("   原因: 报告可能绕过流水线手写，或引擎JSON已被篡改")
        sys.exit(1)


if __name__ == '__main__':
    main()
