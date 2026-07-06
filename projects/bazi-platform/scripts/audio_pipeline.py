#!/usr/bin/env python3
"""
金鉴真人·音频全流水线工具 v2.0
=============================
完整流程：永久存档 → 逐字转写 → 知识点提取

用法:
  # 完整流水线（默认）
  python3 audio_pipeline.py <音频文件路径> [--name "课程名称"]

  # 测试验证
  python3 audio_pipeline.py --test

输出目录结构:
  ~/永维基音频库/YYYY-MM-DD_课程名称/
    ├── 原始音频/
    │   └── 课程名称_原始音频.m4a
    ├── 逐字转写.txt          ← 带时间戳的完整转写
    └── 知识点提取.md          ← 逐字逐句知识提取报告

知识点提取格式（对标之前的Word文档处理）:
  ### 【知识点N】知识点名称
  - **原文精读**：引述原文关键段落
  - **体系归类**：所属命理体系（十神/格局/神煞/大运等）
  - **覆盖状态**：【已掌握】/【新发现】/【补充细节】
  - **案例佐证**：若有案例则附上
"""

import sys, os, re, json, time, shutil, argparse
from datetime import datetime
from pathlib import Path
from faster_whisper import WhisperModel

# ============ 配置 ============
ARCHIVE_ROOT = os.path.expanduser("~/永维基音频库")
CACHE_DIR = os.path.expanduser("~/.cache/whisper-models")
DEFAULT_MODEL = "small"

# ============ 第1步：永久存档 ============
def archive_audio(audio_path, course_name):
    """将原始音频永久存档"""
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None, None
    
    # 确定目录名：日期_课程名
    today = datetime.now().strftime("%Y-%m-%d")
    dir_name = f"{today}_{course_name}" if course_name else f"{today}_未命名音频"
    archive_dir = os.path.join(ARCHIVE_ROOT, dir_name)
    audio_dir = os.path.join(archive_dir, "原始音频")
    os.makedirs(audio_dir, exist_ok=True)
    
    # 复制音频文件
    ext = os.path.splitext(audio_path)[1] or ".m4a"
    dest_name = f"{course_name or '音频'}_原始{ext}"
    dest_path = os.path.join(audio_dir, dest_name)
    shutil.copy2(audio_path, dest_path)
    
    file_size = os.path.getsize(dest_path)
    print(f"📦 音频已存档: {dest_path}")
    print(f"   大小: {file_size/1024:.1f} KB")
    
    return archive_dir, dest_path


