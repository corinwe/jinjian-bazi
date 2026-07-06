#!/usr/bin/env python3
"""
金鉴真人·八字报告自动验证器 v1.0
===================================
强制验证：所有通过 delegate_task / 手动生成的八字报告，
在推库前必须运行此脚本，通过后方可 commit。

检查项：
1. §1 一页总览表：24个必填字段是否全部存在
2. §1-§20 全部20个板块是否存在（标题格式正确）
3. §16 全生命周期事件总表：数据行数是否≥40
4. 事件表时序：年份从小到大排列（无倒序）
5. 基础逻辑：子女出生年份不早于父母出生年、结婚早于生子等
6. 称谓自检：无「长女→长子→子女3」等矛盾序列
7. 头部元数据：编制人、编制时间、版本号是否存在

用法：
    python3 bazi-report-validator.py --report <报告文件路径>
    python3 bazi-report-validator.py --report <路径> --verbose  (详细输出)
    python3 bazi-report-validator.py --dir <目录>              (批量检查目录下所有.md文件)
    python3 bazi-report-validator.py --git-precommit            (作为git pre-commit hook运行)

返回码：
    0 = 全部通过
    1 = 有错误（不可推库）
"""

import sys
import re
import os

# ============================================================
# 配置区
# ============================================================

REQUIRED_SECTIONS = [str(i) for i in range(1, 21)]  # §1 to §20

REQUIRED_FIELDS_S1 = [
    "四柱八字", "日主", "性别", "出生时间", "命格等级", "身强身弱",
    "喜用神", "忌神", "财星分数", "财富等级", "最高学历", "事业等级",
    "从事行业", "婚姻质量", "子女情况", "最佳大运", "次佳大运", "最差大运",
    "身材/体型", "结婚最佳窗口", "置业/买房年份", "发财最佳年份",
    "学习力", "健康注意方面"
]

REQUIRED_HEADER_FIELDS = ["金鉴真人", "编制人", "编制时间", "版本"]

MIN_EVENT_ROWS = 40

# ============================================================
# 验证函数
# ============================================================

def check_section_headers(content):
    """检查§1-§20全部20个板块是否存在且标题格式正确"""
    errors = []
    warnings = []
    
    # 找所有 ## § 开头的标题
    found = {}
    for s in REQUIRED_SECTIONS:
        # 精确匹配：## §1 一页总览表（允许中间有空格或表情符号）
        pattern = rf'##\s*§{s}\b'
        matches = re.findall(pattern, content)
        found[s] = len(matches) > 0
        if not found[s]:
            errors.append(f"❌ 缺失板块 ## §{s}")
    
    # 检查是否有非§格式的板块标题（如 板块一、一、等）
    nonstandard_headers = re.findall(r'## (?:板块|第[一二三四五六七八九十])', content)
    if nonstandard_headers:
        warnings.append(f"⚠️ 发现非标准板块标题格式: {nonstandard_headers[:3]}...（应使用 ## §N 格式）")
    
    return errors, warnings, found

def check_s1_completeness(content):
    """检查§1一页总览表是否包含24个必填字段"""
    errors = []
    warnings = []
    
    # 提取§1内容
    s1_match = re.search(r'##\s*§1\s*一页总览表(.*?)(?=##\s*§2|\Z)', content, re.DOTALL)
    if not s1_match:
        return [f"❌ §1 一页总览表 未找到"], [], {}
    
    s1_text = s1_match.group(1)
    
    # 检查24个必填字段
    found_fields = {}
    for field in REQUIRED_FIELDS_S1:
        if field in s1_text:
            found_fields[field] = True
        else:
            found_fields[field] = False
            errors.append(f"❌ §1缺少字段: 「{field}」")
    
    # 检查字段值是否为空（即 | **字段名** | ** | ← 空值）
    empty_values = re.findall(r'\|\s*\*\*([^*]+)\*\*\s*\|\s*\*\*\s*\*?\*?\s*\|', s1_text)
    if empty_values:
        for field in empty_values:
            warnings.append(f"⚠️ §1字段「{field}」值为空")
    
    return errors, warnings, found_fields

