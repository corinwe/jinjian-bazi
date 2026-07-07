#!/bin/bash
# bazi-report-template 知识库全量同步脚本
# 每次修改本技能包后执行：bash scripts/sync-knowledge-base.sh

SRC="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/skills/bazi-report-template"
DST="/root/.hermes/weiwuji-knowledge-base/07-国学哲学/八字命格/04-金鉴真人体系/技能包/bazi-report-template"

echo "🔄 同步 SKILL.md..."
cp "$SRC/SKILL.md" "$DST/SKILL.md"

echo "🔄 同步 scripts/..."
mkdir -p "$DST/scripts"
for f in "$SRC"/scripts/*.sh "$SRC"/scripts/*.py; do
  if [ -f "$f" ]; then
    cp "$f" "$DST/scripts/"
    echo "  ✅ $(basename "$f")"
  fi
done

# 清理知识库中已废弃的目录（references/ templates/）
if [ -d "$DST/references" ]; then
  echo "🧹 清理废弃的 references/ 目录..."
  rm -rf "$DST/references"
fi
if [ -d "$DST/templates" ]; then
  echo "🧹 清理废弃的 templates/ 目录..."
  rm -rf "$DST/templates"
fi

echo ""
echo "✅ 同步完成"
echo "📁 知识库：$DST"
echo ""
echo "📊 文件清单："
find "$DST" -type f | sort
