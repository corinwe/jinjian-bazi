#!/usr/bin/env python3
"""step_runner.py — 通用步骤执行器"""
import json, os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflow_v2 import WORKFLOW, load_rule

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def render_template(tpl_path, vars_dict):
    with open(tpl_path) as f:
        tpl = f.read()
    for k, v in vars_dict.items():
        tpl = tpl.replace('{'+k+'}', v if v else '[待生成]')
    return tpl


def apply_generic_rules(ds, rule, sec_name):
    result = {}
    r = rule.get('rule', {})
    items = [ar.get('text', '') for ar in r.get('analysis_rules', [])]
    result['ANALYSIS'] = '\n'.join(items) if items else sec_name + '分析'
    for k in r.get('template_vars', {}):
        if k not in result:
            result[k] = '[' + k + ']'
    return result


def apply_cai_fu_rules(ds, rule):
    result = {}
    cai_items = []
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk, []):
            if c['十神'] in ['正财','偏财']:
                cai_items.append((zk, c['天干'], c['十神']))
    result['cai_table'] = '\n'.join([f"| {p} | {t} | {s} |" for p,t,s in cai_items]) if cai_items else "| 财星不显 |"
    pos_texts = []
    for r_item in rule.get('rule', {}).get('position_rules', []):
        for pos, tg, ss in cai_items:
            if pos == r_item['name'].replace('财',''):
                pos_texts.append('- ' + r_item['name'] + '：' + r_item['text'])
                break
    result['cai_positions'] = '\n'.join(pos_texts) if pos_texts else ''
    shen_level = ds['身强弱']['等级']
    shen_text = ''
    for sr in rule.get('rule', {}).get('shen_rules', []):
        if '身强' in shen_level and '身强' in sr.get('name',''):
            shen_text = sr.get('text',''); break
        elif '从弱' in shen_level and '从弱' in sr.get('name',''):
            shen_text = sr.get('text',''); break
        elif '身弱' in shen_level and '身弱' in sr.get('name',''):
            shen_text = sr.get('text',''); break
    result['shen_analysis'] = shen_text
    has_ss = ds['十神'].get('月','') in ['食神','伤官'] or any(c['十神'] in ['食神','伤官'] for c in ds['藏干十神'].get('日支',[]))
    result['shi_shang'] = rule.get('rule', {}).get('shi_shang_rule', {}).get('text','') if has_ss else ''
    wx_m = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
    cai_yun = []
    for y in ds['大运']:
        dg = y['干支'][0]
        if wx_m.get(dg,'') in '木水':
            cai_yun.append(f"  - {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 财富机遇期")
    result['da_yun'] = '\n'.join(cai_yun) if cai_yun else '  大运不显财干'
    ku_zhi = [ds[zk] for zk in ['年支','月支','日支','时支'] if ds[zk] in '辰戌丑未']
    result['kai_ku'] = '财库: ' + ', '.join(ku_zhi) if ku_zhi else '原局无明库'
    return result


def apply_shi_ye_rules(ds, rule):
    result = {}
    r = rule.get('rule', {})
    month_ss = ds['十神'].get('月','?')
    result['month_analysis'] = '月干为' + month_ss
    for mr in r.get('month_stem_rules', []):
        if month_ss in mr.get('condition',''):
            result['month_analysis'] = mr.get('text',''); break
    shen_level = ds['身强弱']['等级']
    result['shen_advice'] = ''
    for sr in r.get('shen_rules', []):
        if '身强' in shen_level and '身强' in sr.get('name',''):
            result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
        elif '从弱' in shen_level and '从弱' in sr.get('name',''):
            result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
        elif '身弱' in shen_level and '身弱' in sr.get('name',''):
            result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
    ri_ss = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    for dr in r.get('day_branch_rules', []):
        if ri_ss in dr.get('condition',''):
            result['day_drive'] = dr.get('text',''); break
    else:
        result['day_drive'] = '日支为' + ri_ss
    wx_m = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
    shiye_yun = []
    for y in ds['大运']:
        dg = y['干支'][0]
        if wx_m.get(dg,'') in '火':
            shiye_yun.append(f"  - {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 事业突破期")
    result['da_yun'] = '\n'.join(shiye_yun) if shiye_yun else '  大运不显官杀'
    return result


def check_ds_alignment(full_report, ds):
    errors = []
    s = str(int(ds['身强弱']['总分']))
    if s not in full_report:
        errors.append(f"身强弱分数{s}在报告中未找到")
    if ds['八字'] not in full_report:
        errors.append("八字未出现在报告中")
    return errors


def check_min_lines(full_report, min_lines=800):
    lc = len(full_report.splitlines())
    return [] if lc >= min_lines else [f"总行数{lc}<{min_lines}"]


def execute_pipeline(ds_path, output_path, sections_only=None):
    ds = json.load(open(ds_path))
    results = {}
    rules = {}
    for phase in WORKFLOW['phases']:
        if phase.get('sections'):
            for sec in phase['sections']:
                rp = os.path.join(HARNESS_DIR, sec['rule'])
                if os.path.exists(rp):
                    rules[sec['id']] = load_rule(rp)

    for phase in WORKFLOW['phases']:
        if phase.get('sections'):
            for sec in phase['sections']:
                if sections_only and sec['id'] not in sections_only:
                    continue
                sid = sec['id']
                if sid == 's8':
                    vars_dict = apply_cai_fu_rules(ds, rules.get(sid, {}))
                elif sid == 's10':
                    vars_dict = apply_shi_ye_rules(ds, rules.get(sid, {}))
                else:
                    vars_dict = apply_generic_rules(ds, rules.get(sid, {}), sec['name'])
                
                tpl_path = os.path.join(HARNESS_DIR, sec['template'])
                output = render_template(tpl_path, vars_dict) if os.path.exists(tpl_path) else '['+sec['name']+'无模板]'
                results[sid] = {'name': sec['name'], 'output': output}
                sys.stdout.write(f'  {sec["name"]}: {len(output)}字\n')

    full_report = '\n\n'.join([v['output'] for v in results.values()])
    
    # 完整报告传感器
    for sname in ['check_ds_alignment', 'check_min_lines']:
        f = globals().get(sname)
        if f:
            errs = f(full_report, ds) if sname == 'check_ds_alignment' else f(full_report)
            if errs:
                sys.stdout.write(f'\n 传感器: {errs}\n')
    
    with open(output_path, 'w') as f:
        f.write(full_report)
    return results


if __name__ == '__main__':
    ds_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/weiqiling_ds.json'
    out_path = sys.argv[2] if len(sys.argv) > 2 else '/tmp/harness_output.md'
    only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    ds = json.load(open(ds_path))
    sys.stdout.write(f'数据源: {ds["八字"]} | {ds["日主"]}{ds["日主五行"]} | {int(ds["身强弱"]["总分"])}分{ds["身强弱"]["等级"]}\n')
    sys.stdout.write(f'过滤: {only if only else "全部§"}\n')
    execute_pipeline(ds_path, out_path, only)
    sys.stdout.write(f'输出: {out_path}\n')
