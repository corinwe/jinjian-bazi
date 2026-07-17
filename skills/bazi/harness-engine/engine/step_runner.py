#!/usr/bin/env python3
"""
step_runner.py — 通用步骤执行器 v4 (含等级判定+发财升官年份+天干财星)
"""
import json, os, sys, yaml, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflow_v2 import WORKFLOW, load_rule

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE_DIR = os.path.join(HARNESS_DIR, 'output', 'state')
os.makedirs(STATE_DIR, exist_ok=True)


# L2: 跨会话状态管理
def save_state(phase_id, completed_sections, label):
    sp = os.path.join(STATE_DIR, f'pipeline_{label}.state')
    with open(sp, 'w') as f:
        json.dump({'phase_id': phase_id, 'completed': completed_sections, 'timestamp': time.time()}, f)


def load_state(label):
    sp = os.path.join(STATE_DIR, f'pipeline_{label}.state')
    return json.load(open(sp)) if os.path.exists(sp) else None


def clear_state(label):
    sp = os.path.join(STATE_DIR, f'pipeline_{label}.state')
    if os.path.exists(sp): os.remove(sp)


# L1: 任务内自我反思
def self_reflect(output, ds, sec_name):
    issues = []
    if len(output.strip()) < 10: issues.append('内容过短')
    if '{' in output and '}' in output:
        unfilled = [p.split('}')[0] for p in output.split('{')[1:] if '}' in p]
        issues.append(f'未填充模板变量: {unfilled}')
    return issues


def render_template(tpl_path, vars_dict):
    with open(tpl_path) as f:
        tpl = f.read()
    for k, v in vars_dict.items():
        tpl = tpl.replace('{'+k+'}', v if v else '[待生成]')
    return tpl


WX_M = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}


# ═══ 财富分析（v3含天干财星+等级+发财年份）═══
def apply_cai_fu_rules(ds, rule):
    result = {}
    ss = ds.get('十神', {})
    cai_items = []
    # 天干财星
    for pos, label in [('年','年'),('月','月'),('时','时')]:
        if '财' in ss.get(pos, ''):
            cai_items.append((f'{label}干', ds[f'{label}干'], ss[pos]))
    # 地支财星
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk, []):
            if c['十神'] in ['正财','偏财']:
                cai_items.append((zk, c['天干'], c['十神']))
    result['cai_table'] = '\n'.join([f"| {p} | {t} | {s} |" for p,t,s in cai_items]) if cai_items else "| 财星不显 |"

    # 财富路线
    pos_texts = []
    m = rule.get('rule', {}).get('position_rules', [])
    for ri in m:
        for pos, tg, sv in cai_items:
            matched = False
            n = ri['name']
            if n in ('年干财','年支财') and '年' in pos: matched = True
            elif n == '月财' and '月' in pos: matched = True
            elif n == '日财' and '日' in pos: matched = True
            elif n == '时财' and '时' in pos: matched = True
            if matched:
                pos_texts.append('- ' + n + '：' + ri['text'])
                break
    result['cai_road'] = '\n'.join(pos_texts) if pos_texts else '财星不显'

    shen_lv = ds['身强弱']['等级']
    cai_cnt = len(cai_items)
    cs = min(cai_cnt, 5)
    if '身强' in shen_lv: ss2 = 3.0
    elif '从弱' in shen_lv: ss2 = 2.0
    elif '中和' in shen_lv: ss2 = 2.0
    else: ss2 = 1.0
    cy_cnt = sum(1 for y in ds['大运'] if WX_M.get(y['干支'][0],'') in '木水')
    ys = 2.0 if cy_cnt >= 3 else (1.0 if cy_cnt >= 1 else 0.0)
    has_ss = ss.get('月','') in ['食神','伤官'] or any(c['十神'] in ['食神','伤官'] for c in ds['藏干十神'].get('日支',[]))
    sss = 2.0 if has_ss else 0.0
    total = cs + ss2 + ys + sss
    if total >= 9: g = '8-10级(高等级财富-富裕阶层)'
    elif total >= 6: g = '5-7级(中高等级财富-小康以上)'
    elif total >= 4: g = '3-4级(中等财富)'
    else: g = '1-2级(低等级财富)'
    result['cai_grade'] = f'综合评分{total:.1f}/10，{g}。评分：财星{cs}分+身强弱{ss2}分+大运{ys}分+食伤{sss}分。'
    result['shen_cai'] = ''
    for sr in rule.get('rule', {}).get('shen_rules', []):
        n2 = sr.get('name','')
        if '身强' in shen_lv and '身强' in n2: result['shen_cai'] = sr.get('text',''); break
        elif '从弱' in shen_lv and '从弱' in n2: result['shen_cai'] = sr.get('text',''); break
        elif '中和' in shen_lv and '中和' in n2: result['shen_cai'] = sr.get('text',''); break
        elif '身弱' in shen_lv and '身弱' in n2: result['shen_cai'] = sr.get('text',''); break

    # 发财年份
    fy = []
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        if dw in '木水':
            fy.append(f"  {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 财运窗口期")
    result['fa_cai_year'] = '\n'.join(fy) if fy else '  无明确发财窗口。'

    # 大运财富窗口
    cy = []
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        if dw in '木水':
            cy.append(f"  {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 财富机遇期")
    result['da_yun_cai'] = '\n'.join(cy) if cy else '  大运不显财干'
    ku_zhi = [ds[zk] for zk in ['年支','月支','日支','时支'] if ds[zk] in '辰戌丑未']
    result['kai_cai_ku'] = '财库: ' + ', '.join(ku_zhi) if ku_zhi else '原局无明库'
    return result


