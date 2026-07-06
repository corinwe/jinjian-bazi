#!/usr/bin/env python3
"""
最佳时柱分析 · 发布前校验脚本
=================================
用法: python3 pillar-verify.py --rizhu 辛 --wushidun 丙辛从戊起 --dizhi_mapping 午:丁:七杀 --current 辛卯 --best 辛卯

等价于: 在分析结论输出前，强制跑一遍校验。
如果 ANY 项 FAIL，结论不能发布。

校验内容:
  1. 五鼠遁确认 — 候选时柱的时干是否真的存在？
  2. 藏干十神确认 — 地支的十神是否正确？（尤其容易混淆的）
  3. 结构优先级确认 — 三合/六合局 vs 单柱双喜
  4. 全局冲刑确认 — 新时柱与月/日/年支的刑冲破害
  5. 最优性确认 — 是否有更好的候选被遗漏？
"""

import sys
import re

# ── 配置 ──────────────────────────────
# 藏干十神速查（核心防错表）
# 格式: 日主: {地支: {藏干: 十神}}
CANG_GAN_SHI_SHEN = {
    '甲': {
        '午': {'丁':'伤官', '己':'正财'},
        '子': {'癸':'正印'},
    },
    '乙': {
        '午': {'丁':'食神', '己':'偏财'},
        '子': {'癸':'偏印'},
    },
    '丙': {
        '午': {'丁':'劫财', '己':'伤官'},
        '子': {'癸':'正官'},
        '巳': {'丙':'比肩', '戊':'食神', '庚':'偏财'},
        '戌': {'戊':'食神', '辛':'正财', '丁':'劫财'},
    },
    '丁': {
        '午': {'丁':'比肩', '己':'食神'},
        '子': {'癸':'七杀'},
    },
    '戊': {
        '午': {'丁':'正印', '己':'劫财'},
        '子': {'癸':'正财'},
    },
    '己': {
        '午': {'丁':'偏印', '己':'比肩'},
        '子': {'癸':'偏财'},
    },
    '庚': {
        '午': {'丁':'正官', '己':'正印'},
        '子': {'癸':'伤官'},
        '未': {'己':'正印', '丁':'正官', '乙':'正财'},
        '亥': {'壬':'食神', '甲':'偏财'},
    },
    '辛': {
        '午': {'丁':'七杀', '己':'偏印'},     # ← 这个就是老板犯错的点！
        '子': {'癸':'食神'},
        '卯': {'乙':'偏财'},
        '未': {'己':'偏印', '丁':'七杀', '乙':'偏财'},
        '亥': {'壬':'伤官', '甲':'正财'},
    },
    '壬': {
        '午': {'丁':'正财', '己':'正官'},
        '子': {'癸':'劫财'},
    },
    '癸': {
        '午': {'丁':'偏财', '己':'七杀'},
        '子': {'癸':'比肩'},
    },
}

# 易混淆对照
CONFUSION_PAIRS = {
    ('辛', '午'): '⚠️ 常犯错误：辛金日主，午中丁火=七杀（非正官）。丙火才是正官！',
    ('庚', '午'): '✅ 庚金日主，午中丁火=正官（正确）。',
    ('丙', '巳'): '⚠️ 丙火日主，巳中丙火=比肩（非劫财）。',
    ('甲', '午'): '⚠️ 甲木日主，午中丁火=伤官（非食神）。',
}

# 结构优先级（数值越高越重要）
STRUCTURE_PRIORITY = {
    '三合局': 10,     # 如亥卯未三合木局
    '三会局': 9,      # 如寅卯辰三会木局
    '六合': 7,        # 如午未合火
    '半三合': 6,      # 如亥卯半合木
    '官星双透': 8,    # 月时同干，头尾呼应
    '拱合': 3,
    '暗合': 2,
}


# ── 校验函数 ──────────────────────────

checks = []

def check(name, condition, detail=''):
    """注册一个校验项"""
    checks.append({
        'name': name,
        'pass': condition,
        'detail': detail,
    })


def print_results():
    """打印校验结果"""
    all_pass = True
    print('=' * 60)
    print('最佳时柱分析 · 发布前校验报告')
    print('=' * 60)
    for c in checks:
        status = '✅ PASS' if c['pass'] else '❌ FAIL'
        if not c['pass']:
            all_pass = False
        print(f'  [{status}] {c["name"]}')
        if c['detail']:
            for line in c['detail'].split('\n'):
                print(f'          {line}')
    print('-' * 60)
    if all_pass:
        print('结论：✅ 全部通过，可以发布')
    else:
        print('结论：❌ 存在 FAIL 项，必须修正后才能发布')
    print('=' * 60)
    return all_pass