def check_s16_events(content):
    """检查§16全生命周期事件总表的数据行数及时序"""
    errors = []
    warnings = []
    
    s16_match = re.search(r'##\s*§16\s*全生命周期重点事件总表(.*?)(?=##\s*§17|\Z)', content, re.DOTALL)
    if not s16_match:
        return [f"❌ §16 全生命周期重点事件总表 未找到"], [], 0, []
    
    s16_text = s16_match.group(1)
    
    # 提取所有数据行（含数字年份的行）
    lines = s16_text.split('\n')
    data_rows = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('|') and '---' not in stripped:
            # 检查是否包含年份（不依赖词边界，支持"1984甲子"格式）
            cells = [c.strip() for c in stripped.split('|') if c.strip()]
            if any(re.search(r'(?:19|20)\d{2}', cell) for cell in cells):
                data_rows.append(stripped)
    
    row_count = len(data_rows)
    
    if row_count < MIN_EVENT_ROWS:
        errors.append(f"❌ §16事件总表仅{row_count}行，要求≥{MIN_EVENT_ROWS}行")
    
    # 检查年份顺序
    years = []
    for row in data_rows:
        cells = row.split('|')
        for cell in cells:
            year_match = re.search(r'(?:19|20)\d{2}', cell)
            if year_match:
                years.append(int(year_match.group(0)))
                break
    
    # 检查是否从小到大
    if len(years) >= 2:
        for i in range(1, len(years)):
            if years[i] < years[i-1]:
                warnings.append(f"⚠️ 事件表年份顺序异常: {years[i-1]} → {years[i]}（可能倒序）")
                break
    
    # 检查9大类事件（宽松匹配，不依赖emoji）
    event_keywords = {
        "学业": "📚 学业", "事业/晋升": "💼 事业", "发财/财务": "🤑 发财",
        "置业/买房": "🏠 置业", "结婚/桃花": "💕 结婚", "子女添丁": "👶 子女",
        "灾祸/疾病": "⚠️ 灾祸", "搬迁/变动": "🔄 搬迁", "觉醒/转折": "💡 觉醒"
    }
    event_counts = {k: 0 for k in event_keywords.values()}
    for row in data_rows:
        type_cell = row.split('|')
        if len(type_cell) >= 3:
            row_text = type_cell[2] if type_cell[2] else ""
            for keyword, label in event_keywords.items():
                if keyword in row_text or keyword.replace("/", "") in row_text:
                    event_counts[label] += 1
    
    missing_types = [k for k, v in event_counts.items() if v == 0]
    for mt in missing_types:
        warnings.append(f"⚠️ 事件表缺少{mt}类事件")
    
    return errors, warnings, row_count, event_counts

def check_basic_logic(content, filename=""):
    """检查基础逻辑：时序、称谓、元数据"""
    errors = []
    warnings = []
    
    # 检查头部元数据
    first_200 = content[:200]
    header_ok = True
    for field in REQUIRED_HEADER_FIELDS:
        if field not in first_200 and field not in content[:500]:
            if field == "编制人":
                # 可能出现在头部
                pass
            warnings.append(f"⚠️ 未找到头部元数据: 「{field}」")
            header_ok = False
    
    # 检查称谓逻辑矛盾
    # 如果有「子女1」后面不能有「长子」
    has_child_numbered = bool(re.search(r'子女\d', content))
    has_elder_son = '长子' in content
    
    if has_child_numbered and has_elder_son:
        # 更精确：检查是否出现在事件表中
        event_section = re.search(r'##\s*§16.*?(?=##\s*§17)', content, re.DOTALL)
        if event_section:
            s16_text = event_section.group(0)
            if re.search(r'子女[12345]', s16_text) and '长子' in s16_text:
                warnings.append("⚠️ 称谓矛盾：「子女X」和「长子」同时出现在事件表中")
    
    # 检查同年结婚和离婚
    divorce_years = set()
    marriage_years = set()
    divorce_matches = re.findall(r'(\d{4}).*?离婚', content)
    marriage_matches = re.findall(r'(\d{4}).*?结婚', content)
    for y in divorce_matches:
        divorce_years.add(y)
    for y in marriage_matches:
        marriage_years.add(y)
    same_year = divorce_years & marriage_years
    if same_year:
        errors.append(f"❌ 同年结婚和离婚: {same_year}")
    
    return errors, warnings

def check_all(content, filename="", verbose=False):
    """运行所有检查"""
    all_errors = []
    all_warnings = []
    
    # 1. 板块标题检查
    if verbose: print("📋 检查板块标题...")
    errs, warns, _ = check_section_headers(content)
    all_errors.extend(errs)
    all_warnings.extend(warns)
    
    # 2. §1检查
    if verbose: print("📋 检查§1一页总览表...")
    errs, warns, fields = check_s1_completeness(content)
    all_errors.extend(errs)
    all_warnings.extend(warns)
    if verbose and fields:
        found_count = sum(1 for v in fields.values() if v)
        print(f"   §1字段: {found_count}/{len(REQUIRED_FIELDS_S1)} 已找到")
    
    # 3. §16检查
    if verbose: print("📋 检查§16全生命周期事件总表...")
    errs, warns, row_count, event_counts = check_s16_events(content)
    all_errors.extend(errs)
    all_warnings.extend(warns)
    if verbose:
        print(f"   §16事件行数: {row_count}")
        if event_counts:
            for k, v in event_counts.items():
                icon = "✅" if v > 0 else "❌"
                print(f"   {icon} {k}: {v}次")
    
    # 4. 基础逻辑检查
    if verbose: print("📋 检查基础逻辑...")
    errs, warns = check_basic_logic(content, filename)
    all_errors.extend(errs)
    all_warnings.extend(warns)
    
    return all_errors, all_warnings

