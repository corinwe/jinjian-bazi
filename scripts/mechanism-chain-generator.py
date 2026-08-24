#!/usr/bin/env python3
"""
mechanism-chain-generator.py — 机制链注入生成器 v1.0
=====================================================
金鉴真人·机制链注入法（2026-08-24 老板校准）

核心原则：
  "给 Agent 的不是知识库，是【用知识的路径】"
  机制链 = 确定性代码从引擎JSON生成的推理链，直接注入报告头部，
  LLM 不需要自己检索规则，照着机制链展开论述 → 产出自然是"分析"而非"标签"。

用法:
  python3 mechanism-chain-generator.py <engine.json> [--out 输出文件]
  例:
  python3 mechanism-chain-generator.py /tmp/qiqi_engine.json --out /tmp/qiqi_chain.txt

输出格式（报告头部注入标记）:
  <!-- 【机制链注入】 版本1.0 生成时间 -->
  【机制链·身强弱】...
  【机制链·财星】...
  ...
"""
import sys, os, json, datetime, re, hashlib

# ─────────────────────────────────────────────
# 机制链构建（全部确定性逻辑，无LLM参与）
# ─────────────────────────────────────────────

def build_shen_qiang_chain(d):
    """身强弱链: 计分明细 → 判定 → 喜忌方向"""
    sq = d['analysis']['shen_qiang_ruo']
    score = sq['score']
    label = sq['label']
    det = sq.get('details', {})
    parts = []
    if det.get('yue_yin'): parts.append(f"月令印{det['yue_yin']}分")
    if det.get('yue_bi'): parts.append(f"月令比劫{det['yue_bi']}分")
    if det.get('tg_bi'): parts.append(f"天干比劫{det['tg_bi']}分")
    if det.get('rz'): parts.append(f"日支印比{det['rz']}分")
    if det.get('nsz'): parts.append(f"年时支印比{det['nsz']}分")
    detail = " + ".join(parts) if parts else "无生扶"
    direction = "喜印比(生扶)" if label == "身弱" else ("喜克泄耗" if label == "身强" else "喜忌随大运灵活变化")
    return f"身强弱: 计分[{detail}] → {label}({score}分) → {direction}"

def build_cai_chain(d):
    """财星链: 财星分布 → 身财匹配 → 等级 → 变现窗口"""
    cx = d['analysis']['cai_xing']
    total = cx.get('total', 0)
    level = cx.get('wealth_level', '未知')
    cdd = cx.get('cai_xing_details', {})
    sq = d['analysis']['shen_qiang_ruo']
    label = sq['label']
    # 财星分布描述
    pos_desc = []
    if cdd.get('yue', 0) > 0: pos_desc.append(f"月令{cdd['yue']}分")
    if cdd.get('ri', 0) > 0: pos_desc.append(f"日支{cdd['ri']}分")
    if cdd.get('sz', 0) > 0: pos_desc.append(f"时支{cdd['sz']}分")
    if cdd.get('nian', 0) > 0: pos_desc.append(f"年支{cdd['nian']}分")
    if cdd.get('sg', 0) > 0: pos_desc.append(f"时干{cdd['sg']}分")
    dist = "、".join(pos_desc) if pos_desc else "财星微弱"
    # 身财匹配
    if label == "身弱" and total >= 50:
        match = "身弱财旺 → 富屋贫人，需印比运变现"
    elif label == "身弱":
        match = "身弱财平 → 求财辛苦，借平台之力"
    elif label in ("身强",) and total >= 50:
        match = "身强财旺 → 天生发财格"
    elif label in ("身强",):
        match = "身强财弱 → 财源不足，需食伤生财"
    else:
        match = "中和 → 身财平衡，喜忌随大运"
    # 变现窗口
    s1 = d['result'].get('sec_1_overview', {})
    best = s1.get('best_da_yun', '')
    return f"财星: 分布[{dist}] → 总分{total}分{level} → {match} → 最佳变现运: {best}"

def build_ge_ju_chain(d):
    """格局链: 月令取格 → 顺逆用 → 成败标记"""
    gj = d['analysis']['ge_ju']
    main = gj.get('main', '未知')
    detail = gj.get('detail', '')
    # 提取关键标记
    flags = []
    if '合绊' in detail: flags.append("用神合绊⚠️")
    if '不成格' in detail: flags.append("成格存疑⚠️")
    if '顺用' in detail: flags.append("顺用")
    if '逆用' in detail: flags.append("逆用")
    flag_str = " ".join(flags) if flags else ""
    return f"格局: 月令取格[{main}] → {flag_str} → {detail[:80]}"

def build_hun_yin_chain(d):
    """婚姻链: 配偶星 → 夫妻宫 → 质量 → 窗口"""
    m = d['result'].get('sec_12_marriage', {})
    po = m.get('pei_ou_xing', {})
    rz = m.get('ri_zhi_analysis', {})
    q = m.get('quality', '未知')
    w = m.get('best_window_age', '')
    star = po.get('primary', '无')
    rz_master = rz.get('master', '未知')
    rz_note = rz.get('quality_note', '')
    return f"婚姻: 配偶星[{star}] → 夫妻宫十神[{rz_master}({rz_note})] → 质量[{q}] → 最佳窗口[{w}岁]"

