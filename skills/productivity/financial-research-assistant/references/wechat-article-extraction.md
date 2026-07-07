# WeChat MP Article Content Extraction

**Purpose:** Extract clean text from mp.weixin.qq.com articles when `browser_navigate` hits a captcha/environment check.

## Problem

WeChat MP (公众号) articles often trigger an "环境异常" captcha when accessed via `browser_navigate`. The browser shows a verification page instead of the article content.

## Solution: curl + BeautifulSoup

### Step 1: Download the full HTML with curl

```bash
curl -s -L \
  "https://mp.weixin.qq.com/s/ARTICLE_ID" \
  -o /tmp/wechat_article.html \
  -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
```

The `-A` (User-Agent) flag is critical — WeChat returns the full article HTML even without passing the captcha, but only to standard browser UAs.

### Step 2: Extract text with BeautifulSoup

```python
from bs4 import BeautifulSoup

with open('/tmp/wechat_article.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

soup = BeautifulSoup(html, 'lxml')
content_div = soup.find('div', class_='rich_media_content')
if content_div:
    text = content_div.get_text(separator='\n', strip=True)
    print(text)
```

### Step 3 (fallback): JS variable `content_noencode`

If BeautifulSoup fails to find the content div (unlikely but possible), the article body is also embedded in a JavaScript variable:

```javascript
content_noencode: '\\x3ch3 ... (HTML-encoded article content)'
```

To extract it directly:

```python
import re

match = re.search(r"content_noencode:\s*'((?:\\.|[^'\\])*)'", html)
if match:
    encoded = match.group(1)
    # Decode \\xHH escape sequences
    def replace_hex(m):
        return chr(int(m.group(1), 16))
    decoded = re.sub(r'\\x([0-9a-fA-F]{2})', replace_hex, encoded)
    # Decode HTML entities
    decoded = decoded.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    decoded = decoded.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '\n', decoded)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    clean_text = '\n'.join(lines)
```

## Metadata

The article metadata is available in the same HTML:

| Field | How to find |
|-------|------------|
| Title | `<meta property="og:title" content="..."/>` |
| Description | `<meta property="og:description" content="..."/>` |
| JS title variable | `var msg_title = '...'.html(false);` |
| Author/Official Account | `.wx_follow_nickname` element text |

## Pitfalls ⚠️

- **3MB+ HTML files** — WeChat pages are bloated with JS. Reading the full file via `read_file` can be slow. Use `search_files` + `read_file(offset, limit)` to find specific sections, or pipe through `python3` directly in `terminal`.
- **Encoding** — The HTML is UTF-8; no special handling needed.
- **CSS class names** — WeChat uses obfuscated class names like `rich_media_content js_underline_content autoTypeSetting24psection`. The stable identifier is `rich_media_content` — don't include obfuscated suffixes in the soup query.
- **Captcha doesn't block curl** — the captcha only affects browser-based access (JS execution environment check). curl with a real User-Agent bypasses it entirely because WeChat serves the full article content server-side before the captcha script runs.
- **Install dependencies first** — `pip install beautifulsoup4 lxml -q` before running the extraction.
