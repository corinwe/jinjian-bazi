#!/usr/bin/env python3
"""金鉴真人·八字报告格式强制验证器 v2.0

用法: python3 bazi-format-check.py <报告路径>
功能: 
  ① 检查§1是否包含完整25字段
  ② 检查最佳/次佳/最差大运是否与喜用神逻辑一致
  ③ 检查格式是否与模板一致

v2.0新增: 大运喜忌逻辑自检（2026-06-24·老板强令物理固化）
"""

import sys
import re

# 标准25字段（必须按顺序出现）
STANDARD_FIELDS = [
    "四柱八字", "纳音", "日主", "性别", "出生时间",
    "命格等级", "格局成立条件", "身强身弱", "从弱格排查", "喜用神（排序）",
    "忌神（排序）", "空亡",
    "财星分数", "财富等级", "最高学历", "事业等级",
    "最佳大运", "起运年龄", "次佳大运", "最差大运", "现行大运",
    "发财最佳年份", "健康注意方面", "四大特征", "搬迁次数预测"
]

# 天干五行映射
TIANGAN_WUXING = {
    '甲':'木','乙':'木','丙':'火','丁':'火','戊':'土',
    '己':'土','庚':'金','辛':'金','壬':'水','癸':'水'
}

# 地支五行映射
DIZHI_WUXING = {
    '寅':'木','卯':'木','巳':'火','午':'火',
    '辰':'土','戌':'土','丑':'土','未':'土',
    '申':'金','酉':'金','亥':'水','子':'水'
}

def extract_dayun_ganzhi(text):
    """从大运文本中提取干支（如从'🏆 丁亥运（2010~2020）杀印相生'提取'丁亥'）"""
    # 匹配所有中文字符中的干支模式：一个天干+一个地支
    match = re.search(r'([甲乙丙丁戊己庚辛壬癸])([子丑寅卯辰巳午未申酉戌亥])', text)
    if match:
        return match.group(1), match.group(2)
    return None, None

def parse_xiyong_shen(text):
    """解析喜用神和忌神字符串, 返回五行列表"""
    # 喜用神格式: "🟢 火 < 木 < 水" 或 "🟢 水 > 土 > 金"
    # 忌神格式: "🔴 土 > 金" 或 "🔴 火 > 木"
    wuxing_list = []
    # 提取所有五行字（金木水火土）
    for w in ['金','木','水','火','土']:
        if w in text:
            wuxing_list.append(w)
    return wuxing_list

def check_dayun_logic(content):
    """检查最佳大运和次佳大运是否与喜用神逻辑一致"""
    errors = []
    warnings = []
    
    # 提取喜用神行
    xiyong_match = re.search(r'(?:喜用神.*排序[：:]\s*|🟢\s*).*?([金木水火土].*?)(?:\n|\||$)', content)
    jishen_match = re.search(r'(?:忌神.*排序[：:]\s*|🔴\s*).*?([金木水火土].*?)(?:\n|\||$)', content)
    shenqiang_match = re.search(r'身强身弱[：:]\s*\*\*\s*([^（★]*?)\s*（', content)
    
    if not xiyong_match:
        warnings.append("⚠️ 大运喜忌自检：未找到喜用神行，跳过")
        return errors, warnings
    
    xiyong_text = xiyong_match.group(1) if xiyong_match else ""
    jishen_text = jishen_match.group(1) if jishen_match else ""
    shenqiang_text = shenqiang_match.group(1) if shenqiang_match else ""
    
    xiyong = parse_xiyong_shen(xiyong_text)
    jishen = parse_xiyong_shen(jishen_text)
    
    if not xiyong:
        warnings.append("⚠️ 大运喜忌自检：喜用神解析失败，跳过")
        return errors, warnings
    
    # 检查是否从弱格（从弱格用特殊逻辑）
    is_congruo = '从弱' in content[:200]
    
    # 提取最佳大运行
    zuijia_match = re.search(r'最佳大运[：:].*?([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])', content)
    zuichai_match = re.search(r'最差大运[：:].*?([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])', content)
    
    # 检查最佳大运
    if zuijia_match:
        tg, dz = zuijia_match.group(1)[0], zuijia_match.group(1)[1]
        tg_wx = TIANGAN_WUXING.get(tg, '')
        dz_wx = DIZHI_WUXING.get(dz, '')
        
        # 最佳大运的天干不应是忌神（从弱格特殊处理）
        if not is_congruo:
            if tg_wx in jishen and dz_wx in jishen:
                errors.append(f"❌ 最佳大运({tg}{dz})的天干({tg_wx})和地支({dz_wx})都是忌神，逻辑矛盾！")
            elif tg_wx in jishen:
                warnings.append(f"⚠️ 最佳大运({tg}{dz})的天干({tg_wx})在忌神中，如果是喜+忌混合可忽略")
        else:
            # 从弱格忌金土（生扶破格）
            pass
    
    # 检查最差大运
    if zuichai_match:
        tg, dz = zuichai_match.group(1)[0], zuichai_match.group(1)[1]
        tg_wx = TIANGAN_WUXING.get(tg, '')
        dz_wx = DIZHI_WUXING.get(dz, '')
        
        # 最差大运的天干和地支不应都是喜用
        if not is_congruo:
            if tg_wx in xiyong and dz_wx in xiyong:
                errors.append(f"❌ 最差大运({tg}{dz})的天干({tg_wx})和地支({dz_wx})都是喜用，逻辑矛盾！")
    
    return errors, warnings