# ═══ 事业分析（v3含等级+升官年份）═══
def apply_shi_ye_rules(ds, rule):
    result = {}
    r = rule.get('rule', {})
    ss = ds.get('十神', {})
    month_ss = ss.get('月','?')
    result['hang_ye'] = ''
    for mr in r.get('month_stem_rules', []):
        if month_ss in mr.get('condition',''):
            result['hang_ye'] = mr.get('text',''); break
    result['hang_ye'] = result['hang_ye'] or ('月干为' + month_ss)

    shen_lv = ds['身强弱']['等级']
    result['shen_advice'] = ''
    for sr in r.get('shen_rules', []):
        n2 = sr.get('name','')
        if '身强' in shen_lv and '身强' in n2: result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
        elif '从弱' in shen_lv and '从弱' in n2: result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
        elif '中和' in shen_lv and '中和' in n2: result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break
        elif '身弱' in shen_lv and '身弱' in n2: result['shen_advice'] = sr.get('text','') + '\n' + sr.get('advice',''); break

    ri_ss = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    result['day_drive'] = ri_ss

    # 事业等级
    guan_score = 0
    if '官' in ss.get('月','') or '杀' in ss.get('月',''): guan_score += 2
    if '官' in str(ds['藏干十神']['日支']): guan_score += 1
    if '官' in ss.get('年','') or '官' in ss.get('时',''): guan_score += 1
    if '身强' in shen_lv: ss2 = 3.0
    elif '从弱' in shen_lv: ss2 = 2.0
    elif '中和' in shen_lv: ss2 = 2.0
    else: ss2 = 1.0
    gy_cnt = sum(1 for y in ds['大运'] if WX_M.get(y['干支'][0],'') in '火')
    gys = 2.0 if gy_cnt >= 2 else (1.0 if gy_cnt >= 1 else 0.0)
    ciyin = 1.0 if ('官' in ss.get('年','') or '印' in ss.get('月','')) else 0.0
    total2 = guan_score + ss2 + gys + ciyin
    if total2 >= 8: gg = '7-8级(高层管理/创始人)'
    elif total2 >= 5: gg = '5-6级(中层管理)'
    elif total2 >= 3: gg = '3-4级(基层到中层)'
    else: gg = '1-2级(事业运弱)'
    result['shiye_grade'] = f'综合评分{total2:.1f}/10，{gg}。评分：官杀{guan_score}分+身强弱{ss2}分+大运{gys}分+财印{ciyin}分。'

    # 升官年份
    sy = []
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        if dw in '火':
            sy.append(f"  {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 官杀透干，事业突破期")
    result['sheng_guan_year'] = '\n'.join(sy) if sy else '  大运不显官杀，事业宜稳中求进。'

    sy2 = []
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        if dw in '火':
            sy2.append(f"  {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 事业突破期")
    result['da_yun_shiye'] = '\n'.join(sy2) if sy2 else '  大运不显官杀'
    return result


