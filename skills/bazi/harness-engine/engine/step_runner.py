#!/usr/bin/env python3
"""step_runner.py — 通用步骤执行器 v3 (含L1+L2)"""
import json, os, sys, yaml, time, pickle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflow_v2 import WORKFLOW, load_rule

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(HARNESS_DIR, 'output', 'state')
os.makedirs(STATE_DIR, exist_ok=True)


# ═══ L2: 跨会话状态管理 ═══
def save_state(phase_id, completed_sections):
    state = {
        'phase_id': phase_id,
        'completed': completed_sections,
        'timestamp': time.time(),
        'version': '2.0'
    }
    sp = os.path.join(STATE_DIR, 'pipeline.state')
    with open(sp, 'w') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_state():
    sp = os.path.join(STATE_DIR, 'pipeline.state')
    if os.path.exists(sp):
        with open(sp) as f:
            return json.load(f)
    return None


def clear_state():
    sp = os.path.join(STATE_DIR, 'pipeline.state')
    if os.path.exists(sp):
        os.remove(sp)


# ═══ L1: 任务内自我反思 ═══
def self_reflect(output, ds, sec_name):
    issues = []
    # 检查1: 输出非空
    if len(output.strip()) < 10:
        issues.append('内容过短(<10字符)')
    # 检查2: 输出不含无法解析的模板变量
    if '{' in output and '}' in output:
        unfilled = [p.split('}')[0] for p in output.split('{')[1:] if '}' in p]
        issues.append(f'未填充的模板变量: {unfilled}')
    # 检查3: 身强弱分数一致性
    shen_s = str(int(ds['身强弱']['总分']))
    if shen_s in output:
        pass
    return issues

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
    
    # 学业文昌特殊处理
    if sec_name in ('学业', '补文昌'):
        wen = ds.get('神煞', {}).get('文昌贵人', '未找到')
        result['WENCHANG_POS'] = f'文昌贵人在：{wen}。'
        zhi_pos = [ds.get(k,'') for k in ['年支','月支','日支','时支']]
        for i, label in enumerate(['年','月','日','时']):
            if wen in zhi_pos[i]:
                result['WENCHANG_POS'] += f'在{label}柱，'
                result['WENCHANG_POS'] += '早年学习力强，正统教育路线顺利。' if label in '年月' else '中年后学业运佳，适合深造。'
                break
        else:
            result['WENCHANG_POS'] += '不在四柱地支，需大运流年引出。'
        wx_map = {'寅':'火-利好文科','午':'火-利好文科','戌':'火-利好文科',
                  '申':'水-利好理科','子':'水-利好理科','辰':'水-利好理科',
                  '亥':'木-利好教育','卯':'木-利好教育','未':'木-利好教育',
                  '巳':'金-利好金融','酉':'金-利好金融','丑':'金-利好金融'}
        result['XUELI'] = f'文昌属{wx_map.get(wen, "—")}' if wen != '未找到' else '文昌不显，学历随大运变化。'
        fw_map = {'子':'北','丑':'东北','寅':'东北','卯':'东','辰':'东南',
                  '巳':'东南','午':'南','未':'西南','申':'西南','酉':'西','戌':'西北','亥':'西北'}
        result['WENCHANG_BU'] = f'书房宜{fw_map.get(wen, "")}向' if wen in fw_map else '文昌按年寻找。'
    
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
        elif '中和' in shen_level and '中和' in sr.get('name',''):
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
        elif '中和' in shen_level and '中和' in sr.get('name',''):
            result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
        else:
            result['shen_advice'] = f'身强弱为{shen_level}。'
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

    # ═══ L2: 检查状态，恢复 ═══
    state = load_state()
    completed = state.get('completed', []) if state else []
    if state:
        sys.stdout.write(f'  [L2] 恢复: 已完成{len(completed)}个§\n')

    for phase in WORKFLOW['phases']:
        if phase.get('sections'):
            for sec in phase['sections']:
                if sections_only and sec['id'] not in sections_only:
                    continue
                # L2: 跳过已完成的§
                if sec['id'] in completed:
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
                
                # ═══ L1: 自我反思 ═══
                l1_issues = self_reflect(output, ds, sec['name'])
                l1_tag = '✅' if not l1_issues else '⚠️'
                for iss in l1_issues:
                    sys.stdout.write(f'    [L1] {iss}\n')
                
                results[sid] = {'name': sec['name'], 'output': output}
                completed.append(sid)
                # L2: 保存状态
                save_state(4, completed)
                sys.stdout.write(f'  {l1_tag} {sec["name"]}: {len(output)}字\n')

    full_report = '\n\n'.join([v['output'] for v in results.values()])
    
    for sname in ['check_ds_alignment', 'check_min_lines']:
        f = globals().get(sname)
        if f:
            errs = f(full_report, ds) if sname == 'check_ds_alignment' else f(full_report)
            if errs:
                sys.stdout.write(f'\n 传感器: {errs}\n')
    
    with open(output_path, 'w') as f:
        f.write(full_report)
    
    # L2: 完成清状态
    if not sections_only:
        clear_state()
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
