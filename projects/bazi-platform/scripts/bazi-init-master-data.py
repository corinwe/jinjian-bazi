#!/usr/bin/env python3
"""
金鉴真人·八字主数据初始化脚本 v1.0
=====================================
流程:
  1. POST提交到官网(www.zydx.top)获取排盘数据
  2. 解析HTML提取: 四柱八字/藏干(十神)/大运/起运/纳音/称骨
  3. 写入 family_bazi_data.json 主数据文件
  4. 报告生成从此JSON读取，绝不再手动计算

用法:
  python3 bazi-init-master-data.py 2010 9 25 10 30 胜源 男

输出:
  - 更新 /scripts/family_bazi_data.json
  - 打印提取的数据摘要
"""

import sys, re, json, os, subprocess
from datetime import date, datetime

# ========== 参数解析 ==========
year, month, day, hour, minute, name, gender = sys.argv[1:8]
month = month.zfill(2)
day = day.zfill(2)
hour = hour.zfill(2)
minute = minute.zfill(2)
gender_int = "1" if gender == "男" else "0"

print(f"═══ 八字主数据初始化 ═══")
print(f"命主: {name} | {year}年{month}月{day}日 {hour}:{minute} | {gender}")

# ========== 第1步：官网拉取数据 ==========
print(f"\n[1/4] 调用官网排盘...")
curl_cmd = [
    "curl", "-s", "-L", "https://www.zydx.top/paipan.php",
    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "-H", "Accept: text/html,application/xhtml+xml",
    "-H", "Accept-Language: zh-CN,zh;q=0.9",
    "--data", f"act=ok&name={name}&DateType=0&year={year}&month={month}&date={day}&hour={hour}&minute={minute}&sex={gender_int}"
]

result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
html = result.stdout

if not html or len(html) < 100:
    print("❌ 官网响应为空或太短，可能网站不可达")
    sys.exit(1)

# ========== 第2步：解析HTML ==========
print(f"[2/4] 解析排盘数据...")

# --- 四柱八字 ---
tg_match = re.search(r'<tr id=\"tgline\">(.*?)</tr>', html, re.DOTALL)
dz_match = re.search(r'<tr id=\"dzline\">(.*?)</tr>', html, re.DOTALL)

tg_spans, dz_spans = [], []
if tg_match:
    tg_spans = [s for s in re.findall(r'<span class=\"big\"[^>]*>([^<]*)</span>', tg_match.group(1)) if s.strip()]
if dz_match:
    dz_spans = [s for s in re.findall(r'<span class=\"big\"[^>]*>([^<]*)</span>', dz_match.group(1)) if s.strip()]

tg_pillars = tg_spans[-4:] if len(tg_spans) >= 4 else ['?']*4
dz_pillars = dz_spans[-4:] if len(dz_spans) >= 4 else ['?']*4
pillars = [f'{t}{d}' for t, d in zip(tg_pillars, dz_pillars)]
bazi_str = f"{pillars[0]} {pillars[1]} {pillars[2]} {pillars[3]}"

# --- 纳音 ---
nayin = re.findall(r'<span class=\"nayin\">([^<]+)</span>', html)
nayin_map = {}
if len(nayin) >= 4:
    nayin_map = {"年柱": nayin[0], "月柱": nayin[1], "日柱": nayin[2], "时柱": nayin[3]}

# --- 地支藏干(十神标签) ---
cg_spans = re.findall(r'<span class=\"small\">([^<]+)</span>', html)
relevant_cg = [s for s in cg_spans if re.search(r'[劫伤印枭杀才食官比]', s)]
cg_pillars = relevant_cg[-4:] if len(relevant_cg) >= 4 else relevant_cg
pillar_names_cg = ['年支', '月支', '日支', '时支']

cg_data = {}
ten_shen_map_cg = {"杀":"七杀","枭":"偏印","比":"比肩","伤":"伤官","财":"正财","才":"偏财",
                   "官":"正官","食":"食神","劫":"劫财","印":"正印"}
for i, pn in enumerate(pillar_names_cg):
    if i < len(cg_pillars):
        cg_str = cg_pillars[i]
        cg_list = []
        for ch in cg_str:
            if ch in ten_shen_map_cg:
                cg_list.append(ten_shen_map_cg[ch])
            else:
                cg_list.append(ch)
        cg_data[pn] = cg_list

# --- 大运序列 ---
dayun_matches = re.findall(r'data-year=\"(\d+)\"[^>]*>([^<]+)', html)
dayun_list = []
for age_str, gan_str in dayun_matches:
    age = int(age_str)
    dayun_list.append({
        "干支": gan_str.strip(),
        "起始年龄": age,
        "终止年龄": age + 10
    })

# --- 起运年龄 ---
qiyun = re.search(r'起运.*?(\d+)\s*岁', html)
qiyun_age = float(qiyun.group(1)) if qiyun else 0

# --- 称骨 ---
weight_m = re.search(r'称骨重量.*?<td[^>]*>([^<]+)</td>', html, re.DOTALL)
comment_m = re.search(r'称骨评语.*?<td[^>]*>([^<]+)</td>', html, re.DOTALL)
chenggu = {}
if weight_m:
    chenggu["重量"] = weight_m.group(1).strip()
if comment_m:
    chenggu["评语"] = comment_m.group(1).strip()

# ========== 第3步：十神推导验证（关键！防财星误判） ==========
print(f"[3/4] 十神全量推导验证...")

