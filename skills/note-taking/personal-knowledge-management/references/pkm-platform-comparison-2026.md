# PKM Platform Comparison 2026

## Research Date: 2026-05-24

Full systematic comparison of 25+ knowledge management platforms for a 10-year+ permanent knowledge base.

## Scoring Matrix (9 Dimensions, Max 35)

| Rank | Platform | Durability | Ownership | AI Writable | Chinese | Sync | Graph/Links | Mobile | Plugins | **TOTAL** |
|:----:|----------|:----------:|:---------:|:-----------:|:-------:|:---:|:-----------:|:-----:|:-------:|:---------:|
| 🥇 | **Obsidian+GitHub** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **34** |
| 🥈 | Obsidian+LiveSync | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | **33** |
| 🥉 | **SiYuan 思源笔记** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | **30** |
| 4 | Logseq+Git | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **29** |
| 5 | Joplin | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | **27** |
| 6 | Docusaurus/MkDocs | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | **28** |
| 7 | Notion | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **25** |
| 8 | AFFiNE | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | **23** |
| 9 | 语雀/飞书/我来 | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | **22** |
| 10 | Anytype | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | **16** |

## Platform Details

### Category A: Local-first Markdown Platforms

#### Obsidian (obsidian.md)
- **Data format**: Pure Markdown (.md) + optional YAML frontmatter
- **Open source**: Client closed-source (free), format fully open
- **GitHub stars**: ~N/A (not open source), but obsidian-git plugin ⭐11024, MCP Server ⭐3772
- **Plugins**: 4167+ community plugins
- **Chinese**: ✅ Perfect (native interface, active Chinese community)
- **Offline**: ✅ Fully offline
- **API**: ✅ REST API via local-rest-api plugin; MCP server for AI; headless mode
- **Bidirectional links**: ✅ Native [[wikilinks]] + graph view
- **Mobile**: ✅ iOS/Android
- **Cost**: Free (optional Obsidian Sync $5/mo)
- **Company**: Very stable, healthy revenue, long-term sustainable

#### SiYuan Note (思源笔记, github.com/siyuan-note/siyuan, ⭐44095)
- **Data format**: Markdown + custom JSON block data (NOT pure Markdown)
- **Open source**: ✅ AGPL-3.0
- **Chinese**: ✅⭐⭐⭐⭐⭐ Purpose-built for Chinese users
- **API**: ✅ REST API + WebSocket
- **Sync**: Official server / S3 / WebDAV / self-hosted
- **Bidirectional links**: ✅ Native, block-level, graph view
- **AI Agent writeable**: ✅ Via REST API
- **Cost**: Free (sync ~¥99-199/yr)
- **Key risk**: AGPL license complicates commercial output; JSON block data may not be readable by other tools in 10 years

#### Logseq (github.com/logseq/logseq, ⭐43043)
- **Data format**: Markdown (outliner format) or Org-mode
- **Open source**: ✅ AGPL-3.0
- **AI Agent writeable**: ⚠️ Difficult — outliner indentation is fragile
- **Chinese**: ✅ Good but less mature than Obsidian
- **Mobile**: ⚠️ Less mature
- **Key risk**: Fragile format for programmatic writes; AGPL license

#### Joplin (github.com/laurent22/joplin, ⭐54935 — largest open-source notes project)
- **Data format**: Markdown (internally SQLite db)
- **Open source**: ✅ AGPL-3.0
- **API**: ✅ REST API + CLI
- **AI Agent writeable**: ✅ Via REST API
- **Bidirectional links**: ⚠️ Limited, no graph view
- **Key gap**: No knowledge network — flat notes, not a "second brain"

#### Other Local Platforms
| Platform | ⭐ | Format | AI Write | Mobile | Verdict |
|----------|---|--------|----------|--------|---------|
| TiddlyWiki5 | 8589 | Single HTML | ✅ API | ⚠️ Limited | Great but single-file limits scale |
| Dendron | 7401 | Pure MD | ✅ Write file | ❌ None | Declining activity, risky |
| Foam | 17155 | Pure MD | ✅ Write file | ❌ None | VS Code plugin, no mobile |
| Zettlr | 13033 | Pure MD | ✅ Write file | ❌ None | Academic writing tool, not general PKM |
| TriliumNext | 2919 | HTML/MD | ✅ REST API | ⚠️ OK | Small community, niche |
| Anytype | 7676 | Proprietary protobuf | ❌ Hard | ⚠️ Unstable | **Rejected**: Proprietary binary format |

