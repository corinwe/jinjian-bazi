# WeChat Article Fetching Techniques

WeChat public account articles (mp.weixin.qq.com) have aggressive anti-bot protection — CAPTCHA verification, dynamic JS content loading. Two techniques work from a Linux server.

## Technique 1: Browser Use (Primary — Most Reliable)

Browser Use is a cloud browser automation service officially integrated with Hermes Agent. It runs a real browser in the cloud, which WeChat can't distinguish from a human user.

### Setup

1. Sign up at https://browser-use.com (free trial for Hermes Agent users: unlimited duration, free proxy, persistent auth — announced April 9, 2026)
2. Go to Settings → API Keys → Create API Key
3. Add to `~/.hermes/.env`:
   ```
   BROWSER_USE_API_KEY=your_key_here
   ```
4. Ask 金久 to create/fix the WeChat scraping skill using Browser Use:
   > "请使用Browser Use封装一个爬取微信公众号文章的skill；我已经将Browser Use的API KEY填写在了你的.env文件中"

### Reference Article

https://mp.weixin.qq.com/s/3SSECMxYl4ZmbT6FSBs9kA — "如何使用Hermes Agent稳定爬取公众号文章" by DracoVibeCoding

The author's skills are published in the Draco-Skills-Collection repository.

## Technique 2: Python Requests with Mobile UA (Fallback — Works ~30%)

When Browser Use isn't configured, Python `requests` with a mobile Android Chrome User-Agent can sometimes bypass the captcha.

### The Cooked Script

```python
import requests, re, html

url = "https://mp.weixin.qq.com/s/ARTICLE_SN"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'https://mp.weixin.qq.com/',
})
r = session.get(url, timeout=30)

# Check if accessible
if '环境异常' in r.text:
    print("BLOCKED — use Browser Use instead")
    return

# Extract title
t = re.search(r'var msg_title = "([^"]+)', r.text)
title = t.group(1) if t else "Untitled"

# Extract rich_media_content
idx = r.text.find('rich_media_content')
if idx > 0:
    start = r.text.find('>', idx) + 1
    # Find all leaf spans with text
    texts = re.finditer(r'<span[^>]*leaf[^>]*>([^<]+)</span>', r.text[start:start+300000])
    content = '\n'.join(html.unescape(m.group(1)) for m in texts)
```

### Key Headers That Matter

| Header | Value | Why |
|--------|-------|-----|
| User-Agent | Android 13 Chrome mobile | Desktop UAs get blocked immediately |
| Accept | text/html,... | Standard |
| Accept-Language | zh-CN,zh | Chinese first |
| Referer | https://mp.weixin.qq.com/ | Simulates clicking from WeChat |

### Why curl / headless browsers get blocked

- `curl` with any desktop UA → redirect to captcha page
- Headless Chrome/Firefox → detected as automation, captcha dialog triggered
- Python `requests` with Android mobile UA → sometimes passes through (the Android mobile endpoint has weaker protection)

### Extracting Article Content from Raw HTML

The article HTML is ~2.99MB for a long article. Content structure:

1. **Metadata**: `var msg_title` (title), `var msg_cdn_url` (cover image), `var create_time` (unix timestamp)
2. **Meta tags**: `<meta name="author" content="...">`, `<meta property="og:title" content="...">`
3. **Content**: Inside `id="js_content"` div. Find by scanning for `rich_media_content` class, then extract all `<span leaf>` inner text.
4. **Images**: `data-src` attributes on `<img>` tags (lazy-loaded). Base URL: `mmbiz.qpic.cn`

### Troubleshooting

- If captcha page appears: try different mobile UA, add cookies from a real session, or use Browser Use
- If content is empty: JS might have failed to render — use Browser Use
- If images don't load: WeChat requires specific referrers for image CDN — set `Referer: https://mp.weixin.qq.com/`

## Recommendation

Use **Browser Use** as the primary method. The Python requests fallback is useful for quick tests but unreliable for production use in the knowledge base pipeline.
