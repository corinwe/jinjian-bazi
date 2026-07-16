#!/usr/bin/env python3
"""
report-generator.py — 物理约束报告生成器
老板要求：所有模块必须从数据源取数，不能凭记忆或重算。
物理机制：DS 是唯一的输入参数，每个模块函数只从 DS 读取数据。

用法: python3 report-generator.py 姓名 模块名
       python3 report-generator.py weiqiling 所有模块
       python3 report-generator.py weiqiling 大运
"""

import json, os, sys, re

# ─── 数据源加载（必经入口） ───
DATA_DIR = '/tmp'

def load_ds(name):
    """物理约束：强制从文件读取数据源。没有文件 → 拒绝执行"""
    path = f'{DATA_DIR}/{name}_ds.json'
    if not os.path.exists(path):
        print(f"❌ 数据源不存在: {path}")
        print(f"   请先运行: python3 bazi-data-source.py /tmp/{name}_engine.json {path}")
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


# ─── 模块1：基础信息 ───
def module_basic(DS):
    """从DS读取基础信息"""
    return f"""# {DS.get('姓名','')} · 八字基础信息

| 源字段 | 数据 |
|:-------|:-----|
| DS['8字段'] | {' '.join(DS['8字段'][:2])} {' '.join(DS['8字段'][2:4])} {' '.join(DS['8字段'][4:6])} {' '.join(DS['8字段'][6:8])} |
| DS['日主'] | {DS['日主']}金 |
| DS['身强弱']['总分'] | {DS['身强弱']['总分']}分 |
| DS['身强弱']['等级'] | {DS['身强弱']['等级']} |
| DS['空亡'] | {DS['空亡']} |
| DS['起运年龄'] | {DS['起运年龄']} |
"""


# ─── 模块2：体用分析 ───
def module_tiyong(DS):
    """体用计算——所有数字从DS['身强弱']和DS['藏干十神']取"""
    # 体 = 身强弱得分 + 印 + 比劫 + 食伤
    ti_base = DS['身强弱']['总分']
    
    # 从藏干十神中提取体的成分（印/比劫/食伤）
    ti_extra = []
    yong_items = []
    for zk in ['年支','月支','日支','时支']:
        if zk in DS.get('藏干十神', {}):
            for c in DS['藏干十神'][zk]:
                ss = c['十神']
                bl = c['比例']
                # 体：印、比劫、食伤
                if ss in ['正印','偏印','比肩','劫财','食神','伤官']:
                    ti_extra.append(f"  {zk}{c['天干']}({bl})={ss}")
                # 用：财、官
                if ss in ['正财','偏财','正官','七杀']:
                    yong_items.append(f"  {zk}{c['天干']}({bl})={ss}")
    
    return f"""## 体用分析

### 体（DS['身强弱']+DS['藏干十神']印比食伤）
- 基础分: {ti_base}分
"""
    + ('\n'.join(ti_extra) if ti_extra else '  (无线下成分)')
    + f"""

### 用（DS['藏干十神']财官）
"""
    + ('\n'.join(yong_items) if yong_items else '  (无线下财官)')


# ─── 模块3：大运分析 ───
def module_dayun(DS):
    """大运——所有数字从DS['大运']取"""
    lines = ["## 大运分析\n"]
    lines.append(f"| 大运 | 年龄 | 天干来源 | 地支来源 |\n|:----|:---:|:---------|:---------|\n")
    
    for y in DS['大运']:
        gan = y['干支'][0]
        zhi = y['干支'][1]
        lines.append(f"| {y['干支']} | {int(y['起始年龄'])}-{int(y['终止年龄'])} | DS['大运'][{y['序号']-1}]['干支'][0]={gan} | DS['大运'][{y['序号']-1}]['干支'][1]={zhi} |\n")
    
    return ''.join(lines)


# ─── 模块4：藏干十神全表 ───
def module_zanggan(DS):
    """藏干十神——所有数据从DS['藏干十神']取"""
    lines = ["## 藏干十神表\n"]
    lines.append("| 地支 | 藏干成分 | 比例 | 十神 | 数据来源 |\n|:----|:---------|:----:|:----|:--------|\n")
    
    for zk in ['年支','月支','日支','时支']:
        if zk in DS.get('藏干十神', {}):
            for c in DS['藏干十神'][zk]:
                lines.append(f"| {zk} | {c['天干']} | {c['比例']} | {c['十神']} | DS['藏干十神']['{zk}'] |\n")
    
    return ''.join(lines)


# ─── 模块5：神煞 ───
def module_shensha(DS):
    """神煞——所有数据从DS['神煞']取"""
    lines = ["## 神煞\n"]
    for k, v in DS.get('神煞', {}).items():
        if v:
            lines.append(f"- **{k}**: {v} (DS['神煞']['{k}'])\n")
    return ''.join(lines)


# ─── 主流程 ───
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 report-generator.py <姓名> [模块名|所有模块]")
        sys.exit(1)
    
    name = sys.argv[1]
    modules = sys.argv[2] if len(sys.argv) > 2 else '所有模块'
    
    # ⚡ 物理约束：从文件加载 DS，不从内存/记忆取
    print(f"加载数据源: {DATA_DIR}/{name}_ds.json")
    DS = load_ds(name)
    
    # 注册模块
    all_modules = {
        '基础': module_basic,
        '体用': module_tiyong,
        '大运': module_dayun,
        '藏干': module_zanggan,
        '神煞': module_shensha,
    }
    
    if modules == '所有模块':
        for mod_name, mod_fn in all_modules.items():
            print(f"\n{'='*50}")
            print(f"模块: {mod_name}")
            print(f"数据源字段: {[k for k in mod_fn.__code__.co_names if 'DS' in k]}")
            print(f"{'='*50}")
            print(mod_fn(DS))
    else:
        mod_fn = all_modules.get(modules)
        if mod_fn:
            print(mod_fn(DS))
        else:
            print(f"❌ 未知模块: {modules}，可选: {list(all_modules.keys())}")