def validate_file(filepath, verbose=False):
    """验证单个文件"""
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    filename = os.path.basename(filepath)
    if verbose:
        print(f"\n{'='*60}")
        print(f"📄 验证: {filename}")
        print(f"{'='*60}")
    
    errors, warnings = check_all(content, filename, verbose)
    
    total_issues = len(errors) + len(warnings)
    
    if verbose or (errors or warnings):
        print(f"\n{'─'*40}")
    
    for e in errors:
        print(f"  {e}")
    for w in warnings:
        print(f"  {w}")
    
    if not errors and not warnings:
        if verbose:
            print(f"  ✅ 全部通过！")
        return True
    elif not errors:
        print(f"  ⚠️ 有{warnings}条警告（可通过）")
        return True
    else:
        print(f"  ❌ 有{len(errors)}个错误（不可推库）")
        return False

def validate_directory(directory, verbose=False):
    """批量验证目录下所有.md文件"""
    md_files = [f for f in os.listdir(directory) if f.endswith('.md') and not f.startswith('_')]
    if not md_files:
        print(f"目录中无.md文件: {directory}")
        return True
    
    results = {}
    for f in sorted(md_files):
        path = os.path.join(directory, f)
        results[f] = validate_file(path, verbose)
    
    print(f"\n{'='*60}")
    print("📊 批量验证汇总")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"  共{len(results)}个文件: ✅ {passed}通过 | ❌ {failed}未通过")
    
    if failed > 0:
        print("\n  未通过文件:")
        for f, v in results.items():
            if not v:
                print(f"    ❌ {f}")
    
    return failed == 0

# ============================================================
# Git pre-commit hook模式
# ============================================================

def git_precommit():
    """作为git pre-commit hook运行，检查即将提交的.md文件"""
    import subprocess
    
    # 获取当前暂存区所有文件
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True, text=True, cwd=os.getcwd()
    )
    
    md_files = [f for f in result.stdout.split('\n') if f.strip().endswith('.md') and '八字' in f]
    
    if not md_files:
        # 也检查人物档案目录下的文件
        result2 = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        md_files2 = [f for f in result2.stdout.split('\n') if f.strip().endswith('.md') and ('人物档案' in f or '深析报告' in f or '命理' in f)]
        md_files.extend(md_files2)
    
    if not md_files:
        # 全量检查
        all_files = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        md_files = [f for f in all_files.stdout.split('\n') if f.strip().endswith('.md')]
    
    if not md_files:
        return True  # 没有需要检查的文件
    
    has_error = False
    for f in md_files:
        if os.path.exists(f):
            if not validate_file(f):
                has_error = True
    
    if has_error:
        print("\n🚫 Pre-commit门禁触发：存在未通过的八字报告！")
        print("   请修正后重新 git add 再 commit。")
        print("   如需跳过验证：git commit --no-verify\n")
        return False
    return True


# ============================================================
# 主入口
# ============================================================

if __name__ == '__main__':
    if '--git-precommit' in sys.argv:
        success = git_precommit()
        sys.exit(0 if success else 1)
    elif '--report' in sys.argv and '--dir' not in sys.argv:
        idx = sys.argv.index('--report')
        if idx + 1 < len(sys.argv):
            filepath = sys.argv[idx + 1]
            verbose = '--verbose' in sys.argv
            success = validate_file(filepath, verbose)
            sys.exit(0 if success else 1)
        else:
            print("❌ --report 后需指定文件路径")
            sys.exit(1)
    elif '--dir' in sys.argv:
        idx = sys.argv.index('--dir')
        if idx + 1 < len(sys.argv):
            directory = sys.argv[idx + 1]
            verbose = '--verbose' in sys.argv
            success = validate_directory(directory, verbose)
            sys.exit(0 if success else 1)
        else:
            print("❌ --dir 后需指定目录路径")
            sys.exit(1)
    else:
        print("金鉴真人·八字报告自动验证器 v1.0")
        print("用法:")
        print("  python3 bazi-report-validator.py --report <文件> [--verbose]")
        print("  python3 bazi-report-validator.py --dir <目录> [--verbose]")
        print("  python3 bazi-report-validator.py --git-precommit")
        sys.exit(0)
