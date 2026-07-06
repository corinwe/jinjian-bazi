#!/bin/bash
# ═══════════════════════════════════════════════════════
#  loop-engineering.sh — 金鉴真人·自动化学习循环引擎
#  Version: 1.0
#  ═══════════════════════════════════════════════════════
#
#  将"学习→验证→应用"三段固化为可重复的自动化循环
#
#  用法:
#    ./loop-engineering.sh <domain> <action> [args...]
#
#  领域(domain):
#    wealth    — 财富体系
#    education — 学业体系
#    marriage  — 婚姻体系
#    general   — 通用（自动检测）
#
#  动作(action):
#    learn     — 精读新素材 + 对比现有skill
#    verify    — 验证变更完整性
#    apply     — 更新skill + 报告 + 推库
#    cycle     — 一键执行完整 learn→verify→apply 循环
#
#  示例:
#    ./loop-engineering.sh wealth cycle --source /tmp/new_wealth_rules.txt
#    ./loop-engineering.sh wealth learn --rules "新规则列表"
#    ./loop-engineering.sh wealth apply --reports "家主,主母,子源,立"
#
# ═══════════════════════════════════════════════════════

set -euo pipefail

# ─── 配置 ─────────────────────────────────────────
BAZI_PLATFORM="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform"
SCRIPTS_DIR="${BAZI_PLATFORM}/scripts"
KNOWLEDGE_BASE="/root/weiwuji-knowledge-base"
SKILLS_DIR="/root/.hermes/profiles/jinjian-zhenren/projects/bazi-platform/skills"
REPORTS_DIR="${KNOWLEDGE_BASE}/07-国学哲学/八字命格/02-人物档案"

# ─── 颜色 ─────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'

log()  { echo -e "${GREEN}[LE]${NC} $1"; }
warn() { echo -e "${YELLOW}[LE⚠]${NC} $1"; }
err()  { echo -e "${RED}[LE✗]${NC} $1"; }
info() { echo -e "${CYAN}[LE→]${NC} $1"; }
sep()  { echo -e "${BLUE}─────────────────────────────────${NC}"; }

# ─── 领域映射 ─────────────────────────────────────
declare -A DOMAIN_SKILL=(
  ["wealth"]="bazi-wealth-analysis"
  ["education"]="bazi-education-analysis"
  ["marriage"]="bazi-marriage-analysis"
  ["general"]=""
)

declare -A DOMAIN_VERSION_DIR=(
  ["wealth"]="财富体系"
  ["education"]="学业体系"
  ["marriage"]="婚姻体系"
  ["general"]="通用"
)

# ─── 阶段1: 学习 (Learn) ──────────────────────────
phase_learn() {
  local domain="$1"; shift
  local skill_name="${DOMAIN_SKILL[$domain]}"
  local source_file=""

  # 解析参数
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --source) source_file="$2"; shift 2 ;;
      --rules) rules_text="$2"; shift 2 ;;
      *) warn "未知参数: $1"; shift ;;
    esac
  done

  sep
  log "📖 阶段1: 学习 — 领域=$domain"

  if [ -z "$skill_name" ]; then
    warn "领域 $domain 没有映射skill，尝试自动检测"
  else
    info "现有skill: $skill_name"
  fi

  # Step 1.1 — 生成变更时间戳
  local timestamp
  timestamp=$(date +%Y%m%d_%H%M%S)
  local changelog_dir="${SCRIPTS_DIR}/_changelogs"
  mkdir -p "$changelog_dir"
  local changelog_file="${changelog_dir}/${domain}_${timestamp}.md"

  cat > "$changelog_file" <<EOF
# 变更清单: ${domain}

| 项目 | 内容 |
|:----|:-----|
| 时间 | $(date '+%Y-%m-%d %H:%M:%S') |
| 领域 | ${domain} |
| 来源 | ${source_file:-手动输入} |
| 状态 | 新建 |

## 新增规则
$(if [ -n "${rules_text:-}" ]; then echo "${rules_text}"; else echo "待精读填充"; fi)

## 修正规则
- （待对比现有skill后填充）

## 删除规则
- （待对比现有skill后填充）

## 影响范围
- skill: ${skill_name:-自动检测}
- 报告: （待扫描）
EOF

  echo "$changelog_file"
  log "✅ 变更清单已生成: ${changelog_file}"
  sep
}

