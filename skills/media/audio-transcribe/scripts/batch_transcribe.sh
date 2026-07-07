#!/bin/bash
# 金鉴真人·批量转写脚本（用于有10份音频需顺序处理时）
# 按文件大小从小到大顺序转写，每个完成后记录日志
# 
# 用法：
#   bash batch_transcribe.sh /path/to/audio/dir
#   或直接启动（自动使用 profile 的 cache/audio/ 目录）
#
# 说明：
#   - 按文件大小从小到大转写（最小的先跑，快速验证管线）
#   - 每个文件完成后记录日志到 transcribe_progress.log
#   - 已转写的文件自动跳过（检查永维基音频库目录）
#   - 转写中断后重新运行会自动跳过已完成项

HERMES_HOME=${HERMES_HOME:-/root/.hermes/profiles/jinjian-zhenren}
AUDIO_DIR="${1:-$HERMES_HOME/cache/audio}"
LOG_FILE="${2:-$HERMES_HOME/cache/transcribe_progress.log}"
PIPELINE=$HERMES_HOME/scripts/audio_pipeline.py
ARCHIVE_ROOT=~/永维基音频库

echo "=== 批量转写开始 $(date) ===" | tee -a "$LOG_FILE"
echo "音频目录: $AUDIO_DIR" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"

# 按文件大小从小到大排序（最快验证管线）
for audio in $(ls -Sr "$AUDIO_DIR"/*.m4a 2>/dev/null); do
  fname=$(basename "$audio")
  
  # 检查是否已转写
  already_done=false
  if [ -d "$ARCHIVE_ROOT" ]; then
    for dir in "$ARCHIVE_ROOT"/*; do
      if [ -f "$dir/逐字转写.txt" ] && [ -f "$dir/原始音频/$fname" ]; then
        already_done=true
        break
      fi
    done
  fi
  
  if $already_done; then
    echo "⏭️  跳过已转写: $fname" | tee -a "$LOG_FILE"
    continue
  fi
  
  echo "🎤 开始转写: $fname ($(du -h "$audio" | cut -f1))" | tee -a "$LOG_FILE"
  
  # 用占位名启动转写（先跑内容再命名）
  python3 -u "$PIPELINE" "$audio" --name "九龙道长新课_${fname%.m4a}" 2>&1 | tee -a "$LOG_FILE"
  
  exit_code=${PIPESTATUS[0]}
  if [ $exit_code -eq 0 ]; then
    echo "✅ 完成: $fname $(date)" | tee -a "$LOG_FILE"
  else
    echo "❌ 失败(exit=$exit_code): $fname $(date)" | tee -a "$LOG_FILE"
  fi
  
  echo "---" >> "$LOG_FILE"
  df -h / | tail -1 >> "$LOG_FILE"
done

echo "=== 批量转写全部完成 $(date) ===" | tee -a "$LOG_FILE"
