# Knowledge Base Directory Reorganization Protocol

> When the 10-domain folder taxonomy degrades — files scattered, duplicates accumulated, classification inconsistent — use this protocol to systematically restructure.

## When To Use

- User says "知识太散了" / "需要整理目录" / "分门别类放好"
- A domain directory has grown >50 flat files with no sub-classification
- Files live in multiple overlapping directories (e.g. 课程资料/ AND 八字实践/ AND root/)
- Same content appears in 2+ paths (duplicate files)
- References/ files spread across subdirectories instead of consolidated

## 7-Step Workflow

### Step 1: Full Scan & Inventory

```bash
# List ALL files (excluding .git/)
find <domain-dir>/ -type f -name '*.md' | grep -v '.git/' | sort

# List ALL subdirectories
find <domain-dir>/ -type d | grep -v '.git/' | sort
```

**Output**: Complete file manifest + directory tree. Print both.

### Step 2: Design Target Taxonomy

Define a **numbered classification scheme**. Use the `0X-` prefix for sort stability:

```
01-理论体系/    — Pure theoretical knowledge
02-人物档案/    — Person-based analysis reports
03-案例校准/    — Calibration records & case studies
references/     — Shared reference files (single instance only)
```

**Rules:**
- One **single** `references/` directory per domain — never split across subdirs
- Numbered prefix ensures filesystem sort order matches logical order
- Keep `00-索引/` or `00-入口/` as the entry point if needed

### Step 3: Create New Directory Structure

```bash
mkdir -p <domain-dir>/01-分类名/子分类
mkdir -p <domain-dir>/references
```

### Step 4: Execute File Move (with duplicate detection)

```python
# Pseudo-logic for the move script:
for each file:
    check if destination already has a file with same name
    if yes:
        md5sum source vs destination
        if identical:  # exact duplicate
            delete source
        if different:  # different versions
            rename source with _variant suffix before moving
    move source → destination
```

**Critical**: Before any `mv`, check for duplicates across old directories first. Use `md5sum` to compare.

### Step 5: Clean Empty Directories + Handle Residuals

```bash
# Remove empty directories
rmdir <old-empty-dir> 2>/dev/null

# Check for leftover files
find <domain-dir>/ -type f -name '*.md' | grep -v '^<domain-dir>/0[0-9]' | grep -v 'references/' | sort
```

If raw source files (PDFs, original transcripts) remain in old dirs, move them to a dedicated `00-原始素材/` subdirectory under 理论体系 rather than deleting.

### Step 6: Create Index Files

**Two files required:**

1. **目录总览.md** — Tree view of the directory + file count stats + quick-lookup table
2. **知识地图.md** — Concept-to-file mapping organized by topic area

```markdown
# Quick-lookup table format in 目录总览.md
| 你想找… | 去这里 |
|---------|--------|
| 某人的分析 | 02-人物档案/ → 对应人 |
| 理论知识 | 01-理论体系/ |

# Concept table format in 知识地图.md
| 概念 | 所在文件 | 路径 |
|------|----------|------|
| 概念A | filename.md | 01-理论体系/ |
```

### Step 7: Update Skills Index + Git Push

If this is the **八字命格** domain or another domain with a corresponding Hermes Agent skill:
- Add a **统一知识索引墙** section to the relevant skill's SKILL.md
- Include a quick-reference mapping: `概念 → skill_ref:目录/文件.md`

Git workflow:
```bash
cd <repo-root>
git add -A
git commit -m "YYMMDD 知识库目录重组 <domain> <new-structure-summary>"
# Resolve rebase conflicts manually — check for new files added to old directories on remote
git pull --rebase origin main
git push origin main
```

## Common Pitfalls

| Pitfall | Mitigation |
|---------|-----------|
| Files in old directories that `find` shows but `ls` misses | Use absolute paths in all mv commands |
| Git rebase conflicts because remote added files to now-renamed dirs | Accept `--ours` for dir structure, then manually move the conflicting files |
| Duplicate files with same name but different content | Keep both by renaming the duplicate with a `_source-variant` suffix |
| Empty directories not deletable because git tracks them | Just leave them — `rmdir` will fail silently, git will clean on next clone |
| User disk images (PDFs) in git history making repo heavy | They're already there; future policy: `.gitignore` PDFs >5MB |

## Example: 八字命格 3+1 Structure

```
八字命格/
├── 00-索引/          ← Entry point: directory overview + concept map
├── 01-理论体系/      ← 15 theory files + 金鉴课程/ + 00-原始素材/
├── 02-人物档案/      ← 7 numbered subdirs (01-家主-魏启令/ ... 07-家族合参/)
├── 03-案例校准/      ← Calibration records (empty, accumulates over time)
└── references/       ← All 9 shared reference files (single instance)
```

## Time Estimate

| Domain size | Files | Estimated time |
|-------------|-------|----------------|
| Small | <30 files | 2-3 minutes |
| Medium | 30-70 files | 5-8 minutes |
| Large | 70-150 files | 8-15 minutes |

Larger domains should be handled in batches (one sub-category at a time) to avoid overwhelming the agent's working memory.