# ═══ 通用规则（学业文昌v3）═══
def apply_generic_rules(ds, rule, sec_name):
    result = {}
    r = rule.get('rule', {})
    items = [ar.get('text', '') for ar in r.get('analysis_rules', [])]
    result['ANALYSIS'] = '\n'.join(items) if items else sec_name + '分析'

    if sec_name in ('学业', '补文昌'):
        # 文昌（已用年干公式）
        wen = ds.get('神煞', {}).get('文昌贵人', '未找到')
        result['wenchang_pos'] = f'文昌贵人在：{wen}。'
        zhi_pos = [ds.get(k,'') for k in ['年支','月支','日支','时支']]
        for i, label in enumerate(['年','月','日','时']):
            if wen in zhi_pos[i]:
                result['wenchang_pos'] += f'在{label}柱，文昌在四柱。'
                if label in '年月': result['wenchang_pos'] += '早慧早成，学历运强。'
                else: result['wenchang_pos'] += '大器晚成，中年后学习力更佳。'
                break
        else:
            result['wenchang_pos'] += '不在四柱地支，需大运流年引出。'
        
        # 印星分析
        shen_lv = ds['身强弱']['等级']
        yin_r = rule.get('rule', {}).get('yin_rules', [])
        yin_text = ''
        for yr in yin_r:
            n2 = yr.get('name','')
            if '身强' in shen_lv and '身强' in n2: yin_text = yr.get('text',''); break
            elif '身弱' in shen_lv and ('身弱' in n2 or '从弱' in n2): yin_text = yr.get('text',''); break
            elif '中和' in shen_lv and '中和' in n2: yin_text = yr.get('text',''); break
        result['yin_analysis'] = yin_text or f'身强弱={shen_lv}'
        
        # 18岁前大运
        yun18 = [y for y in ds['大运'] if int(y['起始年龄']) < 18]
        yun18_text = []
        for y in yun18:
            yun18_text.append(f"{y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁)")
        result['yun_18'] = '18岁前大运：' + ', '.join(yun18_text) if yun18_text else '起运较晚'
        
        # 学历等级
        edu_score = 0
        # 印星分
        has_yin = '印' in str(ds['十神']) or '印' in str(ds['藏干十神'])
        edu_score += 2 if has_yin else 0
        # 身强弱分
        if '身弱' in shen_lv: edu_score += 3
        elif '中和' in shen_lv: edu_score += 2
        elif '从弱' in shen_lv: edu_score += 2
        else: edu_score += 1
        # 文昌分
        if wen in zhi_pos: edu_score += 3
        else: edu_score += 0
        # 18岁前大运分
        y18_wen = sum(1 for y in yun18 if WX_M.get(y['干支'][0],'') in '火土')
        edu_score += 2 if y18_wen >= 1 else 0
        
        if edu_score >= 8: eg = '7-8级(高等学历-研究生水平)'
        elif edu_score >= 5: eg = '5-6级(中等学历-本科水平)'
        elif edu_score >= 3: eg = '3-4级(基础教育)'
        else: eg = '1-2级(学历偏低)'
        result['education_grade'] = f'综合评分{edu_score}/10，{eg}。评分依据：印星{2 if has_yin else 0}分+身强弱{edu_score}分+文昌{3 if wen in zhi_pos else 0}分+大运{2 if y18_wen>=1 else 0}分。'
        
        # 补文昌
        fw_map = {'子':'北','丑':'东北','寅':'东北','卯':'东','辰':'东南','巳':'东南',
                  '午':'南','未':'西南','申':'西南','酉':'西','戌':'西北','亥':'西北'}
        result['wenchang_bu'] = f'书房宜{fw_map.get(wen, "")}向' if wen in fw_map else '文昌按年寻找。'

    for k in r.get('template_vars', {}):
        if k not in result:
            result[k] = '[' + k + ']'
    return result