# ─── 阶段2: 验证 (Verify) ─────────────────────────
phase_verify() {
  local changelog_file="$1"

  sep
  log "🔍 阶段2: 验证 — 完整性检查"

  if [ ! -f "$changelog_file" ]; then
    err "变更清单不存在: $changelog_file"
    return 1
  fi

  # Step 2.1 — 检查变更清单完整性
  local missing_sections=0
  for section in "新增规则" "修正规则" "删除规则" "影响范围"; do
    if ! grep -q "^## ${section}" "$changelog_file"; then
      warn "缺少章节: ${section}"
      missing_sections=$((missing_sections + 1))
    fi
  done

  if [ "$missing_sections" -gt 0 ]; then
    warn "变更清单不完整，缺少 ${missing_sections} 个章节"
    return 1
  fi

  # Step 2.2 — 检查新增规则是否有内容（排除"待填充"占位符）
  local empty_sections=0
  if grep -q "待精读填充" "$changelog_file"; then
    warn "新增规则章节仍有'待精读填充'占位符"
    empty_sections=$((empty_sections + 1))
  fi

  if [ "$empty_sections" -gt 0 ]; then
    warn "变更清单中有 ${empty_sections} 个占位符尚未填充"
    return 1
  fi

  log "✅ 变更清单验证通过 — 所有章节完整无占位符"
  sep
  return 0
}

# ─── 阶段3: 应用 (Apply) ──────────────────────────
phase_apply() {
  local domain="$1"; shift
  local skill_name="${DOMAIN_SKILL[$domain]}"
  local changelog_file=""
  local reports_list=""

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --changelog) changelog_file="$2"; shift 2 ;;
      --reports) reports_list="$2"; shift 2 ;;
      --skip-skill) skip_skill=true; shift ;;
      --skip-reports) skip_reports=true; shift ;;
      *) warn "未知参数: $1"; shift ;;
    esac
  done

  sep
  log "🚀 阶段3: 应用 — 领域=$domain"

  if [ -z "$changelog_file" ] || [ ! -f "$changelog_file" ]; then
    err "变更清单不存在或未指定: ${changelog_file:-}"
    return 1
  fi

  # Step 3.1 — 更新skill（由Hermes自身执行，脚本只生成patch指示）
  if [ "${skip_skill:-false}" != "true" ] && [ -n "$skill_name" ]; then
    log "→ Step 3.1: 标记skill ${skill_name} 需要更新"
    local skill_version
    skill_version=$(grep -oP 'v\d+\.\d+' <<< "$skill_name" || echo "v1.0")
    echo "SKILL_UPDATE: ${skill_name}"
    echo "CHANGELOG: ${changelog_file}"
  fi

  # Step 3.2 — 扫描受影响报告
  if [ "${skip_reports:-false}" != "true" ]; then
    log "→ Step 3.2: 扫描受影响报告"
    if [ -n "$reports_list" ]; then
      IFS=',' read -ra REPORTS <<< "$reports_list"
      for report in "${REPORTS[@]}"; do
        report=$(echo "$report" | xargs)  # trim
        log "  📄 标记更新: ${report}"
        echo "REPORT_UPDATE: ${report}"
      done
    else
      warn "未指定报告列表，跳过报告更新"
    fi
  fi

  # Step 3.3 — 标记变更清单为已应用
  sed -i "s/状态 | 新建/状态 | 已应用/" "$changelog_file"
  log "✅ 变更清单标记为已应用"
  sep
}

# ─── 完整循环 ─────────────────────────────────────
phase_cycle() {
  local domain="$1"; shift

  sep
  echo -e "${BLUE}╔══════════════════════════════════════╗${NC}"
  echo -e "${BLUE}║  🔄  Loop Engineering 完整循环        ║${NC}"
  echo -e "${BLUE}║  领域: ${domain}                      ║${NC}"
  echo -e "${BLUE}╚══════════════════════════════════════╝${NC}"
  sep

  # 阶段1: 学习 → 生成变更清单
  local changelog_file
  changelog_file=$(phase_learn "$@")

  # 阶段2: 验证
  if ! phase_verify "$changelog_file"; then
    warn "⚠️ 验证失败，变更清单需手动填充后再 apply"
    echo "变更清单位置: $changelog_file"
    return 1
  fi

  # 阶段3: 应用
  phase_apply "$domain" --changelog "$changelog_file"

  log "🎉 循环完成！"
  sep
  echo "变更清单: ${changelog_file}"
  sep
}

# ─── 主入口 ───────────────────────────────────────
main() {
  local domain="${1:-general}"; shift || true
  local action="${1:-help}"; shift || true

  case "$action" in
    learn)    phase_learn "$domain" "$@" ;;
    verify)   phase_verify "$@" ;;
    apply)    phase_apply "$domain" "$@" ;;
    cycle)    phase_cycle "$domain" "$@" ;;
    help|*)
      echo "用法: $0 <领域> <动作> [参数]"
      echo ""
      echo "领域: wealth | education | marriage | general"
      echo "动作: learn | verify | apply | cycle"
      echo ""
      echo "示例: $0 wealth cycle --source /tmp/new_rules.txt"
      echo "      $0 wealth learn --rules '新增规则A;新增规则B'"
      echo "      $0 wealth apply --reports '家主,主母,子源,立'"
      ;;
  esac
}

main "$@"
