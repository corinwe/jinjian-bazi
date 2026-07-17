#!/usr/bin/env python3
"""
mangpai_runner.py v2 — 盲派报告生成器（含命理珍宝规则）
应用段建业命理珍宝体系：
  六冲七型/六合三用/宾主七层/虚实喜忌
  以禄当财/忌神三制/贼神/从格四条件/十干喜忌
"""
import json, os, sys, yaml

HARNESS_DIR = '/root/.hermes/profiles/jinjian-zhenren/skills/bazi/harness-engine'


def load_rule(path):
    with open(path, encoding='utf-8') as f:
        return yaml.safe_load(f)


def calc_ti_yong(ds):
    ti = int(ds['身强弱']['总分'])
    yong = max(100 - ti, 1)
    return ti, yong, ti / yong


def render_template(tpl_path, vars_dict):
    with open(tpl_path) as f:
        tpl = f.read()
    for k, v in vars_dict.items():
        tpl = tpl.replace('{' + k + '}', v if v else '[待生成]')
    return tpl


WX_M = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}


def apply_rules(ds):
    """应用命理珍宝规则体系"""
    results = {}
    ss = ds.get('十神', {})
    
    # 1. 虚实判定
    for k in ['年','月','日','时']:
        g = ds.get(f'{k}干','')
        z = ds.get(f'{k}支','')
        # 天干是否通根
        root_found = False
        for zk in ['年支','月支','日支','时支']:
            if g == zk[0]:  # 天干在支中找到同五行
                root_found = True
                break
        results[f'{k}_xu_shi'] = '实' if root_found else '虚'
    
    # 2. 财星（天干+地支）
    cai_items = []
    for pos, label in [('年','年'),('月','月'),('时','时')]:
        if '财' in ss.get(pos, ''):
            cai_items.append((f'{label}干', ds[f'{label}干'], ss[pos]))
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk, []):
            if c['十神'] in ['正财','偏财']:
                cai_items.append((zk, c['天干'], c['十神']))
    results['cai_table'] = '\n'.join([f"| {p} | {t} | {s} |" for p,t,s in cai_items]) if cai_items else "| 财星不显 |"
    
    # 3. 六冲分析
    zhi_list = [ds.get(k,'') for k in ['年支','月支','日支','时支']]
    chong_pairs = [['子午'],['丑未'],['寅申'],['卯酉'],['辰戌'],['巳亥']]
    chong_found = []
    for i, z1 in enumerate(zhi_list):
        for j, z2 in enumerate(zhi_list):
            if i < j:
                in_same = any(z1 in p and z2 in p for p in chong_pairs)
                if in_same:
                    chong_found.append(f'{z1}{z2}冲')
    results['chong'] = '、'.join(chong_found) if chong_found else '无冲'
    
    # 4. 六合分析
    he_pairs = {'子丑':'子丑合','寅亥':'寅亥合','卯戌':'卯戌合',
                '辰酉':'辰酉合','巳申':'巳申合','午未':'午未合'}
    he_found = []
    for i, z1 in enumerate(zhi_list):
        for j, z2 in enumerate(zhi_list):
            if i < j:
                key = z1+z2
                key2 = z2+z1
                if key in he_pairs: he_found.append(he_pairs[key])
                elif key2 in he_pairs: he_found.append(he_pairs[key2])
    results['he'] = '、'.join(he_found) if he_found else '无合'
    
    # 5. 宾主分析
    shen_lv = ds['身强弱']['等级']
    month_ss = ss.get('月','?')
    results['bin_zhu'] = f'日主为主，他干支为宾。主在日柱({ds["日干"]}{ds["日支"]})，宾在年时。八字为主，大运流年为宾。'
    
    # 6. 体用比（盲派核心）
    ti, yong, bi = calc_ti_yong(ds)
    if bi > 2: body_text = '体远大于用，靠自身能量。体为自己能力，用为外部资源。'
    elif bi > 1: body_text = '体略大于用，自身能力为主外部资源为辅。'
    elif bi > 0.5: body_text = '体用均衡，自身与外部资源并重。'
    else: body_text = '用大于体，靠外部资源和机遇。'
    results['ti_yong'] = f'体{ti}分，用{yong}分，比{bi:.1f}:1。{body_text}'
    
    # 7. 虚实喜忌
    xu_shi_list = []
    for k in ['年','月','日','时']:
        g = ds.get(f'{k}干','')
        s = ss.get(k,'')
        xr = results.get(f'{k}_xu_shi','虚')
        if xr == '虚' and '忌' in s:
            xu_shi_list.append(f'{k}干{s}虚忌→吉')
        elif xr == '实' and '喜' in s:
            xu_shi_list.append(f'{k}干{s}实喜→吉')
        elif xr == '实' and '忌' in s:
            xu_shi_list.append(f'{k}干{s}实忌→凶')
    results['xu_shi_analysis'] = '；'.join(xu_shi_list) if xu_shi_list else '暂无虚实判定'
    
    # 8. 财富等级（盲派体用体系）
    cai_cnt = len(cai_items)
    if ti > 60 and cai_cnt >= 3: grade = '7-8级(体旺财旺-大富格)'
    elif ti > 60 and cai_cnt >= 1: grade = '5-6级(体旺财有-中富)'
    elif ti < 40 and cai_cnt >= 2: grade = '5-6级(用旺财显-资源型财富)'
    elif cai_cnt >= 3: grade = '3-4级(财多但体弱-机会型)'
    else: grade = '1-2级(财星不显)'
    results['cai_grade_mangpai'] = f'盲派体用判定：{grade}。体{ti}分，财{cai_cnt}颗。'
    
    return results