# ═══ 传感器 ═══
def check_ds_alignment(full_report, ds):
    errors = []
    s = str(int(ds['身强弱']['总分']))
    if s not in full_report: errors.append(f'身强弱分数{s}在报告中未找到')
    if ds['八字'] not in full_report: errors.append('八字未出现在报告中')
    return errors


def check_min_lines(full_report, min_lines=800):
    lc = len(full_report.splitlines())
    return [] if lc >= min_lines else [f'总行数{lc}<{min_lines}']


# ═══ 主执行器 ═══
def execute_pipeline(ds_path, output_path, sections_only=None, label=None):
    ds = json.load(open(ds_path))
    label = label or ds.get('八字', 'unknown')
    results = {}
    rules = {}
    for phase in WORKFLOW['phases']:
        if phase.get('sections'):
            for sec in phase['sections']:
                rp = os.path.join(HARNESS_DIR, sec['rule'])
                if os.path.exists(rp): rules[sec['id']] = load_rule(rp)

    state = load_state(label)
    completed = state.get('completed', []) if state else []
    if state: sys.stdout.write(f'  [L2] 恢复: 已完成{len(completed)}个§\n')

    for phase in WORKFLOW['phases']:
        if phase.get('sections'):
            for sec in phase['sections']:
                if sections_only and sec['id'] not in sections_only: continue
                if sec['id'] in completed: continue
                sid = sec['id']
                if sid == 's8':
                    vars_dict = apply_cai_fu_rules(ds, rules.get(sid, {}))
                elif sid == 's10':
                    vars_dict = apply_shi_ye_rules(ds, rules.get(sid, {}))
                else:
                    vars_dict = apply_generic_rules(ds, rules.get(sid, {}), sec['name'])
                
                tpl_path = os.path.join(HARNESS_DIR, sec['template'])
                output = render_template(tpl_path, vars_dict) if os.path.exists(tpl_path) else '['+sec['name']+'无模板]'
                
                l1_issues = self_reflect(output, ds, sec['name'])
                l1_tag = '\u2705' if not l1_issues else '\u26a0\ufe0f'
                for iss in l1_issues: sys.stdout.write(f'    [L1] {iss}\n')
                
                results[sid] = {'name': sec['name'], 'output': output}
                completed.append(sid)
                save_state(4, completed, label)
                sys.stdout.write(f'  {l1_tag} {sec["name"]}: {len(output)}字\n')

    full_report = '\n\n'.join([v['output'] for v in results.values()])
    
    for sname in ['check_ds_alignment', 'check_min_lines']:
        f = globals().get(sname)
        if f:
            errs = f(full_report, ds) if sname == 'check_ds_alignment' else f(full_report)
            if errs: sys.stdout.write(f'\n 传感器: {errs}\n')
    
    with open(output_path, 'w') as f: f.write(full_report)
    if not sections_only: clear_state(label)
    return results


if __name__ == '__main__':
    ds_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/weiqiling_ds.json'
    out_path = sys.argv[2] if len(sys.argv) > 2 else '/tmp/harness_output.md'
    only = sys.argv[3].split(',') if len(sys.argv) > 3 else None
    label = sys.argv[4] if len(sys.argv) > 4 else None
    ds = json.load(open(ds_path))
    sys.stdout.write(f'数据源: {ds["八字"]} | {ds["日主"]}{ds["日主五行"]} | {int(ds["身强弱"]["总分"])}分{ds["身强弱"]["等级"]}\n')
    sys.stdout.write(f'过滤: {only if only else "全部§"}\n')
    execute_pipeline(ds_path, out_path, only, label)
    sys.stdout.write(f'输出: {out_path}\n')