# ============ 第2步：逐字转写 ============
def transcribe_audio(audio_path, archive_dir, course_name, model_size=DEFAULT_MODEL):
    """将音频转写为完整文字"""
    print(f"\n{'='*50}")
    print(f"🎤 逐字转写中...")
    print(f"{'='*50}")
    
    # 加载模型
    print(f"🤖 模型: {model_size}")
    model = WhisperModel(model_size, device='cpu', compute_type='int8', download_root=CACHE_DIR)
    
    # 转写
    segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
    
    # 收集结果
    segment_list = []
    full_text_lines = []
    for seg in segments:
        ts = f"[{seg.start:.1f}s]"
        text = seg.text.strip()
        segment_list.append({"start": seg.start, "end": seg.end, "text": text})
        full_text_lines.append(f"{ts} {text}")
    
    full_text = "\n".join(full_text_lines)
    
    # 保存逐字转写文件
    transcript_path = os.path.join(archive_dir, "逐字转写.txt")
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(f"# 逐字转写\n")
        f.write(f"## 课程: {course_name or '未命名'}\n")
        f.write(f"## 源文件: {os.path.basename(audio_path)}\n")
        f.write(f"## 转写语言: {info.language} (置信度: {info.language_probability:.1%})\n")
        f.write(f"## 转写时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"## 模型: {model_size}\n")
        f.write(f"\n---\n\n")
        for seg in segment_list:
            f.write(f"[{seg['start']:.1f}s] {seg['text']}\n")
    
    print(f"🌐 语言: {info.language} ({info.language_probability:.1%})")
    print(f"📝 全文长度: {len(full_text)} 字符")
    print(f"💾 转写已保存: {transcript_path}")
    
    return transcript_path, full_text, segment_list


# ============ 第3步：知识点提取 ============
def extract_knowledge(transcript_path, archive_dir, course_name, full_text, segments):
    """从转写文本中逐字逐句提取知识点"""
    print(f"\n{'='*50}")
    print(f"🔍 知识点提取中...")
    print(f"{'='*50}")
    
    # 这是第一部分基础提取——时间戳分段+关键词标记
    # 详细的逐句分析由金鉴真人LLM完成，这里先做预处理
    
    # 基础分段统计
    total_chars = len(full_text)
    total_segments = len(segments)
    est_minutes = segments[-1]['end'] / 60 if segments else 0
    
    # 提取关键词标记（常见命理术语）
    bazi_terms = {
        "十神体系": ["正印", "偏印", "枭神", "食神", "伤官", "正官", "七杀", "偏官", 
                    "正财", "偏财", "比肩", "劫财", "吉神", "恶神", "平神"],
        "格局类": ["身强", "身弱", "从弱", "从强", "化气", "从格", "中和", "旺衰",
                  "得令", "得地", "得势", "调候", "用神", "忌神", "喜用"],
        "五行类": ["金木水火土", "相生", "相克", "生助", "消耗", "五行能量"],
        "神煞类": ["天乙贵人", "文昌", "华盖", "桃花", "驿马", "灾煞", "血刃",
                  "禄神", "空亡", "天德", "月德"],
        "大运流年": ["大运", "流年", "岁运", "应期", "引化", "合化", "三合", "六合",
                    "三会", "合局", "冲", "刑", "害"],
        "实战断事": ["断语", "口诀", "案例", "应事", "断法", "技法", "过三关"],
        "其他": ["墓库", "藏干", "透干", "通根", "纳音", "十二长生", "空亡"]
    }
    
    # 收集命理术语出现频次
    term_freq = {}
    for category, terms in bazi_terms.items():
        for term in terms:
            count = full_text.count(term)
            if count > 0:
                term_freq[term] = {"count": count, "category": category}
    
    # 按出现频率排序
    sorted_terms = sorted(term_freq.items(), key=lambda x: x[1]['count'], reverse=True)
    
    # 按类别聚合
    category_stats = {}
    for term, info in sorted_terms:
        cat = info['category']
        if cat not in category_stats:
            category_stats[cat] = {"terms": [], "total": 0}
        category_stats[cat]["terms"].append(f"{term}({info['count']}次)")
        category_stats[cat]["total"] += info['count']
    
    # 保存知识点提取基础报告
    extract_path = os.path.join(archive_dir, "知识点提取.md")
    
    with open(extract_path, 'w', encoding='utf-8') as f:
        f.write(f"# 知识点提取报告\n")
        f.write(f"## 课程: {course_name or '未命名'}\n")
        f.write(f"## 源文件: {os.path.basename(transcript_path)}\n")
        f.write(f"## 提取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"\n---\n\n")
        
        # 基础统计
        f.write(f"## 📊 基础统计\n\n")
        f.write(f"| 项目 | 数值 |\n")
        f.write(f"|:----|:----:|\n")
        f.write(f"| 音频时长 | ~{est_minutes:.1f} 分钟 |\n")
        f.write(f"| 转写字数 | {total_chars} 字符 |\n")
        f.write(f"| 分段数量 | {total_segments} 段 |\n")
        f.write(f"| 检测语言 | {segments[0]['text'] if segments else 'N/A'} |\n")
        f.write(f"\n")
        
        # 术语统计
        f.write(f"## 📖 命理术语热度\n\n")
        for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['total'], reverse=True):
            f.write(f"### {cat}（共{stats['total']}次）\n\n")
            f.write(f"{'、'.join(stats['terms'])}\n\n")
        
        # 空模板供LLM填充详细分析
        f.write(f"\n---\n\n")
        f.write(f"## 🔬 逐段精读与知识点提取\n\n")
        f.write(f"> ⬇️ 以下由金鉴真人LLM逐句分析填充\n\n")
        
        # 逐段标注（每段预留分析空间）
        f.write(f"### 一、逐段精读\n\n")
        for i, seg in enumerate(segments):
            ts = f"[{seg['start']:.1f}s-{seg['end']:.1f}s]"
            f.write(f"**{ts}** {seg['text']}\n\n")
            f.write(f"> 🔍 知识点：\n\n")
            f.write(f"---\n\n")
        
        # 综合总结模板
        f.write(f"### 二、综合总结\n\n")
        f.write(f"| # | 知识点名称 | 体系归类 | 覆盖状态 | 是否含案例 |\n")
        f.write(f"|---|:----------|:--------|:--------:|:---------:|\n")
        f.write(f"| 1 | | | | |\n\n")
        
        f.write(f"### 三、与现有技能交叉验证\n\n")
        f.write(f"| 体系 | ✅ 已覆盖 | 🔴 新发现 | ⚠️ 需更新 |\n")
        f.write(f"|:----|:--------:|:--------:|:--------:|\n")
        f.write(f"| 身强弱 | | | |\n")
        f.write(f"| 十神体系 | | | |\n")
        f.write(f"| 大运流年 | | | |\n")
        f.write(f"| 格局 | | | |\n")
        f.write(f"| 神煞 | | | |\n")
        f.write(f"| 婚姻 | | | |\n")
        f.write(f"| 财富 | | | |\n")
        f.write(f"| 事业 | | | |\n")
        f.write(f"| 健康 | | | |\n")
        f.write(f"| 其他 | | | |\n")
    
    print(f"📊 命理术语统计:")
    for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f"   {cat}: {stats['total']}次 — {'、'.join(stats['terms'][:5])}")
    
    print(f"💾 知识点提取模板已保存: {extract_path}")
    print(f"   ⚠️ 知识点填充需要 LLM 逐段精读完成")
    
    return extract_path, term_freq, category_stats