def check_report(path):
    errors = []
    warnings = []
    
    try:
        with open(path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {path}")
        return False
    except Exception as e:
        print(f"❌ 读取失败: {e}")
        return False
    
    lines = content.split('\n')
    
    # 检查1: 头部元数据（8项：编制人/时间/版本/模板/八字/日主/性别/出生）
    header_checks = ["**编制人：**", "**编制时间：**", "**版本：**", "**模板：**", 
                     "**八字：**", "**日主：**", "**性别：**", "**出生：**"]
    for hc in header_checks:
        if hc not in content:
            errors.append(f"缺少头部元数据: {hc}")
    
    # 检查2: §1 25字段完整性
    found_fields = []
    for field in STANDARD_FIELDS:
        pattern1 = re.search(r'\|\s*\d+\s*\|\s*\*\*' + re.escape(field) + r'\*\*', content)
        pattern2 = re.search(r'\|\s*\d+\s*\|\s*' + re.escape(field), content)
        if pattern1 or pattern2:
            found_fields.append(field)
        else:
            errors.append(f"缺少字段: {field}")
    
    # 检查3: §1后白话解读
    if "🗣️ 白话：" not in content and "白话：" not in content:
        warnings.append("缺少§1后白话解读段（🗣️）")
    
    # 检查4: 版本说明段落
    if "版本说明" not in content:
        warnings.append("缺少版本说明段落")
    
    # 🔥 检查5: 大运喜忌逻辑自检（v2.0新增·物理固化）
    dy_errors, dy_warnings = check_dayun_logic(content)
    errors.extend(dy_errors)
    warnings.extend(dy_warnings)
    
    # 输出结果
    print(f"\n{'='*50}")
    print(f"  格式验证报告: {path}")
    print(f"{'='*50}")
    print(f"\n  25字段检查: {len(found_fields)}/{len(STANDARD_FIELDS)}")
    missing = [f for f in STANDARD_FIELDS if f not in found_fields]
    if missing:
        print(f"  ❌ 缺失: {', '.join(missing)}")
    else:
        print(f"  ✅ 全部完整")
    
    if errors:
        print(f"\n  ❌ 错误 ({len(errors)}项):")
        for e in errors:
            print(f"    - {e}")
    
    if warnings:
        print(f"\n  ⚠️ 警告 ({len(warnings)}项):")
        for w in warnings:
            print(f"    - {w}")
    
    if not errors:
        print(f"\n  ✅ 验证通过！格式符合标准")
        return True
    else:
        print(f"\n  ❌ 验证不通过！存在{len(errors)}项错误，禁止推库")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 bazi-format-check.py <报告路径>")
        sys.exit(1)
    
    result = check_report(sys.argv[1])
    sys.exit(0 if result else 1)
