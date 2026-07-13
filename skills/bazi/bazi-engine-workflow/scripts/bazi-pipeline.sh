#!/bin/bash
# 金鉴真人·全流程主控脚本 v1.0
# 安装路径：该脚本与 bazi-engine.py 同目录
# 详细文档：bazi-engine-workflow/SKILL.md §全流程物理锁死
# 功能：唯一官方入口，自动串联排盘→验证→生成context→回检→全量验证→推库
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# ...（完整脚本内容请查看 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-pipeline.sh）
echo "bazi-pipeline.sh - 请直接从 /root/.hermes/profiles/jinjian-zhenren/scripts/bazi-pipeline.sh 运行"
echo "此文件为知识库副本，运行请使用主目录下的原始脚本"
