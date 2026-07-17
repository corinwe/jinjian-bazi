#!/usr/bin/env python3
"""
step_runner.py — Harness Engine 步骤执行器
读workflow → 执行每步 → 传感器验证
模型只做翻译，不做决策
"""
import json, os, sys, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from workflow_v2 import WORKFLOW, load_rule

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── 模板引擎 ───
def render_template(template_path, vars_dict):
    """渲染模板，替换{变量}为实际内容"""
    with open(template_path) as f:
        tpl = f.read()
    for k, v in vars_dict.items():
        tpl = tpl.replace('{'+k+'}', v)
    return tpl


# ─── 规则操作器（从DS提取数据，匹配规则） ───
def apply_cai_fu_rules(ds, rule):
    """应用财富规则到DS数据"""
    results = {}
    
    # 1. 找财星
    cai_items = []
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk, []):
            if c['十神'] in ['正财','偏财']:
                cai_items.append((zk, c['天干'], c['十神']))
    
    # 2. 财星位置分析
    pos_texts = []
    for r in rule['position_rules']:
        matched = False
        for pos, tg, ss in cai_items:
            if pos == r['name'].replace('财',''):
                matched = True
                break
        if matched:
            pos_texts.append(f"- {r['name']}：{r['text']}")
    
    results['cai_table'] = '\n'.join([f"| {p} | {t} | {s} |" for p,t,s in cai_items]) if cai_items else "| 财星不显 | — | — |"
    results['cai_positions'] = '\n'.join(pos_texts) if pos_texts else "原局财星不显，财富需大运引出。"
    
    # 3. 身强弱vs财富
    shen_level = ds['身强弱']['等级']
    shen_text = "中和格局，财为中性。"
    for r in rule['shen_rules']:
        if '身强' in shen_level and '身强' in r['name']:
            shen_text = r['text']
            break
        elif '从弱' in shen_level and '从弱' in r['name']:
            shen_text = r['text']
            break
        elif '身弱' in shen_level and '身弱' in r['name']:
            shen_text = r['text']
            break
    results['shen_analysis'] = shen_text
    
    # 4. 食伤生财
    has_shishen = (
        ds['十神'].get('月','') in ['食神','伤官'] or
        any(c['十神'] in ['食神','伤官'] for c in ds['藏干十神'].get('日支',[]))
    )
    results['shi_shang'] = rule['shi_shang_rule']['text'] if has_shishen else ""
    
    # 5. 财星状态
    gan_wx_map = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
    cai_wx_dry = False
    for gan_key in ['年干','月干','日干','时干']:
        g = ds[gan_key]
        if g in gan_wx_map and gan_wx_map[g] in '木':
            cai_wx_dry = True
    results['state'] = rule['state_rules'][0]['text'] if cai_wx_dry else rule['state_rules'][1]['text']
    
    # 6. 大运财富窗口
    wx_m2 = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
    cai_yun = []
    for y in ds['大运']:
        dg = y['干支'][0]
        if wx_m2.get(dg,'') in '木水':
            cai_yun.append(f"  - {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 财星或食伤透干，财富机遇期")
    results['da_yun'] = '\n'.join(cai_yun) if cai_yun else "  大运不显财干，财富宜守不宜攻。"
    
    # 7. 开财库
    ku_zhi = [ds[zk] for zk in ['年支','月支','日支','时支'] if ds[zk] in '辰戌丑未']
    results['kai_ku'] = f"原局财库：{', '.join(ku_zhi)}。{'被冲开的大运是财富释放期。' if ku_zhi else '原局无明库，大运遇辰戌丑未为借库。'}"
    
    return results


def apply_shi_ye_rules(ds, rule):
    """应用事业规则到DS数据"""
    results = {}
    
    # 1. 月干十神→事业倾向
    month_ss = ds['十神'].get('月','?')
    results['month_analysis'] = "月干为" + month_ss
    for r in rule['month_stem_rules']:
        if month_ss in r['condition']:
            results['month_analysis'] = r['text']
            break
    
    # 2. 身强弱→事业建议
    shen_level = ds['身强弱']['等级']
    results['shen_advice'] = ""
    for r in rule['shen_rules']:
        if '身强' in shen_level and '身强' in r['name']:
            results['shen_advice'] = r['text'] + '\n' + r['advice']
            break
        elif '从弱' in shen_level and '从弱' in r['name']:
            results['shen_advice'] = r['text'] + '\n' + r['advice']
            break
        elif '身弱' in shen_level and '身弱' in r['name']:
            results['shen_advice'] = r['text'] + '\n' + r['advice']
            break
    
    # 3. 日支十神→内在驱动力
    ri_ss = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    results['day_drive'] = "日支为" + ri_ss
    for r in rule['day_branch_rules']:
        if ri_ss in r['condition']:
            results['day_drive'] = r['text']
            break
    
    # 4. 大运事业窗口
    wx_m2 = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
    shiye_yun = []
    for y in ds['大运']:
        dg = y['干支'][0]
        if wx_m2.get(dg,'') in '火':
            shiye_yun.append(f"  - {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 官杀透干，事业突破期✅")
    if not shiye_yun:
        for y in ds['大运']:
            dg = y['干支'][0]
            if wx_m2.get(dg,'') in '木':
                shiye_yun.append(f"  - {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 财星透干，事业同步上升")
    results['da_yun'] = '\n'.join(shiye_yun) if shiye_yun else "  大运不显官财干，事业宜稳中求进。"
    
    return results