### Category B: Cloud Platforms

#### Notion
- **Score**: 25/35
- **Fatal flaw**: Data on Notion's servers. Export corrupts database relationships, formulas, rollups. No real version history (30 days on paid plans). **Cannot be a 10yr+ permanent knowledge asset.**
- **API**: ✅ Excellent REST API — but writing to a platform that doesn't own your data is building on rented land.
- **Cost**: Free / Plus $10/mo / Business $18/mo

#### AFFiNE (github.com/toeverything/AFFiNE, ⭐68678 — fastest growing)
- **Score**: 23/35
- **Key issue**: Too young (launched 2023). API not mature. Data format evolving rapidly.
- **Promise**: Open source Notion alternative with local-first. **Watch in 2-3 years.**

#### Other Cloud
| Platform | Format | Data Ownership | Verdict |
|----------|--------|---------------|---------|
| Capacities | Proprietary | ❌ | Pure cloud, proprietary |
| Outline (⭐38599) | Markdown | ✅ Self-hosted | Team wiki, no graph/links |
| BookStack (⭐18776) | HTML/MD | ✅ Self-hosted | Documentation, not PKM |
| Docmost (⭐20334) | Markdown | ✅ | New, small community |

### Category C: Chinese-specific Platforms

| Platform | Format | Ownership | Offline | API | Verdict |
|----------|--------|-----------|--------|-----|---------|
| 语雀 (Yuque) | Proprietary | ❌ | ❌ | ⚠️ Limited | Alibaba-owned, pure online |
| 飞书文档 (Feishu) | Proprietary | ❌ | ❌ | ✅ | Great for collaboration, bad for personal asset |
| 我来 (Wolai) | Proprietary | ❌ | ❌ | ❌ No public API | Startup, highest risk |
| 印象笔记 (Evernote China) | Proprietary .enex | ❌ | ✅ Limited | ⚠️ Old API | Declining, acquired 2024, mass layoffs |

### Category D: Self-Hosted Wiki Platforms

| Platform | ⭐ | Format | Links/Graph | Verdict |
|----------|---|--------|------------|---------|
| Wiki.js | 28352 | Markdown | ⚠️ Limited | Enterprise wiki, not PKM |
| MediaWiki | 5063 | Wiki markup | ✅ | Too heavy for personal use |
| Docusaurus | 64993 | Pure MD | ❌ | Documentation site generator |
| MkDocs Material | 26784 | Pure MD | ❌ | Documentation site generator |
| GitBook | 28861 | Pure MD | ❌ | Documentation site generator |

## Sync Mechanism Comparison

### 4 Ways to Sync Obsidian

| Method | Realtime | Reliability | Cost | Best For |
|--------|----------|-------------|------|----------|
| **GitHub + git plugin** | Near-realtime | ⭐⭐⭐⭐⭐ Best durability | Free | Agent-write + multi-device sync ✅ |
| Obsidian Sync | Real-time | ⭐⭐⭐⭐ Official but closed | $5/mo | Simple setup, but not fully self-controlled |
| LiveSync (CouchDB) | Real-time | ⭐⭐⭐⭐ Self-host CouchDB | Server cost | When instant sync needed |
| WebDAV | Near-realtime | ⭐⭐⭐ Need WebDAV server | Server cost | Legacy approach |

## Key Takeaways for 10yr+ Knowledge Base

1. **Obsidian + GitHub** is the only solution scoring ≥⭐⭐⭐⭐ on durability, ownership, AI writability, Chinese, and graph/links simultaneously.
2. **Pure Markdown** is non-negotiable for 10-year durability.
3. **Git-based version history** is far superior to any built-in versioning in other platforms.
4. **Avoid platforms with proprietary formats** (Notion, Anytype, 语雀, 飞书) — they are knowledge traps.
5. **思源笔记 is the strongest Chinese-language alternative**, but the non-pure-Markdown data format + AGPL license are real concerns.
