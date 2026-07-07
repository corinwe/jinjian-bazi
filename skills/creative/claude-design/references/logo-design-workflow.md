# Logo / Brand Identity Design Workflow

Use this when the user asks for a logo, brand name, or visual identity. Complements the main claude-design SKILL.md — read that first for general design principles.

## When to use

- User asks "design me a logo"
- User asks "come up with a name + logo for my [project/brand/persona]"
- User wants a brand identity package (logo variants, color palette, usage scenarios)
- User wants to rename or rebrand an existing identity

## Pipeline: Naming → Visual → Delivery

### Phase 1: Name Brainstorming

Before designing, help the user settle on a name. This avoids spending effort on a visual direction for a name they won't keep.

**Process:**
1. Propose 4-5 name options, each with a short rationale
2. Each name should sound good, be easy to remember, and carry meaning
3. Mark your top recommendation clearly
4. Wait for the user to pick before moving to Phase 2

**Naming guidance for Chinese brand identities:**
- Two-character names are preferred (memorable, balanced)
- First character should convey domain/quality (金=wealth/gold, 招=fortune, 富=prosperity)
- Second character should convey longevity/aspiration (久=forever, 恒=constant, 远=farsighted)
- The name should sound good spoken aloud
- Avoid homophones with negative meanings

### Phase 2: Logo Visual Exploration

Default to **3 logo variants**, each exploring a different visual language:

| Variant | Style | Best for |
|---------|-------|----------|
| A (Conservative) | Traditional/heritage — seal script, stamp, calligraphy | Trust, authority, history |
| B (Strong-fit) | Modern/minimalist — geometric, gradient, clean | Tech, finance, contemporary brands |
| C (Divergent) | Symbolic/monogram — single character or mark, circular | Social avatars, app icons, quick recognition |

**Technical approach (when image_generate is unavailable):**

Hand-craft SVG files. SVGs are scalable, editable, and render correctly in all browsers.

For each SVG logo:
- `viewBox="0 0 400 400"` as standard canvas
- Dark background (#1a1817 or similar) for premium feel
- Use `<defs>` for gradients and filters
- For gold/chrome: multi-stop linearGradient (dark → light → dark)
- For seal/stamp: vermilion red (#c41e3a), rough edges via feTurbulence filter
- Chinese text: use `font-family="'Noto Serif SC', 'SimSun', 'STSong', serif"`
- Include pinyin/English subtext for completeness

### Phase 3: Brand Identity Page

Build an HTML showcase page with:
- All 3 logo variants displayed side by side
- Color palette swatches (4-5 colors)
- Brand tagline/motto
- Usage scenarios (avatar, business card, report watermark, social header)
- Your recommendation clearly marked

Use dark background with gold accents for premium financial/personal brands.

### Phase 4: Avatar Variant

In addition to the main logo, always create a **circular avatar version**:
- `viewBox="0 0 400 400"`, dark background
- Gold gradient circle, `r="160"`
- Single dominant character in center (the second character of the name, often the more distinctive one)
- No English/pinyin on the avatar — keep it clean
- Suitable for WeChat, Feishu, Discord profile pictures

## Color palette for wealth/investment brands

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary accent | Gold | #D4AF37 | Main brand color |
| Secondary accent | Vermilion | #C41E3A | Seals, traditional elements |
| Background | Near-black | #1A1817 | Dark mode base |
| Text/Muted | Bronze | #A0896A | Secondary text |
| Light accent | Gold highlight | #F5D480 | Gradients, shine effects |

## Pitfalls

- **Don't offer just one logo variant** — the user needs to choose between directions
- **Don't skip the naming phase** — designing a logo for a name the user rejects wastes effort
- **Don't use image_generate as the only path** — it may not be available; SVG fallback is production-ready
- **Don't use random web fonts** — Chinese brands need proper serif (Noto Serif SC, SimSun, STSong) for traditional feel, or clean sans for modern
- **Don't forget the avatar variant** — it's the most immediately useful deliverable (profile pics)
- **Don't output just SVG raw code** — deliver SVGs as files on disk with clear paths