# ─── 传感器（计算型验证） ───
def check_cai_fu(output, ds):
    """财富分析传感器"""
    errors = []
    if '财星' not in output and '财富' not in output:
        errors.append("缺财富相关关键词")
    if len(output) < 50:
        errors.append("内容过短(<50字符)")
    return errors


def check_shi_ye(output, ds):
    """事业分析传感器"""
    errors = []
    if '事业' not in output and '行业' not in output:
        errors.append("缺事业相关关键词")
    if len(output) < 50:
        errors.append("内容过短(<50字符)")
    return errors


def check_min_lines(report, min_lines=800):
    return [] if len(report.splitlines()) >= min_lines else [f"行数不足:{len(report.splitlines())}<{min_lines}"]


# ─── 主执行器 ───
def execute_pipeline(ds_path, output_path):
    """完整执行一次pipeline"""
    ds = json.load(open(ds_path))
    results = {}
    
    # Phase 3: 加载规则
    rules = {}
    for phase in WORKFLOW['phases']:
        if phase['type'] == 'orchestrated':
            for sec in phase.get('sections', []):
                rule_path = os.path.join(HARNESS_DIR, sec['rule'])
                if os.path.exists(rule_path):
                    rules[sec['id']] = load_rule(rule_path)
    
    # Phase 4: 生成模块
    for phase in WORKFLOW['phases']:
        if phase['type'] == 'orchestrated':
            for sec in phase['sections']:
                rule_data = rules.get(sec['id'])
                if not rule_data:
                    results[sec['id']] = f"[规则缺失: {sec['rule']}]"
                    continue
                
                rule = rule_data.get('rule', {})
                
                # 应用规则
                if sec['id'] == 's8':
                    vars_dict = apply_cai_fu_rules(ds, rule)
                elif sec['id'] == 's10':
                    vars_dict = apply_shi_ye_rules(ds, rule)
                else:
                    results[sec['id']] = f"[未实现的规则: {sec['id']}]"
                    continue
                
                # 渲染模板
                tpl_path = os.path.join(HARNESS_DIR, sec['template'])
                if os.path.exists(tpl_path):
                    output = render_template(tpl_path, vars_dict)
                else:
                    # 无模板时直接返回v键值对
                    output = '\n'.join([f"### {k}\n{v}" for k,v in vars_dict.items()])
                
                # 传感器验证
                if sec['id'] == 's8':
                    errs = check_cai_fu(output, ds)
                elif sec['id'] == 's10':
                    errs = check_shi_ye(output, ds)
                
                status = '✅' if not errs else '❌'
                results[sec['id']] = {
                    'name': sec['name'],
                    'output': output,
                    'status': status,
                    'errors': errs
                }
                print(f"  {status} {sec['name']}: {len(output)}字符")
    
    # Phase 5: 质量门禁
    full_report = ''
    for k, v in results.items():
        if isinstance(v, dict):
            full_report += v['output'] + '\n\n'
        elif isinstance(v, str):
            full_report += v + '\n\n'
    
    line_errs = check_min_lines(full_report)
    if line_errs:
        print(f"  行数检查: {'❌ '+'; '.join(line_errs)}")
    
    # 写输出
    with open(output_path, 'w') as f:
        f.write(full_report)
    
    return results


if __name__ == '__main__':
    ds_path = sys.argv[1] if len(sys.argv) > 1 else '/tmp/weiqiling_ds.json'
    out_path = sys.argv[2] if len(sys.argv) > 2 else '/tmp/harness_output.md'
    
    print(f"Harness Engine: 加载数据源 {ds_path}")
    ds = json.load(open(ds_path))
    print(f"  八字: {ds['八字']} | 日主: {ds['日主']}{ds['日主五行']} | 身强弱: {ds['身强弱']['总分']}分{ds['身强弱']['等级']}")
    print()
    
    results = execute_pipeline(ds_path, out_path)
    print(f"\n输出已保存: {out_path}")
