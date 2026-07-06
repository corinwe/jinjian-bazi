"""批量测试每个家族成员的九龙道长原始规则评分"""
import subprocess
import json

# 家族成员列表：(姓名, 年, 月, 日, 时, 分, 时辰索引, 性别, 备注)
members = [
    ("家主(老板)",    1980, 8,  6,  5,  0,  3, "男", "庚申 癸未 辛亥 辛卯"),
    ("主母成",        1987, 7,  20, 12, 0,  7, "女", "丁卯 丁未 庚午 壬午"),
    ("子源",          2011, 5,  31, 10, 0,  6, "男", "辛卯 癸巳 丙戌 癸巳"),
    ("父亲",          1949, 9,  30, 11, 0,  6, "男", "己丑 癸酉 癸亥 戊午"),
    ("立",            2011, 5,  19, 11, 10, 6, "男", "辛卯 癸巳 甲戌 庚午"),
    ("文",            1958, 9,  27, 16, 0,  8, "男", "戊戌 辛酉 丁未 戊申"),
    ("晓",            1984, 9,  4,  12, 0,  7, "女", "甲子 壬申 辛丑 甲午"),
    ("霞",            1984, 9,  19, 12, 0,  7, "女", "甲子 癸酉 丙辰 甲午"),
    ("母亲",          1952, 8,  25, 1,  0,  1, "女", "壬辰 戊申 癸卯 癸丑"),
    ("亮",            1982, 12, 6,  12, 0,  7, "男", "壬戌 辛亥 癸亥 戊午"),
    ("静",            2006, 4,  1,  5,  25, 3, "女", "丙戌 辛卯 庚申 己卯"),
]

for name, y, m, d, h, minute, shichen, gender, bazi in members:
    cmd = f"python3 bazi-engine.py {y} {m} {d} {h} {minute} {shichen} {gender} {name} --json"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        score = data['身强弱']['总分']
        level = data['身强弱']['等级']
        print(f"{name:12s} | {bazi:25s} | {score:4.1f}分 | {level}")
    except:
        print(f"{name:12s} | {bazi:25s} | ERROR | {result.stderr[:100]}")
