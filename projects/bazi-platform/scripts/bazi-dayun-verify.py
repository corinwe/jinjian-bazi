#!/usr/bin/env python3
"""
金鉴真人·大运年份物理约束验证脚本 v1.0
2026-06-24新增·老板令

功能：强制检查报告中所有大运年份与引擎JSON是否一致
用法：python3 bazi-dayun-verify.py <报告路径> <引擎JSON路径> [姓名]
输出：通过/不通过 详细差异列表

物理约束：此脚本必须集成到：
  1. git pre-commit hook（自动触发）
  2. bazi-pipeline.sh --verify（手动触发）
  3. delegate_task子agent返回后强制校验
"""

import json
import re
import sys


def load_engine_data(json_path):
    """从引擎JSON加载大运序列（兼容两种schema）

    schema-A（bazi-engine.py / bazi-data-source.py 排盘口径）:
        data['大运'] = {'序列': [{'干支','起始年龄','终止年龄','起始年份','终止年份'}]}
    schema-B（pipeline_v5 全量分析口径·2026-09-11 补齐）:
        data['analysis']['da_yun']['list'] = [{'gan_zhi','start_age','end_age','start_year','end_year'}]
    ⚠️ 旧版只认 schema-A → pipeline_v5 报告（现主路径）恒返回「无法加载」，大运年份门禁**静默失效**。
       本函数补齐 schema-B 归一化，让门禁对 v5 报告真正生效。
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    qiyun, qiyun_age = '未知', '未知'
    engine_dayun = []

    dy_a = data.get('大运') or {}
    sequences = dy_a.get('序列') if isinstance(dy_a, dict) else None
    if sequences:
        qiyun = dy_a.get('起运', '未知')
        qiyun_age = dy_a.get('起运年龄', '未知')
        for dy in sequences:
            engine_dayun.append({
                'ganzhi': dy.get('干支'),
                'start_year': dy.get('起始年份'),
                'end_year': dy.get('终止年份'),
                'start_age': dy.get('起始年龄'),
                'end_age': dy.get('终止年龄'),
            })
    else:
        dy_b = ((data.get('analysis') or {}).get('da_yun') or {})
        seq_b = dy_b.get('list') if isinstance(dy_b, dict) else None
        if not seq_b:
            seq_b = ((data.get('result') or {}).get('sec_17_da_yun_detail') or {}).get('list')
        if seq_b:
            for dy in seq_b:
                engine_dayun.append({
                    'ganzhi': dy.get('gan_zhi') or dy.get('干支'),
                    'start_year': dy.get('start_year') or dy.get('起始年份'),
                    'end_year': dy.get('end_year') or dy.get('终止年份'),
                    'start_age': dy.get('start_age') or dy.get('起始年龄'),
                    'end_age': dy.get('end_age') or dy.get('终止年龄'),
                })
            sq = ((data.get('analysis') or {}).get('shen_qiang_ruo') or {})
            qiyun_age = dy_b.get('qiyun_age') or dy_b.get('起运年龄') or sq.get('qy_age', '未知')

    if not engine_dayun:
        print("❌ 引擎JSON中无大运序列数据")
        return None

    return {
        'sequences': engine_dayun,
        'qiyun': qiyun,
        'qiyun_age': qiyun_age
    }


_GZ = r'[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]'
_YEAR_PAIR = r'(\d{4})\s*[~\-–—]\s*(\d{4})'
# 清洗：去 markdown 标记 / emoji / 全角标点分隔符（保留干支+数字+括号+破折号）
_KEEP = re.compile(r'[^\u4e00-\u9fffA-Za-z0-9()（）~\-–—|/\.，,。：: 　]')


def _clean(line: str) -> str:
    s = line.replace('**', '').replace('`', '')
    s = _KEEP.sub(' ', s)
    return re.sub(r'\s+', ' ', s)


def extract_report_dayun(report_path):
    """从报告中提取所有「大运干支 + 起止年份」引用（2026-09-11 重写）

    旧版两个模式都匹配不到生成器实际格式 → 恒 0 处 → 门禁空转。实际格式（generate_deep_report 产物）：
      A) `### 17.1 🏆 乙巳大运（2015~2024）·8~17岁`      标题式
      B) `> - DS['大运'] = 起运7.7岁，首运 乙巳（2015–2024）共11步`   数据源对齐块
      C) `| | **🏆 乙巳运（2015~2024·8~17岁）** |`        §16 分段表头（年份与年龄用 · 分隔）
      D) `| 乙巳 | 2015~2024 | ...`                      标准表格
      E) `乙巳运 2015-2024`                              行内裸格式（保留兼容）
    策略：**先定位年份对，再取同行距离最近的干支**（干支后紧跟「运/大运」加权优先），
    从而同时兼容「干支在前」和「年份在前」两种写法。
    """
    with open(report_path, 'r', encoding='utf-8') as f:
        lines = f.read().split('\n')

    found = []
    for ln, raw in enumerate(lines, 1):
        s = _clean(raw)
        pairs = []
        for m in re.finditer(_YEAR_PAIR, s):
            a, b = int(m.group(1)), int(m.group(2))
            if 5 <= b - a <= 15:          # 大运固定 10 年（含边界年）
                pairs.append((a, b, m.start()))
        if not pairs:
            continue
        cands = []
        for m in re.finditer(_GZ, s):
            nxt = s[m.end():m.end() + 3]
            weight = 2 if ('运' in nxt) else 1      # 「乙巳运」优先于裸「乙巳」
            cands.append((m.group(0), m.start(), weight))
        if not cands:
            continue
        for a, b, ypos in pairs:
            gz = min(cands, key=lambda c: (abs(c[1] - ypos) - c[2] * 3))[0]
            found.append({'ganzhi': gz, 'start': a, 'end': b, 'line': ln,
                          'text': raw.strip()[:100]})

    seen, unique = set(), []
    for f in found:
        key = f"{f['ganzhi']}_{f['start']}_{f['end']}"
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def verify_dayun(engine_data, report_refs, name=""):
    """验证报告中大运年份与引擎一致性 → (errors, ok_count, unknown)

    unknown = 报告中带年份对的干支，引擎大运序列里没有 → 警惕凭空捏造的大运（按警告处理，不阻断）
    """
    engine_seqs = engine_data['sequences']

    errors = []
    ok_count = 0
    unknown = []

    engine_year_pairs = {}
    for seq in engine_seqs:
        engine_year_pairs[seq['ganzhi']] = (seq['start_year'], seq['end_year'])

    for ref in report_refs:
        gz = ref['ganzhi']
        if gz in engine_year_pairs:
            expected_start, expected_end = engine_year_pairs[gz]
            if ref['start'] != expected_start or ref['end'] != expected_end:
                errors.append({
                    'ganzhi': gz,
                    'report': (ref['start'], ref['end']),
                    'engine': (expected_start, expected_end),
                    'diff': ref['start'] - expected_start,
                    'line': ref.get('line'),
                })
            else:
                ok_count += 1
        else:
            unknown.append(ref)

    return errors, ok_count, unknown


def main():
    if len(sys.argv) < 3:
        print("用法: python3 bazi-dayun-verify.py <报告.md> <引擎.json> [姓名]")
        sys.exit(1)
    
    report_path = sys.argv[1]
    json_path = sys.argv[2]
    name = sys.argv[3] if len(sys.argv) > 3 else ""
    
    print(f"{'='*60}")
    print(f"  金鉴真人·大运年份物理约束验证")
    if name:
        print(f"  命主: {name}")
    print(f"{'='*60}")
    
    # 加载引擎数据
    engine = load_engine_data(json_path)
    if not engine:
        print("\n❌ 验证失败：无法加载引擎数据")
        sys.exit(1)
    
    print(f"\n引擎起运: {engine['qiyun']} (年龄{engine['qiyun_age']})")
    print(f"引擎大运序列:")
    for seq in engine['sequences']:
        print(f"  {seq['ganzhi']}: {seq['start_year']}~{seq['end_year']} ({seq['start_age']}~{seq['end_age']}岁)")
    
    # 从报告提取大运引用
    report_refs = extract_report_dayun(report_path)
    print(f"\n报告中共发现 {len(report_refs)} 处大运年份引用（行号/原文）：")
    for r in report_refs[:15]:
        print(f"  L{r['line']:<5} {r['ganzhi']} {r['start']}~{r['end']}  ← {r['text']}")
    if len(report_refs) > 15:
        print(f"  ...（其余 {len(report_refs)-15} 处略）")

    # 🚨 门禁空转保护：一处理不提取到 = 没有验证任何东西 → 必须报错，不得静默放行
    MIN_REFS = 1
    if len(report_refs) < MIN_REFS:
        print(f"\n❌ 门禁空转（未从报告提取到任何大运年份引用，提取阈值={MIN_REFS}）")
        print("   说明：提取规则未覆盖本报告的写法，或报告完全不含大运年份 → 门禁无法验证")
        print("   请检查 extract_report_dayun() 的格式规则，不要当作通过")
        sys.exit(3)

    # 验证
    errors, ok_count, unknown = verify_dayun(engine, report_refs, name)

    if unknown:
        print(f"\n⚠️ 警告：{len(unknown)} 处带年份的干支不在引擎大运序列中（疑似捏造或口径不符）")
        for u in unknown[:10]:
            print(f"  ⚠️ L{u['line']} {u['ganzhi']} {u['start']}~{u['end']}")

    # 输出结果
    if not errors:
        print(f"\n✅ 全部 {ok_count} 处大运年份与引擎一致！"
              f"（覆盖率 {ok_count}/{len(engine['sequences'])} 步大运，报告引用 {len(report_refs)} 处）")
        sys.exit(0)

    print(f"\n❌ 发现 {len(errors)} 处大运年份错误！")
    print(f"\n{'='*60}")
    print(f"  错误明细")
    print(f"{'='*60}")
    for err in errors:
        print(f"  ❌ L{err.get('line')} {err['ganzhi']}: 报告={err['report'][0]}~{err['report'][1]}, "
              f"引擎={err['engine'][0]}~{err['engine'][1]}, "
              f"偏差={err['diff']:+.0f}年")
    print(f"\n✅ 正确 {ok_count} 处 | ❌ 错误 {len(errors)} 处")
    # 🚨 失败摘要必须是最后一行且含「不一致」——pre-commit hook 依赖该关键字拦截
    print(f"❌ 大运年份校验不一致：{len(errors)} 处与引擎数据不一致，禁止推库！")
    sys.exit(1)


if __name__ == '__main__':
    main()
