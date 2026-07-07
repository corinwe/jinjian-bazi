# 日期扫描技术 — 八字反推正确出生日期

## 适用场景

当已知某人的准确八字，但提供的出生日期与引擎排盘结果不符时，使用此技术扫描一定日期范围，找到唯一匹配的日期。

### 典型触发条件

- 用户说「1980-07-16」但引擎排出来是 **庚寅日己卯时**，而用户的八字是 **辛亥日辛卯时**
- 八字已知（如庚申 癸未 辛亥 辛卯），但日期与八字对不上
- 多个信息来源日期冲突

## 原理

八字月柱由节气决定（非公历月份），日柱由60甲子循环决定。已知八字的年柱/月柱/日柱/时柱，就可以反向搜索哪些公历日期产生完全一致的排盘结果。

**关键：** 月柱与节气强绑定——只要日期还在该月令的节气范围内，就有可能。

## Python 扫描方法

### 方法一：搜索整个可能月份，输出匹配日

```python
from datetime import datetime, timedelta
import sys
sys.path.insert(0, 'projects/bazi-platform/engine')  # 或引擎实际路径
from paipan import get_full_paipan

known_八字 = '庚申 癸未 辛亥 辛卯'

# 扫描1980年6月~8月所有日期
start = datetime(1980, 6, 1)
end = datetime(1980, 8, 31)
d = start
while d <= end:
    for hour in [5, 6]:  # 卯时范围 5-7点
        try:
            pp = get_full_paipan(d.year, d.month, d.day, hour, '男')
            yg=pp['year_pillar']['gan']; yz=pp['year_pillar']['zhi']
            mg=pp['month_pillar']['gan']; mz=pp['month_pillar']['zhi']
            dg=pp['day_pillar']['gan']; dz=pp['day_pillar']['zhi']
            hg=pp['hour_pillar']['gan']; hz=pp['hour_pillar']['zhi']
            bazi = f'{yg}{yz} {mg}{mz} {dg}{dz} {hg}{hz}'
            if bazi == known_八字:
                print(f'✅ FOUND: {d.year}-{d.month:02d}-{d.day:02d} 时{hour}点 → {bazi}')
        except:
            pass
    d += timedelta(days=1)
```

### 方法二：只输出癸未月辛亥日

如果已知月柱（癸未）和日柱（辛亥），可以缩小搜索范围：

```python
from datetime import datetime, timedelta
import sys
sys.path.insert(0, 'projects/bazi-platform/engine')
from paipan import get_full_paipan

d = datetime(1980, 1, 1)
while d.year == 1980:
    try:
        pp = get_full_paipan(d.year, d.month, d.day, 5, '男')
        mg=pp['month_pillar']['gan']+pp['month_pillar']['zhi']
        dg=pp['day_pillar']['gan']+pp['day_pillar']['zhi']
        if mg == '癸未' and dg == '辛亥':
            print(f'  癸未月辛亥日: {d.year}-{d.month:02d}-{d.day:02d}')
    except:
        pass
    d += timedelta(days=1)
```

## 实战案例：老板（魏启令）生日纠正

| 项目 | 旧值（错误） | 新值（正确） |
|:----|:-----------|:------------|
| 用户提供的日期 | 1980-07-16 | 1980-08-06 |
| 日柱（旧日期） | 庚寅日 | — |
| 日柱（正确） | — | **辛亥日** |
| 月柱 | 癸未 ✅（正确） | 癸未 ✅ |
| 年柱 | 庚申 ✅ | 庚申 ✅ |
| 时柱（卯时） | 己卯 | **辛卯** |
| 引擎验证八字 | 庚申 癸未 庚寅 己卯 ❌ | **庚申 癸未 辛亥 辛卯** ✅ |

**扫描过程：**
1. 扫描1980年7月全月 + 8月1-10日（整个未月范围7月7日~8月7日）
2. 搜索 `get_full_paipan(1980, month, day, hour, '男')` 输出匹配的八字
3. 1980年唯一满足 **庚申年·癸未月·辛亥日·辛卯时** 的日期是 **8月6日**

**为什么8月6日仍在未月？**
- 1980年 **立秋** = 8月7日17:10
- 立秋前仍属未月（小暑~大暑→立秋前）
- 8月6日距立秋仅1天，完全在未月范围内 ✅

## 注意事项

### 1. 节气边界

扫描时一定要覆盖预计月份的**前后各2个月**，因为：
- 用户可能记错了月份
- 节气边界附近的日期可能在预期月份之外
- 如：7月28日仍属未月，但8月8日起已属申月

**安全范围：** 左右各扩展30天，扫描至少60天的窗口。

### 2. 时辰也要扫描

不同时辰的时柱不同，如果知道准确八字，把可能的时间段都扫一遍：
- 卯时范围 = 5-7点，两个整点小时（5:00-5:59和6:00-6:59）时柱相同（辛卯）
- 但跨时辰边界（如7点前/后）时柱可能变

### 3. 交叉验证

找到匹配日期后，跑一次完整引擎确认：
```bash
bash scripts/bazi-must-run-engine.sh -n 姓名 -g 性别 -y 年 -m 月 -d 日 -h 时
```

确认输出八字与已知八字完全一致。

### 4. USER.md / memory 同步

找到正确日期后，同步更新：
```yaml
□ USER.md 中的出生字段（如果包含）
□ memory 记录纠正事实
□ 所有引用旧日期的报告添加勘误
```

## 口诀

```
日期日柱对不上，扫描范围找真身
安全窗口六十天，节气边界要考虑
卯时卯时都一样，寅卯辰时要分清
找到日期跑引擎，八字一致才放心
同步更新记忆库，旧版勘误不能省
```
