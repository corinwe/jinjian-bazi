# Python execute_code 批量追加报告内容（BULK-FILL 模式实战记录）

## 问题背景

梦的八字报告初始已写基础框架，需从 ~900 行补到 ≥1,500 行。不能覆写（内容正确），也不能逐段 patch（效率太低）。需要「追加深度内容到已有报告中」。

## 使用流程（已验证5轮·每轮~200行）

```python
# Step 1: 读取完整文件（必须用with open，禁止read_file）
with open('/tmp/报告.md') as f:
    content = f.read()

# Step 2: 定位插入位置——通常在最终签名块前
sig_pos = content.find('**排盘验证**')

# Step 3: 生成待插入的markdown内容
bulk = """
### 新§标题

{详细内容…}
"""

# Step 4: 插入拼接
new_content = content[:sig_pos] + bulk + '\n' + content[sig_pos:]

# Step 5: 覆写文件
with open('/tmp/报告.md', 'w') as f:
    f.write(new_content)

# Step 6: 验证行数和结构
lines = new_content.split('\n')
print(f"总行数: {len(lines)}")
sec_count = sum(1 for l in lines if l.startswith('## §'))
print(f"§数量: {sec_count}")
```

## 补充内容最佳方向（按优先级）

| 轮次 | 补充方向 | 每轮行数 |
|:----:|:---------|:--------:|
| 1 | §6.5 价值观分析 + §12.7 感情走势 | ~130行 |
| 2 | 8.6.1 增财方案 + 三决断补充 | ~90行 |
| 3 | 2.6 藏干纳音 + 3.6 评分对照 | ~70行 |
| 4 | 4.5 用神窗口 + 10.8 行业 | ~70行 |
| 5 | 附录B+C + 21.9 寄语 | ~50行 |

总效率：5轮→从903行到1502行

## 文件完整性检查（每轮后强制）

```python
lines = open('/tmp/报告.md').read().split('\n')
assert sum(1 for l in lines if l.startswith('## §')) == 21
assert len(lines) >= 1500
```

## 已发现陷阱

| 陷阱 | 修复 |
|:----|:-----|
| **断点位置选错**→内容插到中间 | 用 `content.rfind()` 定位最终插入点 |
| **编制人块重复**→mid-file断 | `grep -c "编制人"` 检查，>1次则手动删除 |
| **old_string不唯一**→patch失败 | 用execute_code全文件操作替代patch |
| **read_file截断**→丢60%内容 | 永远用 `with open` + `f.read()` |

## 推库前验证

```bash
echo "§: $(grep '^## §' 文件.md | wc -l)" && \
echo "重复: $(grep '^## §' 文件.md | sort | uniq -d | wc -l)" && \
echo "行数: $(wc -l < 文件.md)" && \
echo "品牌: $(grep -c '九龙道长' 文件.md)"
```
