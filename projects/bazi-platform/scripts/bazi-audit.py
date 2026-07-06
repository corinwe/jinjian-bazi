#!/usr/bin/env python3
"""
金鉴真人·八字全面审计脚本 v1.0
2026-06-24新增·老板令

审计范围：学业·财富·事业维度
审计内容：原局+喜用忌神+大运不利因素在关键时期的影响

用法：python3 bazi-audit.py <引擎JSON路径>
      读取引擎JSON后自动输出审计报告

集成到：git hook / bazi-pipeline.sh --audit
"""

import json
import sys
import re

WUXING = {'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
SHENG_WO = {'金':'土','木':'水','水':'金','火':'木','土':'火'}  # 生我者为印
KE_WO = {'金':'火','木':'金','水':'土','火':'水','土':'木'}  # 克我者为官杀
WO_KE = {'金':'木','木':'土','水':'火','火':'金','土':'水'}  # 我克者为财
WENCHANG = {'甲':'巳','乙':'午','丙':'申','丁':'酉','戊':'申','己':'酉','庚':'亥','辛':'子','壬':'寅','癸':'卯'}

KONGWANG = {
    '甲子':'戌亥','乙丑':'戌亥','丙寅':'戌亥','丁卯':'戌亥','戊辰':'戌亥','己巳':'戌亥','庚午':'戌亥','辛未':'戌亥','壬申':'戌亥','癸酉':'戌亥',
    '甲戌':'申酉','乙亥':'申酉','丙子':'申酉','丁丑':'申酉','戊寅':'申酉','己卯':'申酉','庚辰':'申酉','辛巳':'申酉','壬午':'申酉','癸未':'申酉',
    '甲申':'午未','乙酉':'午未','丙戌':'午未','丁亥':'午未','戊子':'午未','己丑':'午未','庚寅':'午未','辛卯':'午未','壬辰':'午未','癸巳':'午未',
    '甲午':'辰巳','乙未':'辰巳','丙申':'辰巳','丁酉':'辰巳','戊戌':'辰巳','己亥':'辰巳','庚子':'辰巳','辛丑':'辰巳','壬寅':'辰巳','癸卯':'辰巳',
    '甲辰':'寅卯','乙巳':'寅卯','丙午':'寅卯','丁未':'寅卯','戊申':'寅卯','己酉':'寅卯','庚戌':'寅卯','辛亥':'寅卯','壬子':'寅卯','癸丑':'寅卯',
    '甲寅':'子丑','乙卯':'子丑','丙辰':'子丑','丁巳':'子丑','戊午':'子丑','己未':'子丑','庚申':'子丑','辛酉':'子丑','壬戌':'子丑','癸亥':'子丑',
}

def load_engine(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_education_audit(data):
    """学历审计：检查文昌+大运窗口"""
    name = data.get('姓名','?')
    bazi = [data['四柱']['年柱'], data['四柱']['月柱'], data['四柱']['日柱'], data['四柱']['时柱']]
    rizhu = data['四柱']['日柱'][0]
    ri_wx = WUXING[rizhu]
    score = data['身强弱']['总分']
    level = data['身强弱']['等级']
    year_gan = bazi[0][0]
    qiyun_age = data['大运']['起运年龄']
    
    issues = []
    
    # 文昌检查
    wen = WENCHANG.get(year_gan, '?')
    wen_present = any(wen in zhi for zhi in [b[1] for b in bazi])
    if not wen_present:
        issues.append(f"⚠️ 文昌缺失(年干{year_gan}→文昌{wen}不在原局)")
    
    # 年干伤官检查（2026-06-24新增·杨昌玉案例）
    year_gan_ss = data['十神']['年干']
    if year_gan_ss == '伤官':
        issues.append(f"❌ 年干{year_gan}={year_gan_ss}→最强烈的负向学业信号(叛逆、不安分)")
        if not wen_present:
            issues.append("⚠️ 年干伤官+文昌缺失→学历低(上限高中/职校)")
    
    # 格局导向检查
    shi_gan_ss = data['十神']['时干']
    yue_gan_ss = data['十神']['月干']
    if (yue_gan_ss in ['食神','伤官'] and shi_gan_ss in ['正财','偏财']) or \
       (shi_gan_ss in ['食神','伤官'] and yue_gan_ss in ['正财','偏财']):
        issues.append("⚠️ 食伤生财格→赚钱导向>读书")
    
    # 伤官见官检查
    for dy in data['大运']['序列'][:2]:
        zheng_guan = {'甲':'辛','乙':'庚','丙':'癸','丁':'壬','戊':'乙','己':'甲','庚':'丁','辛':'丙','壬':'己','癸':'戊'}
        if year_gan_ss == '伤官' and dy['干支'][0] == zheng_guan.get(rizhu, ''):
            issues.append(f"⚠️ 年干伤官+{dy['干支']}运正官=伤官见官→叛逆加剧")
    
    # 印运在18岁前检查
    # 第一步大运的年份范围
    first_dy = data['大运']['序列'][0]
    first_gan_wx = WUXING.get(first_dy['干支'][0], '?')
    yin_wx = SHENG_WO[ri_wx]
    if first_gan_wx == yin_wx:
        issues.append("✅ 第一步大运为印运(18岁前有印)")
    else:
        issues.append(f"⚠️ 第一步大运{first_dy['干支']}非印运(18岁前缺印)")
    
    # 结论
    edu_result = "✅ 学历正常"
    if not wen_present and first_gan_wx != yin_wx:
        edu_result = "⚠️ 文昌缺失+印运未在18岁前到位 → 学历上限不超过本科"
    
    return edu_result, issues

def check_wealth_audit(data):
    """财富审计：检查大运对财星的不利因素"""
    rizhu = data['四柱']['日柱'][0]
    ri_wx = WUXING[rizhu]
    score = data['身强弱']['总分']
    level = data['身强弱']['等级']
    cai_wx = WO_KE[ri_wx]  # 财星五行
    
    issues = []
    
    # 检查大运是否在某段关键时期克财星
    for dy in data['大运']['序列']:
        ganzhi = dy['干支']
        start_year = dy['起始年份']
        end_year = dy['终止年份']
        start_age = dy['起始年龄']
        end_age = dy['终止年龄']
        
        # 大运天干和地支的五行
        gan_wx = WUXING.get(ganzhi[0], '?')
        
        # 大运天干克财星？→破财大运
        # 克财星的五行 = 生财星的五行...不，克财星的五行
        # 财星五行被克的五行：木被金克，土被木克，火被水克，金被火克，水被土克
        ke_cai = {'木':'金','土':'木','火':'水','金':'火','水':'土'}
        if cai_wx in ke_cai and gan_wx == ke_cai[cai_wx]:
            issues.append(f"⚠️ {ganzhi}运({int(start_year)}~{int(end_year)})天干{ganzhi[0]}克财星{get_cai_name(cai_wx)}→破财信号")
        
        # 身弱+财星大运=破财（身弱不担财）
        if score < 40 and gan_wx == cai_wx:
            issues.append(f"⚠️ 身弱({score}分)+{ganzhi}运天干{ganzhi[0]}(财星)→身弱不担财，遇财反破")
    
    if not issues:
        issues.append("✅ 大运无直接克财星因素")
    
    return issues

def check_career_audit(data):
    """事业审计：基于原始素材21（恶神制化）+素材02（十神应用）"""
    rizhu = data['四柱']['日柱'][0]
    ri_wx = WUXING[rizhu]
    score = data['身强弱']['总分']
    level = data['身强弱']['等级']
    
    issues = []
    
    # 获取所有天干的十神
    all_ss = [data['十神']['年干'], data['十神']['月干'], data['十神']['时干']]
    has_qisha = '七杀' in all_ss
    has_yin = '正印' in all_ss or '偏印' in all_ss
    has_shishen = '食神' in all_ss or '伤官' in all_ss
    
    # 检查杀印相生格（素材21行53「身弱杀印相生，收七杀为己所用」）
    if has_qisha and has_yin and score < 40:
        issues.append("⚠️ 杀印相生格+身弱→借平台/贵人/专业发展，不适合单干创业（素材21行53）")
    
    # 检查食神制杀格（素材21行85「身强用食神去制杀」）
    if has_qisha and has_shishen and score >= 60:
        issues.append("✅ 食神制杀格+身强→领袖气质（素材21行85）")
    
    # 检查七杀无制（素材21行189「七杀无制就是灾祸产生的时候」）
    if has_qisha and not has_yin and not has_shishen:
        issues.append("⚠️ 七杀无制→灾祸信号，需大运流年补印或食神化解（素材21行189）")
    
    # 大运官杀对身弱者的压力
    for dy in data['大运']['序列'][:4]:  # 前4步（关键事业期）
        ganzhi = dy['干支']
        gan_wx = WUXING.get(ganzhi[0], '?')
        guan_wx = KE_WO[ri_wx]
        
        if score < 40 and gan_wx == guan_wx:
            issues.append(f"⚠️ 身弱({score}分)+{ganzhi}运天干{ganzhi[0]}(官杀)→压力大需印比支持")
    
    # 格局导向检查（素材02行49）
    yue_gan_ss = data['十神']['月干']
    yue_zhi_ss_tou = data.get('格局','未定')
    
    if not issues:
        issues.append("✅ 事业大运无异常风险")
    
    return issues

def get_cai_name(cai_wx):
    names = {'木':'木(财)','火':'火(财)','土':'土(财)','金':'金(财)','水':'水(财)'}
    return names.get(cai_wx, '?')

def main():
    if len(sys.argv) < 2:
        print("用法: python3 bazi-audit.py <引擎JSON路径> [姓名]")
        sys.exit(1)
    
    path = sys.argv[1]
    data = load_engine(path)
    name = sys.argv[2] if len(sys.argv) > 2 else data.get('姓名','?')
    
    rizhu = data['四柱']['日柱'][0]
    bazi_str = f"{data['四柱']['年柱']} {data['四柱']['月柱']} {data['四柱']['日柱']} {data['四柱']['时柱']}"
    score = data['身强弱']['总分']
    level = data['身强弱']['等级']
    
    print(f"{'='*60}")
    print(f"  金鉴真人·八字全面审计 v1.0")
    print(f"  命主: {name}")
    print(f"  八字: {bazi_str}")
    print(f"  日主: {rizhu} | 身{score}分({level})")
    print(f"{'='*60}")
    
    print(f"\n{'─'*60}")
    print(f"  【学历维度审计】")
    print(f"{'─'*60}")
    edu_result, edu_issues = check_education_audit(data)
    for i in edu_issues:
        print(f"  {i}")
    print(f"\n  → {edu_result}")
    
    print(f"\n{'─'*60}")
    print(f"  【财富维度审计】")
    print(f"{'─'*60}")
    wealth_issues = check_wealth_audit(data)
    for i in wealth_issues:
        print(f"  {i}")
    
    print(f"\n{'─'*60}")
    print(f"  【事业维度审计】")
    print(f"{'─'*60}")
    career_issues = check_career_audit(data)
    for i in career_issues:
        print(f"  {i}")
    
    # 综合：检查是否有任何alert
    all_issues = [i for i in edu_issues + wealth_issues + career_issues if '⚠️' in i]
    
    print(f"\n{'─'*60}")
    if all_issues:
        print(f"  ⚠️ 发现 {len(all_issues)} 个潜在问题")
        sys.exit(1)
    else:
        print(f"  ✅ 全部维度审计通过")
        sys.exit(0)

if __name__ == '__main__':
    main()
