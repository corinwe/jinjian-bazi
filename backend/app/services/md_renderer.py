"""Markdown-to-HTML section pre-renderer for report performance optimization"""
import re
import markdown as md_lib


# Icon mapping — must match frontend
SECTION_ICON_MAP = {
    "格局": "🏛️",
    "学业": "📚",
    "事业": "💼",
    "财富": "💰",
    "婚姻": "💑",
    "感情": "💑",
    "子女": "👶",
    "文昌": "👶",
    "健康": "🏥",
    "灾祸": "⚠️",
    "搬迁": "⚠️",
    "大运": "⏳",
    "流年": "📅",
    "综合": "📋",
    "总览": "📊",
    "总结": "📋",
    "总评": "📋",
    "姓名": "🖋️",
    "建议": "💡",
    "三决断": "⚖️",
    "事件": "📅",
    "总表": "📊",
    "六亲": "👨‍👩‍👧‍👦",
    "置业": "🏠",
    "买房": "🏠",
    "身材": "🧍",
    "外貌": "🧍",
    "健康": "🏥",
    "附录": "📎",
    "实证": "✅",
    "校准": "✅",
    "五行": "🔥",
}


def _pick_icon(title: str) -> str:
    for keyword, icon in SECTION_ICON_MAP.items():
        if keyword in title:
            return icon
    return "📋"


_MD_EXTENSIONS = [
    "markdown.extensions.fenced_code",
    "markdown.extensions.tables",
    "markdown.extensions.codehilite",
    "markdown.extensions.nl2br",
    "markdown.extensions.sane_lists",
]


def render_sections(report_md: str) -> list[dict]:
    """Split markdown report into pre-rendered HTML sections.

    Returns list of {icon, title, content_html} — frontend can drop
    this directly into the DOM via dangerouslySetInnerHTML.
    """
    if not report_md or not report_md.strip():
        return []

    # Split by ## headers (but not #### sub-headers)
    parts = re.split(r'(?=^## (?!@|#))', report_md, flags=re.MULTILINE)
    parts = [p.strip() for p in parts if p.strip()]

    sections = []
    for part in parts:
        lines = part.split("\n")
        title_line = lines[0].strip()
        title = re.sub(r"^##\s*", "", title_line).strip()
        content = "\n".join(lines[1:]).strip()
        if not content:
            continue

        # Convert to HTML
        html = md_lib.markdown(content, extensions=_MD_EXTENSIONS)

        # Clean up nested <p> wrapping
        html = html.strip()

        sections.append({
            "icon": _pick_icon(title),
            "title": title,
            "content_html": html,
        })

    return sections
