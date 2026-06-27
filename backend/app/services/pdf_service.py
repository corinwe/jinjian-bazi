"""PDF生成服务 — 使用wkhtmltopdf将Markdown报告转为PDF"""
import os
import tempfile
import subprocess
import logging
import markdown

logger = logging.getLogger(__name__)

PDF_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<style>
@page {{ size: A4; margin: 15mm 12mm; }}
body {{
    font-family: "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 9.5pt;
    line-height: 1.7;
    color: #1a1a1a;
    background: #fff;
}}
h2 {{
    font-size: 12pt;
    color: #8B4513;
    border-bottom: 1px solid #ddd;
    padding-bottom: 3px;
    margin-top: 16px;
    margin-bottom: 8px;
}}
h3 {{
    font-size: 10.5pt;
    color: #555;
    margin-top: 12px;
    margin-bottom: 4px;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin: 6px 0;
    font-size: 8.5pt;
}}
td, th {{
    border: 1px solid #ccc;
    padding: 3px 5px;
}}
th {{
    background: #f5f5f5;
    font-weight: bold;
}}
strong {{ color: #8B4513; }}
p {{ margin: 4px 0; }}
ul, ol {{ margin: 4px 0; padding-left: 20px; }}
li {{ margin: 2px 0; }}
hr {{ border: none; border-top: 1px dashed #ddd; margin: 12px 0; }}
</style>
</head>
<body>
<div style="text-align:center;margin-bottom:20px;">
    <h1 style="font-size:16pt;color:#8B4513;border:none;">金鉴真人 · 八字命理分析报告</h1>
    <p style="font-size:8pt;color:#999;">基于传统八字命理学 · 确定性规则引擎生成</p>
</div>
{content}
</body>
</html>"""


def markdown_to_html(md_text: str) -> str:
    """Convert markdown report to styled HTML for PDF conversion"""
    # Convert markdown to HTML
    html_body = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code", "nl2br"],
    )
    return PDF_TEMPLATE.format(content=html_body)


def generate_pdf(md_text: str, output_path: str) -> str:
    """Generate PDF from markdown using wkhtmltopdf, returns output path"""
    # Convert MD → HTML
    html = markdown_to_html(md_text)

    # Write HTML to temp file
    fd, html_path = tempfile.mkstemp(suffix=".html", prefix="jinjian_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(html)

    try:
        # wkhtmltopdf options
        cmd = [
            "wkhtmltopdf",
            "--encoding", "UTF-8",
            "--page-size", "A4",
            "--margin-top", "15",
            "--margin-bottom", "15",
            "--margin-left", "12",
            "--margin-right", "12",
            "--no-outline",
            "--enable-local-file-access",
            html_path,
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            logger.error(f"wkhtmltopdf failed: {result.stderr[:500]}")
            # Fallback: return None, caller handles
            return output_path if os.path.exists(output_path) and os.path.getsize(output_path) > 0 else None
        logger.info(f"PDF generated: {output_path} ({os.path.getsize(output_path)} bytes)")
        return output_path
    except subprocess.TimeoutExpired:
        logger.error("wkhtmltopdf timed out after 60s")
        return None
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        return None
    finally:
        # Clean up temp HTML
        try:
            os.unlink(html_path)
        except OSError:
            pass
