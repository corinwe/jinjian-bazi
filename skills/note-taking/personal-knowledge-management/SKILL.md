---
name: personal-knowledge-management
description: Architecture and setup for a permanent personal knowledge base — local-first, open-format, AI-agent-writable, output-ready for courses/videos/consulting. Covers platform selection, sync architecture, folder taxonomy, and AI processing pipeline design.
version: 1.0.0
author: 金久
tags: [pkm, knowledge-base, obsidian, github, second-brain, knowledge-management]
related_skills: [obsidian, note-taking, obsidian]
---

# Personal Knowledge Management (PKM) System Design

## When To Use This Skill

Use this skill when the user asks about:
- Building a permanent/durable knowledge base (永久知识库)
- Personal knowledge management (PKM) system architecture
- Platform selection (Obsidian vs Notion vs 思源 vs others)
- Designing input/output pipelines for knowledge assets
- Setting up AI-agent-managed (金久) knowledge processing
- Knowledge monetization (courses, videos, consulting, speaking)

## Core Requirements (the user's specific needs)

This PKM design is for a specific profile:
- **Role**: Fortune 500 Greater China Tech #1 (技术一号位)
- **Domains**: 10 knowledge areas (see 10-Domain Folder Taxonomy below) — tech, management, digital transformation, AI/agents, OPC entrepreneurship, parenting/education, Chinese classics (国学, I-Ching), personal growth, investing/wealth, plus 🔟 output/作品
- **Input channels**: WeChat, Feishu, voice notes, links, articles, screenshots, random thoughts
- **Processing**: AI agent (金久) auto-categorizes, extracts insights, links to existing knowledge
- **Output**: Video courses, paid content, consulting, speaking presentations
- **Agent access**: Me (金久 = Hermes Agent) runs on Linux server, needs to write files programmatically

## 🥇 Recommended Architecture: Obsidian + GitHub + Obsidian Git Plugin

**Why this wins** (score 34/35 across 9 dimensions):

| Dimension | Score | Why |
|-----------|:-----:|-----|
| Durability (10yr+) | ⭐⭐⭐⭐⭐ | Pure Markdown files + GitHub distributed storage. Any editor can open them. GitHub backed by Microsoft. Even if GitHub dies, local files survive. |
| Data Ownership | ⭐⭐⭐⭐⭐ | 100% owned. Open format. No vendor lock-in. If Obsidian shuts down, files work in VS Code, Typora, any text editor. |
| AI Agent Writable | ⭐⭐⭐⭐⭐ | Write `.md` files → `git add/commit/push`. Trivial from terminal. |
| Chinese Support | ⭐⭐⭐⭐⭐ | Native Unicode. Perfect for classical Chinese, I-Ching trigrams, rare characters. |
| Sync | ⭐⭐⭐⭐ | GitHub as central hub. Agent push → user pull via Obsidian Git plugin. Not real-time but close enough. |
| Bidirectional Links | ⭐⭐⭐⭐⭐ | Native `[[wikilinks]]` + graph view. |
| Mobile | ⭐⭐⭐⭐ | iOS/Android app available. |
| Plugin Ecosystem | ⭐⭐⭐⭐⭐ | 4167+ community plugins. |
| Cost | ⭐⭐⭐⭐⭐ | Free (GitHub free tier sufficient for 10yr+). |

### How The Sync Works

```text
┌─────────────────┐     git push     ┌───────────┐     git pull     ┌──────────────────┐
│  金久 (Agent)    │ ──────────────►  │  GitHub   │ ◄────────────── │  用户电脑 (macOS)  │
│  Linux Server    │                  │  私有仓库  │                  │  Obsidian Desktop  │
│  write .md       │                  │           │                  │  + Git Plugin     │
│  git commit/push │                  └───────────┘                  │  auto sync        │
└─────────────────┘                                                 └──────────────────┘
```

## 10-Domain Folder Taxonomy (内容分类目录)

