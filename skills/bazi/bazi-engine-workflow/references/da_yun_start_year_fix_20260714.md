# 大运起算年份修复记录（2026-07-14）

## Bug描述
`da_yun.py` 中起运年份 `start_year` 使用「浮点月份偏移+Q4进位」算法，导致+1年偏移。

## 复现
- 八字：丙子 丁酉 庚戌 乙酉（1996-09-10 17:00 出生）
- 起运年龄：9.3岁
- 旧算法：1996 + int(9.3) + year_carry(1) = 2006 ❌
- 正确：1996 + 9 = 2005（0.3 < 0.5，不进位）✅

## 修复方案
将大运起算年份从「浮点月份偏移+Q4进位」改为统一规则：
```
qi_yun_year = birth_year + int(qi_yun_age)
if (qi_yun_age - int(qi_yun_age)) >= 0.5:
    qi_yun_year += 1
start_year = qi_yun_year + step * 10
end_year = start_year + 9
```

## 影响范围
- 所有qi_yun_age分数部分<0.5且出生月+月偏移跨年的八字
- 修复后第1步大运start_year正确=qi_yun_year
- 修复后不再出现qi_yun_year与第1步start_year不一致的情况

## 验证
家主(1980年生, 0.3岁起运): 甲申1980-1989 ✅ 不变
案例二(1996年生, 9.3岁起运): 戊戌2005-2014 ✅ 修正(原2006-2015)