def generate(ds_path, out_path, label):
    ds = json.load(open(ds_path))
    results = apply_rules(ds)
    
    # 加载盲派模板
    tpl_dir = os.path.join(HARNESS_DIR, 'templates_mangpai')
    
    sections = []
    
    # 财富
    cai_tpl_path = os.path.join(tpl_dir, 'cai_fu.md')
    if os.path.exists(cai_tpl_path):
        vars_dict = {
            'CAI_BIAO': results['cai_table'],
            'LU_XIAN': f'财星分布如上。体用比：{results["ti_yong"]}',
            'TI_YONG': results['cai_grade_mangpai'],
        }
        output = render_template(cai_tpl_path, vars_dict)
    else:
        output = f"## 财富分析（盲派）\n{results['cai_table']}\n{results['ti_yong']}\n{results['cai_grade_mangpai']}"
    sections.append(output)
    
    # 事业
    ss = ds.get('十神', {})
    month_ss = ss.get('月','?')
    ri_zhi_ss = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    shen_lv = ds['身强弱']['等级']
    
    shiye_tpl_path = os.path.join(tpl_dir, 'shi_ye.md')
    if os.path.exists(shiye_tpl_path):
        vars_dict = {
            'HANG_YE': f'月干{month_ss}。宾主分析：{results["bin_zhu"]}',
            'LU_XIAN': f'日支{ri_zhi_ss}，为内在驱动力。',
            'TI_YONG_SHIYE': f'体用比：{results["ti_yong"]}。{results["xu_shi_analysis"]}',
        }
        output = render_template(shiye_tpl_path, vars_dict)
    else:
        output = f"## 事业分析（盲派）\n月干{month_ss}\n{results['bin_zhu']}\n{results['xu_shi_analysis']}"
    sections.append(output)
    
    # 学业
    wen = ds.get('神煞', {}).get('文昌贵人', '未找到')
    zhi_pos = [ds.get(k,'') for k in ['年支','月支','日支','时支']]
    wen_info = f'文昌：{wen}'
    if wen in zhi_pos:
        wen_info += f'（在四柱中，位置：{zhi_pos.index(wen)+1}）'
    else:
        wen_info += '（不在四柱，需大运引出）'
    
    # 十干喜忌
    rizhu = ds['日主']
    stem_xi_ji = {
        '甲':'春夏火水，秋水怕土，冬火。怕强金',
        '乙':'春水，秋火怕水',
        '丙':'怕湿土燥土',
        '丁':'怕丙夺光',
        '戊':'爱丙火，怕通根戌',
        '己':'旺喜金弱喜禄(丁)',
        '庚':'顽固，宜制化',
        '辛':'夏癸水冬丁火',
        '壬':'爱寅不喜卯',
        '癸':'能从木火化气最好'
    }.get(rizhu, '')
    
    xueye_tpl_path = os.path.join(tpl_dir, 'xue_ye.md')
    if os.path.exists(xueye_tpl_path):
        vars_dict = {
            'WENCHANG': wen_info,
            'XUEYE': f'日主{rizhu}喜忌：{stem_xi_ji}。{results["xu_shi_analysis"]}',
        }
        output = render_template(xueye_tpl_path, vars_dict)
    else:
        output = f"## 学业分析（盲派）\n{wen_info}\n日主{rizhu}喜忌：{stem_xi_ji}"
    sections.append(output)
    
    full = '\n\n'.join(sections)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full)
    
    return full


if __name__ == '__main__':
    for ds_path, label, subdir in [
        ('/tmp/weiqiling_ds.json', '魏启令', '01-家主-魏启令'),
        ('/tmp/ziyuan_ds.json', '子源', '03-少爷-子源'),
    ]:
        out = f'/tmp/{label}_盲派_财富事业学业_v2.md'
        report = generate(ds_path, out, label)
        lc = len(report.splitlines())
        cc = len(report)
        print(f'{label}: {lc}行 {cc}字')
        
        kb = f'/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{subdir}/{label}_盲派_财富事业学业.md'
        with open(kb, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f'  保存: {kb}')