```
📁 魏无记知识库/
├── 📁 01-技术能力/          (architecture, cloud-native, engineering)
├── 📁 02-管理能力/          (team building, hiring, OKR, management)
├── 📁 03-数智化转型/        (strategy, tactics, case studies)
├── 📁 04-AI+智能体/         (LLM, agents, tools, hands-on)
├── 📁 05-OPC创业/           (business model, product, marketing)
├── 📁 06-教育育儿/           (philosophy, communication, planning)
├── 📁 07-国学哲学/          (I-Ching, Confucianism/Buddhism/Taoism)
├── 📁 08-个人成长/          (mental models, reading notes, health)
├── 📁 09-投资和财富/        (philosophy, market analysis, portfolio)
└── 📁 00-输出作品/          (course outlines, scripts, published work)
```

Prefixing with `01-` style numbering so they sort correctly in filesystem and Obsidian. The user's OPC brand is **魏无记**; the knowledge base repo lives at `github.com/corinwe/weiwuji-knowledge-base`.

## AI Processing Pipeline

When user sends input (any format):
1. **Identify domain** — from content analysis, not just folder match
2. **Extract core insight** — remove noise, preserve depth. Multi-perspective analysis (pro/con/金久判断) included by default
3. **Link to existing knowledge** — search vault for related notes via `[[wikilinks]]`
4. **Generate structured note** using `templates/knowledge-card.md` with YAML frontmatter + standard sections
5. **Mark output readiness** (⭐⭐⭐ = ready for course/video; ⭐⭐ = needs case/data; ⭐ = raw material)
6. **Write `.md` file** to correct folder in `/root/.hermes/weiwuji-knowledge-base/`
7. **Git workflow**: `cd /root/.hermes/weiwuji-knowledge-base && git pull --rebase && git add . && git commit -m "..." && git push`

### Input handling by source type

| Source | Technique | Reference |
|--------|-----------|-----------|
| WeChat article links | Python requests with mobile UA first; fall back to Browser Use | `references/wechat-article-fetching.md` |
| Feishu voice notes | 飞书妙记 transcribe → extract transcript → process text | |
| Plain links/URLs | Fetch with Python requests, extract main content with trafilatura | |
| Pasted text/articles | Direct extraction and analysis | |
| Random thoughts | Expand and clarify with user before writing | |

## Platform Comparison Reference

See `references/pkm-platform-comparison-2026.md` for full 25+ platform analysis (detailed scoring tables, GitHub stars data, exclusion reasons).
See `references/wechat-article-fetching.md` for WeChat article scraping techniques (Python requests fallback + Browser Use official integration).

### Key Exclusions Summary

| Platform | Why Excluded |
|----------|-------------|
| Notion | Data on someone else's server. Export corrupts database structure. No real version history. |
| 语雀/飞书/我来 | Pure online + proprietary format. Data not yours. Platform lock-in. |
| 思源笔记 SiYuan | Data isn't pure Markdown (JSON block data inside). AGPL license has commercial output risks. |
| Logseq | Outliner format is fragile for agent writes. Weak mobile. |
| Anytype | Proprietary protobuf binary. May be unreadable in 10 years. |
| AFFiNE | Too young (2023+), API not mature despite rapid growth (⭐68678). |
| Joplin | No bidirectional links or graph view. Not suitable for networked knowledge. |

## Capacity Planning

| Content Type | Size | Notes |
|-------------|------|-------|
| Per note (pure text) | ~3-5KB | Ultra concise, YAML frontmatter |
| 10,000 notes | ~50MB | ~10 years of daily input |
| With compressed screenshots | ~200-400KB each | Keep <500KB per image |
| GitHub free tier limit | 500MB-1GB recommended | Hard limit 5GB |

**GitHub free tier supports 10+ years of this knowledge base with room to spare.**

## Knowledge Card Template

