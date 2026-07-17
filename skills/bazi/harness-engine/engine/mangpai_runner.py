#!/usr/bin/env python3
"""
mangpai_runner.py — 盲派报告生成器
使用盲派规则(rules_mangpai/) + 盲派模板(templates_mangpai/)
体用分析替代身强弱，做功分析替代喜用神
"""
import json, os, sys, yaml

HARNESS_DIR = '/root/.hermes/profiles/jinjian-zhenren/skills/bazi/harness-engine'


def load_rule(path):
    with open(path) as f:
        return yaml.safe_load(f)


def calc_ti_yong(ds):
    """计算体用比"""
    ti = int(ds['身强弱']['总分'])
    yong = max(100 - ti, 1)
    bi = ti / yong
    return ti, yong, bi


def render_template(tpl_path, vars_dict):
    with open(tpl_path) as f:
        tpl = f.read()
    for k, v in vars_dict.items():
        tpl = tpl.replace('{' + k + '}', v if v else '[待生成]')
    return tpl


def generate(ds_path, out_path, label):
    ds = json.load(open(ds_path))
    ti, yong, bi = calc_ti_yong(ds)
    body_use = f'体{ti}分，用{yong}分，比{bi:.1f}:1'

    # 财星位置
    cai_pos = []
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk, []):
            if c['十神'] in ['正财','偏财']:
                cai_pos.append(f'{zk}:{c["天干"]}({c["十神"]})')
    cai_table = '\n'.join(cai_pos) if cai_pos else '无'

    # 官杀位置
    guan_pos = []
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk, []):
            if c['十神'] in ['正官','七杀']:
                guan_pos.append(f'{zk}:{c["天干"]}({c["十神"]})')

    # 月干十神
    month_shi = ds['十神'].get('月', '?')
    day_zhi_shi = ds['藏干十神'].get('日支', [{}])[0].get('十神', '?')

    # 加载盲派规则
    report_sections = []

    # 财富
    rule = load_rule(os.path.join(HARNESS_DIR, 'rules_mangpai', 'cai_fu.yaml'))
    r = rule.get('rule', {})
    items = [a.get('text', '') for a in r.get('analysis_rules', [])]
    wx_lu = '体外财(年时柱)' if '年' in ''.join(cai_pos) or '时' in ''.join(cai_pos) else '体内财(月日柱)'
    vars_dict = {
        'CAI_BIAO': cai_table,
        'LU_XIAN': f'财星位置：{wx_lu}。' + (items[0] if items else ''),
        'TI_YONG': f'体用比：{body_use}。' + (items[1] if len(items) > 1 else ''),
    }
    tpl = render_template(os.path.join(HARNESS_DIR, 'templates_mangpai', 'cai_fu.md'), vars_dict)
    report_sections.append(tpl)

    # 事业
    rule = load_rule(os.path.join(HARNESS_DIR, 'rules_mangpai', 'shi_ye.yaml'))
    r = rule.get('rule', {})
    items = [a.get('text', '') for a in r.get('analysis_rules', [])]
    guan_info = f'官杀位置：{guan_pos}' if guan_pos else '官杀不显'
    vars_dict = {
        'HANG_YE': f'月干{month_shi}，日支{day_zhi_shi}。' + (items[0] if items else ''),
        'LU_XIAN': guan_info + '。' + (items[1] if len(items) > 1 else ''),
        'TI_YONG_SHIYE': f'体用比：{body_use}。' + (items[2] if len(items) > 2 else ''),
    }
    tpl = render_template(os.path.join(HARNESS_DIR, 'templates_mangpai', 'shi_ye.md'), vars_dict)
    report_sections.append(tpl)

    # 学业
    rule = load_rule(os.path.join(HARNESS_DIR, 'rules_mangpai', 'xue_ye.yaml'))
    r = rule.get('rule', {})
    items = [a.get('text', '') for a in r.get('analysis_rules', [])]
    wen = str(ds.get('神煞', {}).get('文昌贵人', '未找到'))
    vars_dict = {
        'WENCHANG': f'文昌贵人：{wen}。' + (items[0] if items else ''),
        'XUEYE': items[1] if len(items) > 1 else '学业趋势分析...',
    }
    tpl = render_template(os.path.join(HARNESS_DIR, 'templates_mangpai', 'xue_ye.md'), vars_dict)
    report_sections.append(tpl)

    full = '\n\n'.join(report_sections)
    with open(out_path, 'w') as f:
        f.write(full)
    return full


if __name__ == '__main__':
    for ds_path, label, subdir in [
        ('/tmp/weiqiling_ds.json', '魏启令', '01-家主-魏启令'),
        ('/tmp/ziyuan_ds.json', '子源', '03-少爷-子源'),
    ]:
        out = f'/tmp/{label}_盲派_财富事业学业.md'
        report = generate(ds_path, out, label)
        line_count = len(report.splitlines())
        char_count = len(report)
        print(f'{label}: {line_count}行 {char_count}字')

        # 保存到知识库
        kb = f'/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{subdir}/{label}_盲派_财富事业学业.md'
        with open(kb, 'w') as f:
            f.write(report)
        print(f'  保存: {kb}')
