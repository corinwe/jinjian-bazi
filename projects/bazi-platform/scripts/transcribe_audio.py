#!/usr/bin/env python3
"""
金鉴真人·音频转录工具 v1.0
用法: python3 transcribe_audio.py <音频文件路径> [--model small|medium|base] [--output 输出路径]
     python3 transcribe_audio.py --test   (生成测试音频并转录验证)

功能: 将音频文件转写为文字，自动检测语言，输出带时间戳的文本
"""

import sys, os, time, json, argparse
from faster_whisper import WhisperModel

CACHE_DIR = os.path.expanduser("~/.cache/whisper-models")

def transcribe(audio_path, model_size="small", output_path=None, verbose=True):
    """转写音频文件为文字"""
    if not os.path.exists(audio_path):
        print(f"❌ 文件不存在: {audio_path}")
        return None
    
    file_size = os.path.getsize(audio_path)
    if verbose:
        print(f"🎵 音频文件: {audio_path}")
        print(f"📦 文件大小: {file_size/1024:.1f} KB")
        print(f"🤖 模型: {model_size}")
        print(f"{'='*50}")
    
    # 加载模型
    if verbose: print("🔄 加载模型中...", end=" ", flush=True)
    start = time.time()
    model = WhisperModel(model_size, device='cpu', compute_type='int8', 
                         download_root=CACHE_DIR)
    if verbose: print(f"✅ ({time.time()-start:.1f}s)")
    
    # 转录
    if verbose: print("🎤 转录中...", end=" ", flush=True)
    start = time.time()
    segments, info = model.transcribe(audio_path, beam_size=5, vad_filter=True)
    elapsed = time.time() - start
    
    # 收集结果
    full_text = ""
    segment_list = []
    for seg in segments:
        ts = f"[{seg.start:.1f}s -> {seg.end:.1f}s]"
        segment_list.append({"start": seg.start, "end": seg.end, "text": seg.text.strip()})
        full_text += seg.text.strip() + "\n"
    
    if verbose:
        print(f"✅ ({elapsed:.1f}s)")
        print(f"🌐 语言: {info.language} (概率: {info.language_probability:.1%})")
        print(f"📊 转录用时: 音频时长 / 处理时间 = ???")
        print(f"📝 全文({len(full_text)}字):")
        for seg in segment_list:
            print(f"  [{seg['start']:.1f}s-{seg['end']:.1f}s] {seg['text']}")
    
    # 输出
    result = {
        "language": info.language,
        "language_probability": info.language_probability,
        "duration": elapsed,
        "segments": segment_list,
        "full_text": full_text.strip()
    }
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            if output_path.endswith('.json'):
                json.dump(result, f, ensure_ascii=False, indent=2)
            else:
                f.write(f"# 音频转录结果\n")
                f.write(f"## 源文件: {audio_path}\n")
                f.write(f"## 语言: {info.language} ({info.language_probability:.1%})\n")
                f.write(f"## 转录时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for seg in segment_list:
                    f.write(f"[{seg['start']:.1f}s] {seg['text']}\n")
        if verbose: print(f"\n💾 已保存: {output_path}")
    
    return result


def generate_test_audio():
    """生成测试音频"""
    test_text = (
        "您好，我是金鉴真人。今天我们来学习八字命理中的身强身弱判断方法。"
        "首先我们需要看月令的能量，然后看其他天干地支的生助和消耗。"
        "这是九龙道长的原始方法论，非常精准。身强身弱的判断是八字分析的第一步，"
        "也是最关键的一步。身强的人喜克泄耗，身弱的人喜生助帮扶。"
    )
    test_file = "/tmp/whisper_test/test_chinese.mp3"
    os.makedirs("/tmp/whisper_test", exist_ok=True)
    
    print("🔄 生成测试音频...")
    os.system(f'edge-tts --voice zh-CN-XiaoxiaoNeural --text "{test_text}" --write-media {test_file} 2>/dev/null')
    print(f"✅ 测试音频已生成: {test_file}")
    return test_file


def main():
    parser = argparse.ArgumentParser(description="金鉴真人·音频转录工具")
    parser.add_argument("audio_file", nargs="?", help="音频文件路径")
    parser.add_argument("--model", default="small", choices=["base", "small", "medium"],
                        help="Whisper模型大小 (默认: small)")
    parser.add_argument("--output", "-o", help="输出文件路径 (.txt 或 .json)")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    if args.test:
        audio_file = generate_test_audio()
        transcribe(audio_file, args.model, args.output)
    elif args.audio_file:
        transcribe(args.audio_file, args.model, args.output)
    else:
        parser.print_help()
        print("\n示例:")
        print("  python3 transcribe_audio.py 录音.mp3")
        print("  python3 transcribe_audio.py 录音.mp3 --model medium -o 转录结果.txt")
        print("  python3 transcribe_audio.py --test")


if __name__ == "__main__":
    main()