def build_xue_ye_chain(d):
    """学业链: 印星 → 文昌 → 学历"""
    e = d['result'].get('sec_11_education', {})
    level = e.get('display', '未知')
    ypc = e.get('year_pillar_check', {})
    wc = e.get('wen_chang_ming_li', {})
    yin = "有印" if ypc.get('has_yin') else "无印"
    wc_s = f"文昌{wc.get('zhi', '')}" if wc.get('has') else "无文昌"
    return f"学业: {yin}+{wc_s} → 学历[{level}]"

def build_zi_nv_chain(d):
    """子女链: 子女星 → 数量 → 窗口"""
    c = d['result'].get('sec_13_children', {})
    cnt = c.get('child_count_estimate', '未知')
    ach = c.get('child_achievement', {})
    direction = ach.get('子女方向', '')
    wins = c.get('windows', [])[:3]
    win_str = "、".join([w.split(',')[0].strip("{}'年份': ") for w in wins]) if wins else "暂无窗口"
    return f"子女: 数量[{cnt}] → 方向[{direction}] → 窗口[{win_str}]"

def build_shi_ye_chain(d):
    """事业链: 格局定方向 → 等级"""
    c = d['result'].get('sec_10_career', {})
    direction = c.get('career_direction', '未知')
    level = c.get('career_level', '未知')
    grade = c.get('career_grade', '')
    return f"事业: 方向[{direction}] → 类型[{level}] → {grade}"

def build_jian_kang_chain(d):
    """健康链: 七杀病灶 + 偏印淤堵 + 五行过三"""
    h = d['result'].get('sec_14_health', {})
    risks = []
    qs = h.get('qi_sha_risks', {}).get('detail', '')
    if qs and '七杀' in qs:
        mm = re.search(r"对应器官[：:]\s*'([^']+)'", qs)
        if mm: risks.append(f"七杀病灶: {mm.group(1)}")
    py = h.get('pian_yin_risks', {}).get('detail', '')
    if py:
        mm = re.search(r"淤堵部位[：:]\s*'([^']+)'", py)
        if mm: risks.append(f"偏印淤堵: {mm.group(1)}")
    wx = d['analysis'].get('energy', {}).get('wu_xing_energy', {})
    over3 = [f"{k}{v}%" for k, v in wx.items() if v and v >= 50]
    if over3: risks.append(f"五行偏旺: {'、'.join(over3)}")
    return f"健康: {' | '.join(risks) if risks else '无明显病灶'}"

def build_best_worst_da_yun(d):
    """大运链: 最佳/最差大运"""
    s1 = d['result'].get('sec_1_overview', {})
    best = s1.get('best_da_yun', '')
    best_l = s1.get('best_da_yun_label', '')
    worst = s1.get('worst_da_yun', '')
    worst_l = s1.get('worst_da_yun_label', '')
    qy = s1.get('qi_yun_age', '')
    return f"大运: 起运{qy}岁 → 最佳[{best}{best_l}] / 最差[{worst}{worst_l}]"

def build_all_chains(d):
    """构建全部机制链"""
    chains = [
        build_shen_qiang_chain(d),
        build_cai_chain(d),
        build_ge_ju_chain(d),
        build_hun_yin_chain(d),
        build_xue_ye_chain(d),
        build_zi_nv_chain(d),
        build_shi_ye_chain(d),
        build_jian_kang_chain(d),
        build_best_worst_da_yun(d),
    ]
    # 产物溯源签名（2026-08-24新增·强制5法之产物溯源）
    # PIPELINE-SIG = sha256(八字+身强弱+格局+喜用+财星+最佳大运) 确定性计算
    try:
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
        pip_sig = hashlib.sha256(sig_src.encode('utf-8')).hexdigest()
        sig_line = f"# PIPELINE-SIG: {pip_sig}  # 溯源签名: sha256(八字+身强弱+格局+喜用+财星+最佳大运)"
    except Exception as e:
        sig_line = f"# PIPELINE-SIG: ERROR-{str(e)[:40]}"
    # 头部标记
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    header = f"<!-- 【机制链注入】 v1.0 {now} 确定性引擎生成，LLM须照链展开论述，禁止跳过 -->\n"
    body = "\n".join([f"【机制链】{c}" for c in chains])
    return header + sig_line + "\n" + body + "\n"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 mechanism-chain-generator.py <engine.json> [--out 输出]")
        sys.exit(1)
    path = sys.argv[1]
    out_path = None
    if '--out' in sys.argv:
        idx = sys.argv.index('--out')
        if idx + 1 < len(sys.argv):
            out_path = sys.argv[idx + 1]
    with open(path, encoding='utf-8') as f:
        d = json.load(f)
    chains = build_all_chains(d)
    print(chains)
    if out_path:
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(chains)
        print(f"\n✅ 机制链已写入: {out_path}")
    else:
        # 打印可复制的块
        print("\n--- 复制以下到报告头部 ---")
        print(chains)

if __name__ == '__main__':
    main()
