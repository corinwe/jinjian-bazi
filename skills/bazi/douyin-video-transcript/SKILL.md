---
name: douyin-video-transcript
description: 抖音视频口播文案提取五步法（2026-08-02突破·对荀太虚等教学视频有效）。核心：Playwright移动端UA访问iesdouyin.com/share（绕过桌面端反爬）→提取ROUTER_DATA拿真实视频URL→curl下载MP4→ffmpeg提音频→faster-whisper转文字。适用：老板发来的抖音教学/命理/国学视频，需逐字提取口播文案沉淀知识库。
tags: [douyin,视频提取,文案,whisper,playwright,口播转写]
---

# 抖音视频口播文案提取五步法

## 触发条件
- 老板发来抖音链接要求"提取文案/看内容/沉淀"
- 教学/讲解类视频（口播在音频里，页面文本只有标题描述）

## 前置环境
- playwright（async API）
- ffmpeg
- faster-whisper（模型缓存medium，首次自动下载约1.5GB）

## 五步流程

### Step 1: Playwright移动端打开分享页
```python
from playwright.async_api import async_playwright
# 必须用移动端UA + iesdouyin.com/share（桌面端www.douyin.com被反爬拦截）
ua = "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
await page.goto(f'https://www.iesdouyin.com/share/video/{aweme_id}', wait_until='domcontentloaded', timeout=30000)
await page.wait_for_timeout(5000)
```
- aweme_id从分享链接跳转后URL提取（/video/7644336490964618502）

### Step 2: 提取真实视频URL（二选一）
**方法A（推荐）**：页面内嵌ROUTER_DATA
```js
// 找 window._ROUTER_DATA 或 script#RENDER_DATA
const t = script.textContent;
const m = t.match(/window\._ROUTER_DATA = (\{.*\})/s);
```
在JSON中搜 `play_addr` → `url_list` → `aweme.snssdk.com/aweme/v1/playwm/?video_id=...`

**方法B**：直接读video标签
```js
document.querySelector('video').src  // 移动端会直接给playwm URL（桌面端是blob不可用）
```

### Step 3: curl下载MP4
```bash
curl -sL "https://aweme.snssdk.com/aweme/v1/playwm/?video_id=XXXX&ratio=720p&line=0" \
  -H "User-Agent: <移动端UA>" -H "Referer: https://www.iesdouyin.com/" \
  -o /tmp/douyin_video.mp4 --max-time 60
```
- playwm是带水印版，直接可下载（HTTP 200，10MB左右/分钟级视频）

### Step 4: ffmpeg提取音频
```bash
ffmpeg -y -i /tmp/douyin_video.mp4 -vn -acodec pcm_s16le -ar 16000 -ac 1 /tmp/douyin_audio.wav
```

### Step 5: faster-whisper转文字
```python
from faster_whisper import WhisperModel
model = WhisperModel("medium", device="cpu", compute_type="int8")
segments, info = model.transcribe("/tmp/douyin_audio.wav", language="zh", beam_size=5)
for seg in segments:
    print(f"[{seg.start:.1f}-{seg.end:.1f}] {seg.text}")
```
- medium模型中文精度好；时间紧可降small
- 同音字需人工修正（如"真权"→"真诠"、"伦语"→"论语"）

## 常见失败路径（勿走弯路）
| 路径 | 结果 | 原因 |
|:-----|:-----|:-----|
| Hermes内置浏览器开www.douyin.com | ❌ 登录墙/反爬 | 桌面端需登录 |
| Playwright桌面端UA | ❌ video readyState=0 | 视频源不加载 |
| 抖音REST API（iesdouyin iteminfo） | ❌ encrypt_data_miss | 需X-Bogus签名 |
| 浏览器console fetch | ❌ 安全策略拦截 | 需allow_unsafe_evaluate |
| tikwm等第三方解析 | ⚠️ 不稳定 | URL解析常失败 |
| yt-dlp | ❌ 需cookies | 登录墙 |
| **移动端分享页** | ✅ **成功** | **分享页无登录墙，SSR直出数据** |

## 验证
- 转写文本与视频时长匹配（45秒≈200-300字口播；16分钟≈4000-5000字）
- 修正同音字后保存文案到知识库（04-金鉴真人体系/ 或对应目录）
- 汇报时附：视频时长+口播字数+核心论点提炼

## 实战Pitfalls（2026-08-02实战发现）

### P1: 一键脚本可能静默失败/超时 → 分步调试
- extract_douyin.py 对部分视频会无输出直接退出（短链解析或页面加载hang）
- **对策**：脚本失败时不要反复重跑，改为分步手动：
  1. 短链解析：Playwright移动端goto短链→page.url取aweme_id（正则\d{15,20}）
  2. 拿video_url：访问`https://www.iesdouyin.com/share/video/{id}`→提取`window._ROUTER_DATA`→搜`play_addr.url_list[0]`（playwm链接）；或读video标签src
  3. curl下载（移动端UA+Referer: https://www.iesdouyin.com/）
  4. ffmpeg提音频 → whisper转写

### P2: 长视频转写必须用后台任务
- medium模型CPU转写约**1分钟音频≈1分钟计算**（16分钟视频≈17分钟）
- 前台terminal timeout=600s会杀进程（**被杀时输出文件可能未写入**）
- **对策**：写转写脚本到文件→`terminal(background=true, notify_on_complete=true)`→process wait/poll等待；或加`vad_filter=True`（跳过静音段，明显加速）
- 转写后先检查输出文件是否生成（`ls -la`），不要只信stdout

### P3: 同音字必须人工修正
- whisper中文同音字错误常见：真权→真诠、伦语→论语、银身→寅申、挡口→档口、洗用→喜用、声望→身旺、硬→印、纪神→忌神、才心→财星、相关→伤官
- **对策**：转写后通读修正同音字再入库；命理术语尤其要校（印/杀/官/财/食伤/身强弱/喜用忌神）

### P4: stdout被tail截断≠转写失败
- `python3 x.py 2>&1 | tail -70`只显示末尾——长视频文案要看完整文件
- **对策**：转写同时写入txt文件，用read_file分段读取完整内容

## 案例
- 2026-08-02 荀太虚《详解〈子平真诠〉》第1集：45.5秒/236字——playwm URL下载10.7MB MP4 → medium转写成功
- 2026-08-02 荀太虚《深度分析人生能量》：15分54秒/4778字——75MB MP4 → 后台转写成功（案例八字庚申壬午己巳丙寅，方法论沉淀到 bazi-foundation-analysis/references/taixu-duanming-method_20260802.md）
