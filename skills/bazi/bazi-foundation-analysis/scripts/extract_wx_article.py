#!/usr/bin/env python3
"""
金鉴真人·微信公众号文章提取器
用法: python3 extract_wx_article.py <URL>
输出: 标准输出打印标题+正文
依赖: curl, python3
"""
import subprocess, re, html, sys

def extract(url):
    ua = "Mozilla/5.0 (Linux; Android 13; SM-S9080) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.33"
    result = subprocess.run(f'curl -s -L -A "{ua}" "{url}"', shell=True, capture_output=True, text=True, timeout=20)
    data = result.stdout

    og_title = re.search(r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', data)
    title = og_title.group(1) if og_title else ""

    m = re.search(r'<div[^>]*id="js_content"[^>]*>(.*?)</div>\s*<script', data, re.DOTALL)
    body = ""
    if m:
        clean = re.sub(r'<[^>]+>', '\n', m.group(1))
        clean = re.sub(r'\n{3,}', '\n\n', clean).strip()
        body = html.unescape(clean).replace('&nbsp;', ' ')

    return title, body

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python3 extract_wx_article.py <URL>", file=sys.stderr)
        sys.exit(1)
    title, body = extract(sys.argv[1])
    print(f"标题: {title}")
    print("=" * 60)
    print(body)