# ============ 主流程 ============
def full_pipeline(audio_path, course_name=None, model_size=DEFAULT_MODEL):
    """完整流水线：存档 → 转写 → 知识提取"""
    print(f"\n{'#'*50}")
    print(f"# 🔮 金鉴真人·音频全流水线")
    print(f"{'#'*50}\n")
    
    if not course_name:
        # 从文件名推断课程名
        base = os.path.splitext(os.path.basename(audio_path))[0]
        # 去除自动缓存前缀
        for prefix in ["audio_", "recording_", "voice_"]:
            if base.startswith(prefix):
                base = base[len(prefix):]
        course_name = base if base else "未命名音频"
    
    print(f"📋 课程: {course_name}")
    print(f"🎵 音频: {audio_path}")
    
    # 第1步：永久存档
    archive_dir, archived_path = archive_audio(audio_path, course_name)
    if not archive_dir:
        return None
    
    # 第2步：逐字转写
    transcript_path, full_text, segments = transcribe_audio(
        archived_path, archive_dir, course_name, model_size
    )
    
    # 第3步：知识点提取预处理
    extract_path, term_freq, category_stats = extract_knowledge(
        transcript_path, archive_dir, course_name, full_text, segments
    )
    
    # 输出总结
    print(f"\n{'='*50}")
    print(f"✅ 流水线完成!")
    print(f"{'='*50}")
    print(f"📂 存档目录: {archive_dir}")
    print(f"   ├── 原始音频/")
    print(f"   │   └── {os.path.basename(archived_path)}")
    print(f"   ├── 逐字转写.txt ({len(full_text)}字符)")
    print(f"   └── 知识点提取.md (模板待LLM填充)")
    print(f"{'='*50}")
    
    return {
        "archive_dir": archive_dir,
        "audio_path": archived_path,
        "transcript_path": transcript_path,
        "extract_path": extract_path,
        "full_text": full_text,
        "segments": segments,
        "course_name": course_name
    }


# ============ 命令行入口 ============
def main():
    parser = argparse.ArgumentParser(description="金鉴真人·音频全流水线")
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("--name", "-n", help="课程名称（用于目录命名）")
    parser.add_argument("--model", default=DEFAULT_MODEL, 
                        choices=["base", "small", "medium"],
                        help="Whisper模型 (默认: small)")
    parser.add_argument("--test", action="store_true", help="运行测试验证")
    
    args = parser.parse_args()
    
    if args.test:
        print("🔄 生成测试音频...")
        test_file = "/tmp/whisper_test_pipeline.mp3"
        os.makedirs("/tmp", exist_ok=True)
        test_text = (
            "您好，我是金鉴真人。今天我们来学习八字命理中的身强身弱判断方法。"
            "首先我们需要看月令的能量，然后看其他天干地支的生助和消耗。"
            "这是九龙道长的原始方法论，非常精准。"
        )
        os.system(f'edge-tts --voice zh-CN-XiaoxiaoNeural --text "{test_text}" --write-media {test_file} 2>/dev/null')
        result = full_pipeline(test_file, "测试_身强身弱判断", args.model)
        # 清理测试文件
        os.remove(test_file)
    elif args.audio_file:
        result = full_pipeline(args.audio_file, args.name, args.model)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 audio_pipeline.py 上课录音.mp3")
        print("  python3 audio_pipeline.py 上课录音.mp3 --name \"九龙道长·十神课程\"")
        print("  python3 audio_pipeline.py 上课录音.mp3 --model medium")
        print("  python3 audio_pipeline.py --test")


if __name__ == "__main__":
    main()
