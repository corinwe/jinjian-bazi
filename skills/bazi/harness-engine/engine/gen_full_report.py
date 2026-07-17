#!/usr/bin/env python3
"""
gen_full_report.py — 完整21§盲派报告生成器（Harness Engine正式模块）
从 rules_mangpai/ 加载规则，生成标准格式报告
"""
import json, os, sys, datetime, yaml
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

HARNESS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_DIR = os.path.join(HARNESS_DIR, 'rules_mangpai')

WX_M = {'庚':'金','辛':'金','甲':'木','乙':'木','壬':'水','癸':'水','丙':'火','丁':'火','戊':'土','己':'土'}
TODAY = datetime.date.today().strftime('%Y%m%d')
ZANGFU = {'木':'肝/胆','火':'心/小肠','土':'脾/胃','金':'肺/大肠','水':'肾/膀胱'}

def load_rule(name):
    p = os.path.join(RULES_DIR, name)
    if os.path.exists(p):
        with open(p, encoding='utf-8') as f:
            return yaml.safe_load(f).get('rule', {})
    return {}

def calc_ti_yong(ds):
    ti = int(ds['身强弱']['总分']); yong = max(100 - ti, 1); return ti, yong, ti / yong

def gen(ds_path, label):
    ds = json.load(open(ds_path))
    ti, yong, bi = calc_ti_yong(ds)
    shen_lv = ds['身强弱']['等级']
    ss = ds['十神']; G = [ds['年干'],ds['月干'],ds['日干'],ds['时干']]
    Z = [ds['年支'],ds['月支'],ds['日支'],ds['时支']]
    r = ds['日主']; w = ds['日主五行']
    
    # 加载规则
    hunyin_r = load_rule('hun_yin_he_xin.yaml')
    zinv_r = load_rule('zi_nv.yaml')
    sanjue_r = load_rule('san_jue_duan.yaml')
    
    lines = []; a = lines.append
    
    # §1 一页总览
    a('# 盲派命理完整报告 — ' + label)
    a('生成日期：' + TODAY)
    a('八字：' + ds['八字'])
    a('日主：' + r + w + ' | 身强弱：' + str(int(ds['身强弱']['总分'])) + '分' + shen_lv)
    a('体用比：体' + str(ti) + '分，用' + str(yong) + '分，' + f'{bi:.1f}:1')
    a('起运年龄：' + str(ds.get('起运年龄','?')) + '岁')
    a('大运：' + ' '.join([y['干支'] for y in ds['大运']]))
    a('空亡：' + ds.get('空亡','?') + ' 纳音：' + ' '.join(ds['纳音'].values()))
    a('')
    
    # §2 格局分析
    m_cang = ds['藏干十神'].get('月支',[])
    cang_text = ' '.join([c['天干']+'('+c['十神']+')' for c in m_cang])
    a('## 格局分析')
    a('生于' + Z[1] + '月，月令藏干：' + cang_text + '。')
    a('月干' + ss.get('月','?') + '，对日主' + r + '形成主要影响。')
    if bi > 1.5: a('体占明显优势。人生靠自身能力拼搏。')
    elif bi > 0.7: a('体用均衡。靠自身也借外部资源。')
    else: a('用占优势。顺势而为，平台比能力重要。')
    a('宾主：年柱祖上/早年、月柱父母/环境、日柱自身/中年、时柱子/晚年。')
    a('')
    
    # §3 身强弱
    a('## 身强弱分析')
    a('得分：' + str(int(ds['身强弱']['总分'])) + '分 — ' + shen_lv)
    if '身强' in shen_lv: a('身强。喜克泄耗（木火水），忌生扶（土金）。')
    elif '从弱' in shen_lv: a('从弱。顺势而为，喜克泄耗忌生扶。')
    elif '中和' in shen_lv: a('中和。喜忌随大运变化。')
    a('')
    
    # §4 喜用神
    a('## 喜用神')
    if '身强' in shen_lv: a('喜用：木(财)、火(官杀)、水(食伤)。忌：土(印)、金(比劫)。')
    elif '从弱' in shen_lv: a('喜用：木(财)、火(官杀)。忌：土(印)、金(比劫)。')
    elif '中和' in shen_lv: a('喜用随大运。好运积极，差运保守。')
    a('')
    
    # §5 灾祸疾病
    a('## 灾祸疾病')
    wuxing_count = {}
    for g in G: wuxing_count[WX_M.get(g,'')] = wuxing_count.get(WX_M.get(g,''),0) + 1
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk,[]):
            wuxing_count[WX_M.get(c['天干'],'')] = wuxing_count.get(WX_M.get(c['天干'],''),0) + 0.6
    for wx, cnt in wuxing_count.items():
        if cnt >= 3: a('⚠ ' + wx + '五行过三(' + f'{cnt:.1f}' + '次)→注意' + ZANGFU.get(wx,wx) + '保养。')
    for zk in ['月支','日支']:
        for c in ds['藏干十神'].get(zk,[]):
            if c['十神'] == '七杀': a('⚠ 七杀在' + zk + '→注意' + ZANGFU.get(WX_M.get(c['天干'],""),w) + '。')
    a('')
    
    # §6 性格
    a('## 性格分析（盲派）')
    nei = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    xg = {'正官':'守规矩','七杀':'有魄力','正印':'温和','偏印':'聪明','正财':'务实','偏财':'灵活','食神':'友善','伤官':'才华','比肩':'独立','劫财':'好胜'}
    a('外在(月干' + ss.get('月','?') + ')：' + xg.get(ss.get('月',''),''))
    a('内在(日支' + nei + ')：' + xg.get(nei,''))
    a('社交(年干' + ss.get('年','?') + ')：' + xg.get(ss.get('年',''),''))
    a('晚年(时干' + ss.get('时','?') + ')：' + xg.get(ss.get('时',''),''))
    a('')
    
    # §7 外貌
    wx_body = {'金':'骨骼挺拔肤白','木':'修长清秀','水':'圆润柔和','火':'中等身材面色好','土':'敦实肤偏黄'}
    a('## 身材外貌')
    a('日主' + r + w + '属' + WX_M.get(r,'') + '性，' + wx_body.get(WX_M.get(r,''),'') + '。')
    a('')
    
    # §8 财富
    cai_items = []
    for pos, lb in [('年','年'),('月','月'),('时','时')]:
        if ss.get(pos,'') in ['正财','偏财']: cai_items.append((lb + '干', ds[lb + '干'], ss[pos]))
    for zk in ['年支','月支','日支','时支']:
        for c in ds['藏干十神'].get(zk,[]):
            if c['十神'] in ['正财','偏财']: cai_items.append((zk, c['天干'], c['十神']))
    cai_cnt = len(cai_items)
    a('## 财富分析')
    a('### 财星分布')
    for p,t,s in cai_items: a('| ' + p + ' | ' + t + ' | ' + s + ' |')
    if not cai_items: a('| 财星不显 |')
    a('### 财富路线')
    for p,t,s in cai_items:
        if '年' in p: a(p + t + '→祖业/早年财源')
        elif '月' in p: a(p + t + '→青年17-32岁财运')
        elif '日' in p: a(p + t + '→中年33-48岁关键期')
        elif '时' in p: a(p + t + '→晚年49-64岁财')
    a('### 财富等级')
    cai_info = {'grade_high':'7-8级高等级财富','grade_mid':'5-6级中高财富','grade_low':'1-2级财不显'}
    if ti >= 60 and cai_cnt >= 3: a('体' + str(ti) + '分财' + str(cai_cnt) + '颗→' + cai_info['grade_high'])
    elif ti >= 60 and cai_cnt >= 1: a('体' + str(ti) + '分财' + str(cai_cnt) + '颗→' + cai_info['grade_mid'])
    elif cai_cnt >= 3: a('体' + str(ti) + '分财' + str(cai_cnt) + '颗→机会型财富')
    else: a('体' + str(ti) + '分财' + str(cai_cnt) + '颗→' + cai_info['grade_low'])
    a('### 发财关键年份')
    for y in ds['大运']:
        if WX_M.get(y['干支'][0],'') in '木水':
            a('  ' + y['干支'] + '运(' + str(int(y['起始年龄'])) + '-' + str(int(y['终止年龄'])) + '岁): 财运窗口')
    a('')
    
    # §9 置业
    a('## 置业买房')
    a('宜选楼层尾数：3、8、2、7、1、6。忌选：4、9、5、0。')
    a('宜选朝向：东南(木)、南(火)、北(水)。')
    a('')
    
    # §10 事业
    a('## 事业分析')
    ms = ss.get('月','?')
    rs = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    if ms in ['食神','伤官']: a('月干' + ms + '→靠才华技术立身。适合创作/咨询/技术/教育类。')
    elif ms in ['正官','七杀']: a('月干' + ms + '→事业心强。适合管理/体制内。')
    elif ms in ['正印','偏印']: a('月干' + ms + '→喜学习重积累。适合研究/学术/工程。')
    elif '财' in str(ms): a('月干' + ms + '→务实重利。适合商贸/金融。')
    elif ms in ['比肩','劫财']: a('月干' + ms + '→竞争意识。适合销售/市场。')
    a('日支' + rs + '为内在驱动力。')
    gs = sum([2 if ('官' in ss.get('月','') or '杀' in ss.get('月','')) else 0, 1 if '官' in str(ds['藏干十神']['日支']) else 0])
    ss2 = 3.0 if '身强' in shen_lv else 2.0
    gy = sum(1 for y in ds['大运'] if WX_M.get(y['干支'][0],'') in '火')
    gys = 2.0 if gy >= 2 else (1.0 if gy >= 1 else 0.0)
    t2 = gs + ss2 + gys
    a('事业等级：' + f'{t2:.1f}' + '/10，' + ('高层' if t2 >= 7 else '中层' if t2 >= 5 else '基层') + '。')
    a('### 升官关键年份')
    for y in ds['大运']:
        if WX_M.get(y['干支'][0],'') in '火': a('  ' + y['干支'] + '运(' + str(int(y['起始年龄'])) + '-' + str(int(y['终止年龄'])) + '岁): 官杀透干期')
    a('')
    
    # §11 学业
    a('## 学业分析')
    wen = ds.get('神煞',{}).get('文昌贵人','未找到')
    zhi_pos = [ds.get(k,'') for k in ['年支','月支','日支','时支']]
    a('文昌贵人：' + wen)
    for i, label in enumerate(['年','月','日','时']):
        if wen in zhi_pos[i]:
            a('在' + label + '柱。' + ('早年学习力强' if label in '年月' else '中年后学习力更佳') + '。'); break
    else: a('不在四柱，需大运引出。')
    if '身强' in shen_lv: a('身强不喜印。18岁前走印运不利学业。')
    elif '从弱' in shen_lv: a('从弱喜印。18岁前走印运学业顺。')
    elif '中和' in shen_lv: a('中和格局，学业看大运。')
    yun18 = [y for y in ds['大运'] if int(y['起始年龄']) < 18]
    a('18岁前大运：' + ' '.join([y['干支'] + '运(' + str(int(y['起始年龄'])) + '-' + str(int(y['终止年龄'])) + '岁)' for y in yun18]))
    fw_map = {'子':'北','丑':'东北','寅':'东北','卯':'东','辰':'东南','巳':'东南','午':'南','未':'西南','申':'西南','酉':'西','戌':'西北','亥':'西北'}
    a('补文昌：书房宜' + fw_map.get(wen,'') + '向。')
    a('')
    
    # §12 婚姻（从规则加载）
    a('## 婚姻分析')
    ri_zhi = Z[2]; ri_ss = ds['藏干十神'].get('日支',[{}])[0].get('十神','?')
    a('配偶宫（日支' + ri_zhi + '）：' + ri_ss + '。')
    gong_m = hunyin_r.get('gong_meaning',{})
    a(gong_m.get(ri_ss, ''))
    for i, l in enumerate(['年','月','日','时']):
        if l == '日': continue
        if Z[i] == {'亥':'卯','卯':'戌','戌':'卯','申':'巳','巳':'申','寅':'亥','子':'丑','丑':'子','午':'未','未':'午','辰':'酉','酉':'辰'}.get(Z[2],''):
            a('绊禄桃花：日支' + Z[2] + '与' + l + '支' + Z[i] + '相合→' + ('内向合熟人' if i == 3 else '常规合') + '。'); break
    else: a('绊禄桃花：四柱无合，不显。')
    a('')
    
    # §13 子女（从规则加载）
    a('## 子女分析')
    a('时柱' + Z[3] + G[3] + '：时干' + ss.get('时','?') + '，时支' + ds['藏干十神'].get('时支',[{}])[0].get('十神','?') + '。')
    for c in ds['藏干十神'].get('时支',[]):
        z_m = zinv_r.get('shi_zhi_meaning',{})
        if c['十神'] in z_m: a('  ' + c['天干'] + '(' + c['十神'] + ')→' + z_m.get(c['十神'],''))
    s_m = zinv_r.get('shi_gan_meaning',{})
    if ss.get('时','') in s_m: a('时干' + ss.get('时','') + '→' + s_m.get(ss.get('时',''),''))
    a(zinv_r.get('jie_zi_kan_fu',''))
    a('')
    
    # §14 健康
    a('## 健康分析')
    for wx, cnt in wuxing_count.items():
        zf = ZANGFU.get(wx,'?')
        if cnt >= 2.5: a(zf + '(' + wx + ')：⚠ 偏旺需注意。')
        elif cnt <= 0.5: a(zf + '(' + wx + ')：⚠ 不足需补充。')
        else: a(zf + '(' + wx + ')：正常')
    a('')
    
    # §15 六亲
    a('## 六亲分析')
    a('年柱' + ss.get('年','?') + '→祖上/父辈。')
    a('月柱' + ss.get('月','?') + '→父母/兄弟。月令为母位。')
    a('日柱→自身和配偶。日支为配偶宫。')
    a('时柱' + ss.get('时','?') + '→子女。')
    for i, (g, z) in enumerate(zip(G, Z)):
        label = ['年','月','日','时'][i]
        if WX_M.get(g,'') == WX_M.get(r,''): a(label + '柱' + g + z + '五行与日主同→性格相近。')
        elif WX_M.get(r,'') in {'木':'火','火':'土','土':'金','金':'水','水':'木'}.get(WX_M.get(g,''),''):
            a(label + '柱' + g + z + '生扶日主→有帮助。')
        else: a(label + '柱' + g + z + '克耗日主→关系有张力。')
    a('')
    
    # §15b 人生关键事件表
    a('## 人生关键事件表')
    a('| 年龄 | 年份 | 事件类型 | 说明 |')
    a('|:----|:----:|:--------|:-----|')
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        age = str(int(y['起始年龄'])) + '-' + str(int(y['终止年龄']))
        yr = str(int(y['起始年份'])) + '-' + str(int(y['终止年份']))
        if dw == '木': a('| ' + age + ' | ' + yr + ' | 💰 财富期 | 财星透干吉 |')
        elif dw == '火': a('| ' + age + ' | ' + yr + ' | 📈 事业期 | 官杀透干吉 |')
        elif dw == '水': a('| ' + age + ' | ' + yr + ' | 💡 才华期 | 食伤运好 |')
        elif dw == '金': a('| ' + age + ' | ' + yr + ' | 🔄 竞争期 | 比劫运注意 |')
        elif dw == '土': a('| ' + age + ' | ' + yr + ' | 📚 沉淀期 | 印运积累好 |')
    a('')
    
    # §16 事件总表
    a('## 事件总表')
    a('| 大运 | 年龄 | 年份 | 判运 |')
    a('|:----|:----:|:----:|:----:|')
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        pan = '吉' if dw in '木火' else ('平' if dw in '水土' else '忌')
        a('| ' + y['干支'] + ' | ' + str(int(y['起始年龄'])) + '-' + str(int(y['终止年龄'])) + ' | ' + str(int(y['起始年份'])) + '-' + str(int(y['终止年份'])) + ' | ' + pan + ' |')
    a('')
    
    # §17 大运精析
    a('## 大运精析')
    for y in ds['大运']:
        dw = WX_M.get(y['干支'][0],'')
        age = str(int(y['起始年龄'])) + '-' + str(int(y['终止年龄']))
        if dw == '火': a(y['干支'] + '运(' + age + '岁): 官杀运→事业关键期，压力即动力。')
        elif dw == '木': a(y['干支'] + '运(' + age + '岁): 财运→财富积累期。')
        elif dw == '水': a(y['干支'] + '运(' + age + '岁): 食伤运→才华展现期。')
        elif dw == '土': a(y['干支'] + '运(' + age + '岁): 印运→学习沉淀期。')
        else: a(y['干支'] + '运(' + age + '岁): 比劫运→竞争加剧期。')
    a('')
    
    # §18 三决断（从规则加载）
    a('## 三决断')
    sj = sanjue_r.get('shen_jue',{})
    if '身强' in shen_lv: a('一决身：身强。' + sj.get('身强',''))
    elif '从弱' in shen_lv: a('一决身：从弱。' + sj.get('从弱',''))
    elif '中和' in shen_lv: a('一决身：中和。' + sj.get('中和',''))
    a('二决财：共' + str(cai_cnt) + '颗财星。')
    if ti >= 60 and cai_cnt >= 3: a('  → ' + sanjue_r.get('cai_jue',{}).get('grade_high',''))
    elif ti >= 60 and cai_cnt >= 1: a('  → 中高财富。体旺能担财。')
    elif cai_cnt >= 3: a('  → 中等财富，机会型。')
    else: a('  → 财不显，宜专技发展。')
    a('三决官：官杀分' + str(gs) + '。')
    if gs >= 4: a('  → ' + sanjue_r.get('guan_jue',{}).get('high',''))
    elif gs >= 2: a('  → ' + sanjue_r.get('guan_jue',{}).get('mid',''))
    else: a('  → ' + sanjue_r.get('guan_jue',{}).get('low',''))
    a('')
    
    # §19 运程总评
    a('## 运程总评（一生定性）')
    for period, yuns, name in [('少年青年', [y for y in ds['大运'] if int(y['起始年龄']) < 30], '1-30'),
                                ('中年', [y for y in ds['大运'] if 30 <= int(y['起始年龄']) < 60], '30-60'),
                                ('晚年', [y for y in ds['大运'] if int(y['起始年龄']) >= 60], '60+')]:
        good = sum(1 for y in yuns if WX_M.get(y['干支'][0],'') in '木火')
        bad = sum(1 for y in yuns if WX_M.get(y['干支'][0],'') in '金')
        if good > bad: a(name + '岁(' + period + '): 好运为主，积极进取。')
        elif good == bad: a(name + '岁(' + period + '): 好坏参半，稳中求进。')
        else: a(name + '岁(' + period + '): 挑战较多，保守经营。')
    a('')
    
    # §20 五行补充
    a('## 五行补充')
    wx_color = {'木':'绿/青','火':'红/紫','土':'黄/咖','金':'白/银','水':'黑/蓝'}
    for wx, cnt in wuxing_count.items():
        if cnt <= 1: a(wx + '不足。宜' + wx_color.get(wx,'') + '色系列补充。')
    a('')
    
    # §21 人生建议
    a('## 人生建议')
    if '身强' in shen_lv: a('身强可攻。事业大胆拼搏，财富主动求取。注意人际。')
    elif '从弱' in shen_lv: a('从弱顺势。选对平台跟对人，借力使力。')
    elif '中和' in shen_lv: a('中和平衡。好运攻差运守，能屈能伸。')
    a('命理珍宝·六冲七型：逢中先辨七型，非概凶。')
    a('命理珍宝·忌神三制：弱忌彻底制，强忌弱制。')
    
    return '\n'.join(lines)


if __name__ == '__main__':
    for dp, label, sd in [
        ('/tmp/weiqiling_ds.json', '魏启令', '01-家主-魏启令'),
        ('/tmp/cheng_ds.json', '主母成', '02-主母-成'),
        ('/tmp/ziyuan_ds.json', '子源', '03-少爷-子源'),
    ]:
        report = gen(dp, label)
        kb = '/root/weiwuji-knowledge-base/07-国学哲学/八字命格/02-人物档案/' + sd + '/' + label + '_盲派完整报告_含命理珍宝_' + TODAY + '.md'
        with open(kb, 'w', encoding='utf-8') as f:
            f.write(report)
        lc = len(report.splitlines())
        cc = len(report)
        print(label + ': ' + str(lc) + '行 ' + str(cc) + '字')