See `templates/knowledge-card.md` for the standardized note template used for every knowledge card the agent writes. Each card includes:
- YAML frontmatter (title, date, domain, tags, source, output_readiness)
- Core insight (one-line distillation)
- Background source
- Deep analysis with 金久思考 (the agent's critical synthesis, not just summary)
- Output readiness scoring (⭐⭐⭐ = publishable)
- Bidirectional links to related notes
- Next action items

## Skill-to-Knowledge-Base Sync Protocol (2026-06-24 新增)

### Why This Matters

Every skill (SKILL.md + references + templates + scripts) has a **canonical** location under `~/.hermes/profiles/jinjian-zhenren/skills/` and a **mirror** under `~/weiwuji-knowledge-base/07-国学哲学/八字命格/04-金鉴真人体系/技能包/<skill-name>/`.

When a skill is updated (new version, new reference files, new scripts), the knowledge base mirror becomes stale. This causes confusion when the user queries from the knowledge base (Obsidian) and gets old content.

### Path Mapping

| Hermes Skills (canonical) | Knowledge Base (mirror) |
|:--------------------------|:------------------------|
| `skills/<skill-name>/SKILL.md` | `07-国学哲学/八字命格/04-金鉴真人体系/技能包/<skill-name>/SKILL.md` |
| `skills/<skill-name>/references/*` | `.../<skill-name>/references/*` |
| `skills/<skill-name>/scripts/*` | `.../<skill-name>/scripts/*` |
| `skills/<skill-name>/templates/*` | `.../<skill-name>/templates/*` |

### Sync Trigger

Sync happens **immediately after** every `skill_manage(action='create')` or `skill_manage(action='patch')` or `skill_manage(action='edit')` that modifies:
- SKILL.md content
- reference files
- scripts
- templates

### Sync Command (one-liner)

```bash
SKILL_NAME="bazi-report-template" && \
  SRC="/root/.hermes/profiles/jinjian-zhenren/skills/$SKILL_NAME" && \
  DST="/root/.hermes/weiwuji-knowledge-base/07-国学哲学/八字命格/04-金鉴真人体系/技能包/$SKILL_NAME" && \
  mkdir -p "$DST/references" "$DST/scripts" "$DST/templates" && \
  cp "$SRC/SKILL.md" "$DST/SKILL.md" && \
  ([ -d "$SRC/references" ] && cp -r "$SRC/references/"* "$DST/references/") && \
  ([ -d "$SRC/scripts" ] && cp -r "$SRC/scripts/"* "$DST/scripts/") && \
  ([ -d "$SRC/templates" ] && cp -r "$SRC/templates/"* "$DST/templates/") && \
  cd /root/.hermes/weiwuji-knowledge-base && \
  git add . && git commit -m "🔄 sync skill: $SKILL_NAME" && git push
```

### Dead Reckoning (when sync was missed)

If an earlier skill update was not synced, the fix is simple:
- The `src/` dir (under `~/.hermes/profiles/jinjian-zhenren/skills/`) is the **canonical truth** — its `ls -lt` shows the newest mtime.
- The `dst/` dir (under `weiwuji-knowledge-base`) is the **snapshot** — compare mtimes or file lists.
- Run the sync one-liner above; it overwrites the stale snapshot without asking.

### Pitfalls

- Do NOT sync skills that are not part of the 金鉴真人 system (e.g. `dogfood`, `creative/*` skills) — they have no knowledge base mirror.
- Do NOT delete the knowledge base copy when deleting a skill — the knowledge base is the user's permanent archive; the skill is the agent's working copy.
- When syncing a skill that doesn't have a mirror yet in the knowledge base, the `mkdir -p` creates the directory automatically.
- After sync, the user sees the updated content next time they open Obsidian + pull from GitHub.

## Deployment (actual setup from 2026-05-24)

- **GitHub repo**: `github.com/corinwe/weiwuji-knowledge-base` (private)
- **Server path**: `/root/weiwuji-knowledge-base/`
- **SSH key**: `~/.ssh/id_ed25519` (GitHub configured)
- **Agent name**: 金久 (wealth/knowledge assistant for 老板);  金鉴真人 (BaZi analysis master)
- **OPC brand**: 魏无记 (weiwuji)
- **User profile**: Fortune 500 Greater China Tech #1, expert in parenting + Chinese classics (国学/周易), doing OPC entrepreneurship
- **User aesthetic preference**: Apple-level minimalism — clean, modern, sharp lines, no ornamentation. Rejects traditional/ornate styles (seal stamps, gold bars, antique effects). All brand identity elements must follow this rule.

## Setup Steps (for user execution)

1. Create GitHub private repository
2. Initialize Obsidian vault locally, push to GitHub
3. Install community plugin `Obsidian Git` — enable auto-pull on startup
4. Configure git commit/push schedule (every 5-15 min)
5. **Tell 金久 the repo URL** — I'll clone it and start processing

## Git Workflow for Agent Management

### Daily write cycle
```bash
cd /root/.hermes/weiwuji-knowledge-base
git pull --rebase          # Always rebase, never merge — avoids merge commits
# ... write notes ...
git add .
git commit -m "📝 domain: topic summary"
git push
```

### Initial repo setup — history cleanup tip
When setting up a new knowledge base repo from scratch, mistakes in the initial commit (wrong repo name, wrong README content) are common. **Fix them immediately before the user clones**:

```bash
# Rebase to edit the root commit
git rebase -i --root
# Change 'pick' to 'edit' for the first commit
# Fix the files, then:
git add . && git commit --amend -m "🎉 init: correct name"
git rebase --continue
# Skip any subsequent empty fix commits
git push --force origin main
```

This is safe only when:
- The repo is new (0 or 1-2 commits)
- Nobody else has cloned yet
- The user has been told to `git fetch && git reset --hard origin/main` after

If the user HAS already cloned, add a fix commit instead — don't force-push and break their local checkout.

## Pitfalls

- **Do NOT store PDFs, videos, or raw audio in GitHub**. Link to cloud storage instead. Use `.gitignore` to exclude large attachments directory.
- **Do NOT over-write user edits**. When agent writes a note and user later modifies it locally, the next agent push must respect that. Git merge handles this naturally but be careful with force-push.
- **Do NOT create duplicate notes**. Always search existing vault before writing. Use `[[wikilinks]]` to reference existing notes.
- **Do NOT use proprietary Obsidian-only formatting** (DataView queries, Canvas diagrams) extensively in notes meant for permanent archive. Keep format portable.
- **Mind the AGPL trap**: If user wants to sell courses based on knowledge base content, avoid source code licensed under AGPL in the same repo (思源笔记 uses AGPL).
- **WeChat articles blocked from standard HTTP requests**: WeChat (mp.weixin.qq.com) has aggressive anti-bot protection — CAPTCHA verification, dynamic JS content loading. Two techniques work:

- **Directory reorganization**: See `references/knowledge-base-reorganization-protocol.md` for the 7-step protocol when knowledge base directories become scattered or need restructuring.
- **Git workflow**: See `references/knowledge-base-git-workflow.md` for repo init, directory structure, and daily push procedure.

  **Primary — Browser Use** (official Hermes Agent integration, most reliable):
  1. Sign up at https://browser-use.com (free trial for Hermes Agent users — unlimited duration, free proxy, persistent auth)
  2. Get API Key from Settings → API Keys
  3. Add to `~/.hermes/.env`: `BROWSER_USE_API_KEY=your_key`
  4. Ask 金久 to create/fix the WeChat scraping skill using Browser Use
  - Reference: https://mp.weixin.qq.com/s/3SSECMxYl4ZmbT6FSBs9kA (article by DracoVibeCoding)

  **Fallback — Python requests with mobile User-Agent** (no new tools needed, works ~30% of the time):
  - `curl` and headless browsers get blocked. But Python `requests` with a mobile Android Chrome UA (`Mozilla/5.0 (Linux; Android 13; Pixel 7) ...`) can sometimes bypass the captcha entirely and return the full 2.99MB article page.
  - Set headers: `Accept`, `Accept-Language: zh-CN,zh;q=0.9`, `Referer: https://mp.weixin.qq.com/`
  - The article content is embedded in `id="js_content"` div. Extract by finding the matching `</div>` with depth tracking.
  - Also check `og:title` / `og:description` meta tags and `var msg_title` JS variable for metadata.
  - See `references/wechat-article-fetching.md` for the cooked script.

  **When both fail**: Ask user to copy-paste article text directly. This is a WeChat-imposed constraint, not a system flaw.
- **Agent writes must not overwrite user edits**: When agent pushes a new note and user later modifies it locally, the next agent push must handle git merge gracefully. Never force-push. Use `git pull --rebase` on the agent side before pushing.
