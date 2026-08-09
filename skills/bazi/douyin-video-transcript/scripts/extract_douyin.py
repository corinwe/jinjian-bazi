#!/usr/bin/env python3
"""
抖音视频口播文案提取器（一键版·2026-08-02）
用法:
    python3 extract_douyin.py "https://v.douyin.com/XXXX/"        # 短链/任意分享链接
    python3 extract_douyin.py "https://www.douyin.com/video/123"  # 完整链接
    python3 extract_douyin.py 7644336490964618502                 # 直接aweme_id
输出:
    /tmp/douyin_video.mp4     视频
    /tmp/douyin_audio.wav     音频
    /tmp/douyin_transcript.txt 转写文案（带时间戳）
"""
import asyncio, json, os, re, sys, subprocess, tempfile


def extract_aweme_id(url_or_id: str) -> str:
    """从任意抖音链接提取aweme_id"""
    m = re.search(r"(\d{15,20})", url_or_id)
    if m:
        return m.group(1)
    return url_or_id.strip()


async def resolve_short_url(url: str) -> str:
    """短链解析（v.douyin.com → 真实URL）"""
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1")
        page = await ctx.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(3000)
            return page.url
        finally:
            await browser.close()


async def get_video_url(aweme_id: str) -> tuple[str, str, str]:
    """移动端分享页提取真实视频URL + 标题 + 描述"""
    from playwright.async_api import async_playwright
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
        ctx = await browser.new_context(user_agent=ua, viewport={"width": 390, "height": 844})
        page = await ctx.new_page()
        await page.goto(f"https://www.iesdouyin.com/share/video/{aweme_id}", wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(5000)

        # 方法A: ROUTER_DATA
        router = await page.evaluate("""() => {
            for (const scr of document.querySelectorAll('script')) {
                const t = scr.textContent || '';
                if (t.includes('_ROUTER_DATA')) {
                    const m = t.match(/window\\._ROUTER_DATA = (\\{.*\\})/s);
                    if (m) return m[1];
                }
            }
            const rd = document.querySelector('script#RENDER_DATA');
            if (rd) return decodeURIComponent(rd.textContent);
            return '';
        }""")

        video_url, title, desc = "", "", ""
        if router:
            try:
                data = json.loads(router)
                item = None
                try:
                    item = data["loaderData"]["video_(id)/page"]["videoInfoRes"]["item_list"][0]
                except Exception:
                    pass
                if item:
                    desc = item.get("desc", "")
                    pa = item.get("video", {}).get("play_addr", {})
                    urls = pa.get("url_list", [])
                    video_url = urls[0] if urls else ""
                    au = item.get("author", {})
                    title = au.get("nickname", "")
            except Exception:
                pass
            if not video_url:
                m = re.search(r'playwm\\?/?[^"\\]*video_id=([^"\\&]+)', router)
                if m:
                    video_url = f"https://aweme.snssdk.com/aweme/v1/playwm/?video_id={m.group(1)}&ratio=720p&line=0"

        # 方法B: video标签
        if not video_url:
            video_url = await page.evaluate("""() => {
                const v = document.querySelector('video');
                return v ? (v.currentSrc || v.src || '') : '';
            }""")
        if not title:
            title = await page.title()
        await browser.close()
        return video_url, title, desc


def download_video(video_url: str, out: str) -> bool:
    """下载MP4（移动端UA+Referer）"""
    ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    r = subprocess.run([
        "curl", "-sL", video_url,
        "-H", f"User-Agent: {ua}",
        "-H", "Referer: https://www.iesdouyin.com/",
        "-o", out, "--max-time", "60",
    ])
    if os.path.exists(out) and os.path.getsize(out) > 100000:
        return True
    return False


def extract_audio(mp4: str, wav: str) -> bool:
    r = subprocess.run(["ffmpeg", "-y", "-i", mp4, "-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", wav],
                       capture_output=True, text=True)
    return os.path.exists(wav) and os.path.getsize(wav) > 10000


def transcribe(wav: str, out_txt: str, model_size: str = "medium") -> str:
    from faster_whisper import WhisperModel
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    except Exception:
        model_size = "small"
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    print(f"[转写] 模型={model_size}")
    segments, info = model.transcribe(wav, language="zh", beam_size=5)
    lines = []
    full = ""
    for seg in segments:
        line = f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text}"
        lines.append(line)
        full += seg.text
    with open(out_txt, "w") as f:
        f.write("\n".join(lines))
    return full


async def main():
    if len(sys.argv) < 2:
        print("用法: python3 extract_douyin.py <抖音链接或aweme_id>")
        sys.exit(1)
    arg = sys.argv[1]
    if arg.startswith("http"):
        if "v.douyin.com" in arg or "/share/" in arg:
            resolved = await resolve_short_url(arg)
            print(f"[解析] {arg} → {resolved}")
            aweme_id = extract_aweme_id(resolved)
        else:
            aweme_id = extract_aweme_id(arg)
    else:
        aweme_id = arg
    print(f"[目标] aweme_id={aweme_id}")

    video_url, title, desc = await get_video_url(aweme_id)
    if not video_url:
        print("❌ 未获取到视频URL")
        sys.exit(1)
    print(f"[视频] {video_url[:100]}")
    if desc:
        print(f"[描述] {desc[:200]}")

    mp4 = "/tmp/douyin_video.mp4"
    if not download_video(video_url, mp4):
        print("❌ 视频下载失败")
        sys.exit(1)
    print(f"[下载] {mp4} ({os.path.getsize(mp4)//1024}KB)")

    wav = "/tmp/douyin_audio.wav"
    if not extract_audio(mp4, wav):
        print("❌ 音频提取失败")
        sys.exit(1)
    print(f"[音频] {wav}")

    full = transcribe(wav, "/tmp/douyin_transcript.txt")
    print(f"\n════ 口播文案（{len(full)}字）════")
    print(full)
    print(f"\n[保存] /tmp/douyin_transcript.txt")


if __name__ == "__main__":
    asyncio.run(main())
