#!/usr/bin/env python3
"""mangpai_runner.py v3 — 全家盲派命理报告生成（含命理珍宝+等级+发财升官年份）"""
import json, os, sys, yaml

HARNESS_DIR = '/root/.hermes/profiles/jinjian-zhenren/skills/bazi/harness-engine'
WX_M = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}


def calc_ti_yong(ds):
    ti = int(ds['身强弱']['总分']); yong = max(100 - ti, 1)
    return ti, yong, ti / yong


def generate(ds_path, label):
    ds = json.load(open(ds_path))
    ss = ds.get('十神', {})
    ti, yong, bi = calc_ti_yong(ds)
    shen_lv = ds['身强弱']['等级']
    report = []
    
    # ═══ 财富分析 ═══
    cai_items = []
    for pos, lb in [('年','年'),('月','月'),('时','时')]:
        if ss.get(pos,'') in ['正财','偏财']: cai_items.append((f'{lb}干', ds[f'{lb}干'], ss[pos]))
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk,[]):
            if c['十神'] in ['正财','偏财']: cai_items.append((zk, c['天干'], c['十神']))
    
    cai_table = '\n'.join([f"| {p} | {t} | {s} |" for p,t,s in cai_items]) if cai_items else "| 财星不显 |"
    
    # 财富路线（位置分析）
    road_lines = []
    for pos, tg, sv in cai_items:
        if '年' in pos: road_lines.append(f'{pos}{tg}{sv} → 祖业根基{"好" if "年干" in pos else "有"}')
        elif '月' in pos: road_lines.append(f'{pos}{tg}{sv} → 青年财运')
        elif '日' in pos: road_lines.append(f'{pos}{tg}{sv} → 中年财富关键期')
        elif '时' in pos: road_lines.append(f'{pos}{tg}{sv} → 晚年财运佳')
    
    # 财富等级（盲派体用体系）
    cai_cnt = len(cai_items)
    if ti >= 60 and cai_cnt >= 3: cai_grade = '7-8级(高等级财富)'
    elif ti >= 60 and cai_cnt >= 1: cai_grade = '5-6级(中高财富)'
    elif ti >= 40 and cai_cnt >= 2: cai_grade = '5-6级(中等财富)'
    elif cai_cnt >= 3: cai_grade = '3-4级(机会型财富)'
    else: cai_grade = '1-2级(财星不显)'
    cai_grade_text = f'盲派体用判定：体{ti}分，财{cai_cnt}颗，等级{cai_grade}'
    
    # 发财年份
    cai_yun = []
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        if dw in '木水':  # 财/食伤运
            cai_yun.append(f"  {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 财运窗口")
    cai_year_text = '\n'.join(cai_yun) if cai_yun else '  大运不显财干，无明确发财窗口'
    
    # 身强弱对财富
    shen_cai = ''
    if '身强' in shen_lv: shen_cai = '身强喜财，有能力追求和驾驭财富。求财主动积极。'
    elif '从弱' in shen_lv: shen_cai = '从弱格局，财为喜用。财富来自外部环境，顺势而为能获利。'
    elif '中和' in shen_lv: shen_cai = '中和格局，财为中性。能赚钱也能守财。运来财来，运去守成。'
    else: shen_cai = '身弱财为忌神。财来耗身，求财辛苦。适合轻资产高利润模式。'
    
    # 体用财富解读
    if bi > 2: ti_text = '体远大于用，靠自己能力赚辛苦钱。'
    elif bi > 1: ti_text = '体略大于用，自身能力为主运气为辅。'
    elif bi > 0.5: ti_text = '体用均衡，自身与外部资源并重。'
    else: ti_text = '用大于体，靠外部资源和机遇。'
    ti_yong_text = f'体用比{bi:.1f}:1。{ti_text}'
    
    wealth_section = f"""## 财富分析（盲派）

### 财星分布（含天干+地支）

{cai_table}

### 财富路线

{chr(10).join(road_lines) if road_lines else '财星不显'}

### 体用比分析

{ti_yong_text}

### 财富等级判定

{cai_grade_text}

### 发财关键年份

{cai_year_text}

### 身强弱对财富的影响

{shen_cai}

### 体用财富解读

体{ti}分代表自身能量和抗风险能力，用{yong}分代表外部资源和机遇。当财星透干或财库冲开的流年，配合喜用大运，是财富增长的窗口期。
"""
    report.append(wealth_section)
    
    # ═══ 事业分析 ═══
    month_ss = ss.get('月','?')
    ri_zhi_ss = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    
    # 行业倾向
    hang_ye = ''
    if month_ss in ['食神','伤官']: hang_ye = '靠才华技术立身。适合创作/咨询/技术/教育类。'
    elif month_ss in ['正官','七杀']: hang_ye = '事业心强。适合管理/体制内/有晋升通道的工作。'
    elif month_ss in ['正印','偏印']: hang_ye = '喜学习重积累。适合研究/学术/工程型岗位。'
    elif '财' in month_ss: hang_ye = '务实重利。适合商务/贸易/金融/运营类。'
    elif month_ss in ['比肩','劫财']: hang_ye = '竞争意识强。适合销售/市场/管理类。'
    else: hang_ye = f'月干为{month_ss}'
    
    # 事业等级
    guan_score = 0
    if '官' in ss.get('月','') or '杀' in ss.get('月',''): guan_score += 2
    if '官' in str(ds['藏干十神']['日支']): guan_score += 1
    if '官' in ss.get('年','') or '官' in ss.get('时',''): guan_score += 1
    if '身强' in shen_lv: ss2 = 3.0
    elif '中和' in shen_lv or '从弱' in shen_lv: ss2 = 2.0
    else: ss2 = 1.0
    gy = sum(1 for y in ds['大运'] if WX_M.get(y['干支'][0],'') in '火')
    gys = 2.0 if gy >= 2 else (1.0 if gy >= 1 else 0.0)
    ci = 1.0 if ('官' in ss.get('年','') or '印' in ss.get('月','')) else 0.0
    total = guan_score + ss2 + gys + ci
    if total >= 8: gg = '7-8级(高层管理)'
    elif total >= 5: gg = '5-6级(中层管理)'
    elif total >= 3: gg = '3-4级(基层到中层)'
    else: gg = '1-2级(事业运弱)'
    shiye_grade = f'综合{total:.1f}/10，{gg}。官杀{guan_score}分+身{ss2}分+大运{gys}分+财印{ci}分'
    
    # 升官年份
    sgy = []
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        if dw in '火':
            sgy.append(f"  {y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁): 官杀透干，事业突破期")
    sgy_text = '\n'.join(sgy) if sgy else '  大运不显官杀'
    
    # 身强弱事业
    shen_advice = ''
    if '身强' in shen_lv: shen_advice = '身强有主见抗压，适合管理/创业。'
    elif '从弱' in shen_lv: shen_advice = '从弱靠顺势而为，适合平台型职业。'
    elif '中和' in shen_lv: shen_advice = '中和适应性强，好运攻差运守。'
    else: shen_advice = '身弱宜合作，适合平台安稳工作。'
    
    career_section = f"""## 事业分析（盲派）

### 适合行业

{hang_ye}日支{ri_zhi_ss}为内在驱动力。

### 事业等级判定

{shiye_grade}

### 升官关键年份

{sgy_text}

### 身强弱与事业

{shen_advice}

### 体用事业分析

体用比{bi:.1f}:1。体{ti}分决定事业抗压能力和责任担当，用{yong}分决定外部资源和机遇。官杀透干的大运是事业突破窗口期。
"""
    report.append(career_section)
    
    # ═══ 学业分析 ═══
    wen = ds.get('神煞', {}).get('文昌贵人', '未找到')
    zhi_pos = [ds.get(k,'') for k in ['年支','月支','日支','时支']]
    
    wen_info = f'文昌贵人在：{wen}。'
    for i, label in enumerate(['年','月','日','时']):
        if wen in zhi_pos[i]:
            wen_info += f'在{label}柱（文昌在四柱）。'
            if label in '年月': wen_info += '早年学习力强。'
            else: wen_info += '中年后学习力更佳。'
            break
    else:
        wen_info += '不在四柱地支，需大运流年引出。'
    
    # 印星分析（身强不喜印，身弱喜印）
    yin_text = ''
    if '身强' in shen_lv: yin_text = '身强不喜印。自身能量已足，逢印反生依赖。18岁前走印运可能学业不利。学业好坏取决于食伤（才华）而非印星（记忆）。'
    elif '身弱' in shen_lv or '从弱' in shen_lv: yin_text = '身弱喜印。印为生扶，18岁前走印运能补足能量，学业顺畅。'
    elif '中和' in shen_lv: yin_text = '中和格局印为中性，学业看大运走向。'
    
    # 学历等级
    edu_score = 0
    has_yin = '印' in str(ss) or '印' in str(ds['藏干十神'])
    edu_score += 2 if has_yin else 0
    if '身弱' in shen_lv: edu_score += 3
    elif '中和' in shen_lv or '从弱' in shen_lv: edu_score += 2
    else: edu_score += 1
    if wen in zhi_pos: edu_score += 3
    yun18 = [y for y in ds['大运'] if int(y['起始年龄']) < 18]
    y18 = sum(1 for y in yun18 if WX_M.get(y['干支'][0],'') in '火土')
    edu_score += 2 if y18 >= 1 else 0
    
    if edu_score >= 8: eg = '7-8级(高等学历-研究生)'
    elif edu_score >= 5: eg = '5-6级(中等学历-本科)'
    elif edu_score >= 3: eg = '3-4级(基础教育)'
    else: eg = '1-2级(学历偏低)'
    edu_grade = f'综合评分{edu_score}/10，{eg}。印星{2 if has_yin else 0}分+身{edu_score}分+文昌{3 if wen in zhi_pos else 0}分+大运{2 if y18>=1 else 0}分'
    
    # 补文昌
    fw_map = {'子':'北','丑':'东北','寅':'东北','卯':'东','辰':'东南','巳':'东南',
              '午':'南','未':'西南','申':'西南','酉':'西','戌':'西北','亥':'西北'}
    wen_bu = f'书房宜{fw_map.get(wen,"")}向' if wen in fw_map else '文昌按年寻找'
    
    education_section = f"""## 学业分析（盲派·含补文昌）

### 文昌贵人

{wen_info}

### 印星与身强弱

{yin_text}

### 18岁前大运

{', '.join([f"{y['干支']}运({int(y['起始年龄'])}-{int(y['终止年龄'])}岁)" for y in yun18]) if yun18 else '起运较晚'}

### 学历等级判定

{edu_grade}

### 补文昌方案

{wen_bu}
"""
    report.append(education_section)
    
    full = '\n\n'.join(report)
    return full


if __name__ == '__main__':
    people = [
        ('/tmp/weiqiling_ds.json', '魏启令', '01-家主-魏启令'),
        ('/tmp/cheng_ds.json', '主母成', '02-主母-成'),
        ('/tmp/ziyuan_ds.json', '子源', '03-少爷-子源'),
    ]
    for ds_path, label, subdir in people:
        out = f'/tmp/{label}_盲派_财富事业学业_v3.md'
        report = generate(ds_path, label)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(report)
        lc, cc = len(report.splitlines()), len(report)
        print(f'{label}: {lc}行 {cc}字')
        
        kb = f'/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/{subdir}/{label}_盲派_财富事业学业.md'
        with open(kb, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f'  -> {kb}')