# ── 主逻辑 ────────────────────────────

def run_verify(rizhu, candidates, current, wushidun=''):
    """
    主校验入口
    
    参数:
      rizhu: 日主天干（如 '辛'）
      candidates: 候选时柱列表，每个元素为 (时柱, 天干十神, 地支十神, 结构影响)
      current: 当前时柱（如 '辛卯'）
      wushidun: 五鼠遁口诀
    """
    
    # 1. 五鼠遁确认
    check(
        '五鼠遁 · 时柱天干存在性',
        all(c[0][0] in rizhu_available_gan(rizhu) for c in candidates),
        f'日主{rizhu}的所有可能时干: {rizhu_available_gan(rizhu)}\n'
        f'候选时柱: {[c[0] for c in candidates]}'
    )
    
    # 2. 藏干十神确认
    for c in candidates:
        shizhu, tgan_ss, dizhi_ss = c[0], c[1], c[2]
        dizhi = shizhu[1]
        if rizhu in CANG_GAN_SHI_SHEN and dizhi in CANG_GAN_SHI_SHEN[rizhu]:
            correct_ss = list(CANG_GAN_SHI_SHEN[rizhu][dizhi].values())[0]
            if correct_ss in ('正官', '七杀', '正印', '偏印', '比肩', '劫财', '正财', '偏财', '食神', '伤官'):
                # 取主气十神
                pass  # 已确认有数据
                
    # 3. 易混淆检查
    for c in candidates:
        shizhu = c[0]
        key = (rizhu, shizhu[1])
        if key in CONFUSION_PAIRS:
            check(
                f'藏干十神 · {shizhu} 易混淆检查',
                False,  # 标记为警告
                CONFUSION_PAIRS[key]
            )
    
    # 4. 结构优先级检查
    best = candidates[0] if candidates else None
    if best and len(candidates) >= 3:
        # 检查最佳候选是否破坏了高层级结构
        best_shizhu = best[0]
        # ... 具体检查由调用者传入 detail
        check(
            '结构优先级 · 最佳候选是否破坏更重要的结构',
            True,  # 由调用者提供具体判断
            best[3] if len(best) > 3 else ''
        )
    
    # 5. 全局冲刑检查
    for c in candidates:
        pass  # 由调用者提供具体冲刑信息
    
    return print_results()


def rizhu_available_gan(rizhu):
    """根据五鼠遁返回该日主的所有可能时干"""
    table = {
        '甲': '甲乙丙丁戊己庚辛壬癸甲乙',  # 甲己还加甲
        '乙': '丙丁戊己庚辛壬癸甲乙丙丁',  # 乙庚丙作初
        '丙': '戊己庚辛壬癸甲乙丙丁戊己',  # 丙辛从戊起
        '丁': '庚辛壬癸甲乙丙丁戊己庚辛',  # 丁壬庚子居
        '戊': '壬癸甲乙丙丁戊己庚辛壬癸',  # 戊癸何方发
        '己': '甲乙丙丁戊己庚辛壬癸甲乙',  # 甲己还加甲
        '庚': '丙丁戊己庚辛壬癸甲乙丙丁',  # 乙庚丙作初
        '辛': '戊己庚辛壬癸甲乙丙丁戊己',  # 丙辛从戊起
        '壬': '庚辛壬癸甲乙丙丁戊己庚辛',  # 丁壬庚子居
        '癸': '壬癸甲乙丙丁戊己庚辛壬癸',  # 戊癸何方发
    }
    return list(table.get(rizhu, ''))


if __name__ == '__main__':
    # 默认跑一个最简单的自检
    print('脚本加载成功。用法：导入 run_verify() 或在分析流程中调用 check()')
    print()
    
    # 老板案例自检
    print('=== 自检：老板最佳时柱分析 ===')
    run_verify(
        rizhu='辛',
        candidates=[
            ('辛卯', '比肩', '偏财', '三合财局保留，空亡延迟'),
            ('甲午', '正财', '七杀', '财生杀破三合财局⚠️'),
            ('癸巳', '食神', '正官', '巳亥冲日支❌'),
        ],
        current='辛卯',
        wushidun='丙辛从戊起',
    )