# 十天干五行归属
tiangan_wuxing = {"甲":"木","乙":"木","丙":"火","丁":"火","戊":"土","己":"土","庚":"金","辛":"金","壬":"水","癸":"水"}
yang_gan = {"甲","丙","戊","庚","壬"}

# 十神判断函数
def get_shishen(rizhu, gan):
    """
    根据日主和天干字，返回十神
    推导逻辑：先定五行生克关系→再定阴阳→得十神名称
    """
    if gan not in tiangan_wuxing or rizhu not in tiangan_wuxing:
        return gan
    if gan == rizhu:
        return "比肩"
    
    ri_wuxing = tiangan_wuxing[rizhu]
    g_wuxing = tiangan_wuxing[gan]
    ri_yang = rizhu in yang_gan
    g_yang = gan in yang_gan
    same_yinyang = "同" if ri_yang == g_yang else "异"
    
    # 五行生克关系
    # 生我者为印
    shengwo = {"木":"水","火":"木","土":"火","金":"土","水":"金"}
    # 我生者
    wosheng = {"木":"火","火":"土","土":"金","金":"水","水":"木"}
    # 克我者
    kewo = {"木":"金","火":"水","土":"木","金":"火","水":"土"}
    # 我克者
    woke = {"木":"土","火":"金","土":"水","金":"木","水":"火"}
    
    if g_wuxing == shengwo[ri_wuxing]:
        return "正印" if same_yinyang == "异" else "偏印"  # 生我:正印(异)/偏印(同)
    if g_wuxing == wosheng[ri_wuxing]:
        return "伤官" if same_yinyang == "异" else "食神"  # 我生:伤官(异)/食神(同)
    if g_wuxing == kewo[ri_wuxing]:
        return "正官" if same_yinyang == "异" else "七杀"  # 克我:正官(异)/七杀(同)
    if g_wuxing == woke[ri_wuxing]:
        return "正财" if same_yinyang == "异" else "偏财"  # 我克:正财(异)/偏财(同)
    # 同五行
    return "比肩" if same_yinyang == "同" else "劫财"

# 推导天干十神
rizhu = tg_pillars[2]  # 日干

tian_gan_ten = {
    "年干": get_shishen(rizhu, tg_pillars[0]),
    "月干": get_shishen(rizhu, tg_pillars[1]),
    "日干": "日主",
    "时干": get_shishen(rizhu, tg_pillars[3]),
}

# 五行生克方向速查
wuxing_kes = {"木":"土","火":"金","土":"水","金":"木","水":"火"}  # 我克者

# 输出十神验证
wuxing = tiangan_wuxing.get(rizhu, "?")
ri_yang = rizhu in yang_gan
cai_wuxing = wuxing_kes.get(wuxing, "?")
print(f"\n  日主: {rizhu}({wuxing}) → {'阳' if ri_yang else '阴'}")
print(f"  我克者为财: {rizhu}克{cai_wuxing} → 财星五行={cai_wuxing}")
print(f"  天干十神: {tg_pillars[0]}({tian_gan_ten['年干']}) {tg_pillars[1]}({tian_gan_ten['月干']}) {tg_pillars[2]}(日主) {tg_pillars[3]}({tian_gan_ten['时干']})")

# ========== 第4步：写入主数据JSON ==========
print(f"\n[4/4] 写入主数据文件...")

# 读取现有数据
master_path = "/root/.hermes/profiles/jinjian-zhenren/scripts/family_bazi_data.json"
existing_data = []
if os.path.exists(master_path):
    with open(master_path) as f:
        existing_data = json.load(f)

# 检查是否已存在（同名覆盖）
existing_data = [e for e in existing_data if e.get("姓名") != name]

entry = {
    "姓名": name,
    "八字": bazi_str,
    "日主": rizhu,
    "性别": gender,
    "出生": f"{year}-{month}-{day} {hour}:{minute}",
    "官网数据": {
        "藏干(十神标签)": cg_data,
        "纳音": nayin_map,
        "称骨": chenggu,
        "起运年龄": qiyun_age,
    },
    "四柱": {
        "年柱": pillars[0],
        "月柱": pillars[1],
        "日柱": pillars[2],
        "时柱": pillars[3],
    },
    "十神天干": tian_gan_ten,
    "十神验证": {
        "日主": f"{rizhu}({wuxing})",
        "财星五行": cai_wuxing,
        "财星说明": f"我克者为财：{rizhu}克{cai_wuxing}",
        "注意事项": "⚠️ 财星五行不等于八字中出现的其他五行！如戊土日主财星为水(壬/癸)，甲木为七杀非偏财"
    }
}

existing_data.append(entry)

with open(master_path, 'w', encoding='utf-8') as f:
    json.dump(existing_data, f, ensure_ascii=False, indent=2)

# ========== 输出摘要 ==========
print(f"\n{'='*50}")
print(f"✅ 主数据初始化完成！")
print(f"{'='*50}")
print(f"  八字: {bazi_str}")
print(f"  日主: {rizhu}({wuxing})")
print(f"  财星五行: {cai_wuxing}")
print(f"  藏干: {cg_data}")
print(f"  纳音: {nayin_map}")
print(f"  大运: {len(dayun_list)}步")
print(f"  称骨: {chenggu}")
print(f"\n  📁 已写入: {master_path}")
print(f"  ⚠️  报告生成必须从此JSON读取，禁止手动计算！")
