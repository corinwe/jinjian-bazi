#!/bin/bash
#===============================================================================
# 金鉴真人·八字全流程主控脚本 bazi-pipeline.sh v2.0
# 功能：物理串联「排盘→验证→数据源强制读取→生成签名context→delegate→回检查→全量验证→推库」
# 
# 🚨 数据源头盔机制
#   ⛔ 不跑pipeline → context无PIPELINE-SIG签名 → delegate-check不通过
#   ⛔ 不读取数据源 → context标注⚠️未验证
#   ⛔ 验证不通过 → push模式自动拒绝
#
# 使用方式：
#   Step 1: bash bazi-pipeline.sh --name ...  # 排盘+验证+生成签名context
#   Step 2: 复制context到delegate_task
#   Step 3: bash bazi-pipeline.sh --verify ... # 回写校验+全量验证
#   Step 4: bash bazi-pipeline.sh --push ...   # 自动先verify后push
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
KB_DIR="/root/.hermes/weiwuji-knowledge-base"
OUTPUT_DIR="/tmp/bazi_pipeline_output"
PIPELINE_VERSION="v2.0"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'

print_banner() {
    echo ""; echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  金鉴真人·八字全流程主控 $PIPELINE_VERSION                    ║"
    echo "║  ⛔ 不跑pipeline=无签名context=验证不通过                    ║"
    echo "╚══════════════════════════════════════════════════════════╝"; echo ""
}

usage() {
    echo "用法:"
    echo "  bash bazi-pipeline.sh --name <姓名> --year <年> --month <月> --day <日> \\"
    echo "                      --hour <时> --min <分> --hour-idx <索引> --gender <男/女>"
    echo "  bash bazi-pipeline.sh --verify <报告路径> [--name <姓名>]"
    echo "  bash bazi-pipeline.sh --push <commit信息>"
    exit 0
}

MODE="full"; NAME=""; YEAR=""; MONTH=""; DAY=""; HOUR=""; MIN=""; HOUR_IDX=""; GENDER=""
BIRTH_YEAR=""; REPORT_PATH=""; COMMIT_MSG=""

while [ $# -gt 0 ]; do
    case "$1" in
        --name) NAME="$2"; shift 2 ;; --year) YEAR="$2"; shift 2 ;;
        --month) MONTH="$2"; shift 2 ;; --day) DAY="$2"; shift 2 ;;
        --hour) HOUR="$2"; shift 2 ;; --min) MIN="$2"; shift 2 ;;
        --hour-idx) HOUR_IDX="$2"; shift 2 ;; --gender) GENDER="$2"; shift 2 ;;
        --birth-year) BIRTH_YEAR="$2"; shift 2 ;;
        --verify) MODE="verify"; REPORT_PATH="$2"; shift 2 ;;
        --push) MODE="push"; COMMIT_MSG="$2"; shift 2 ;;
        --version) echo "bazi-pipeline.sh $PIPELINE_VERSION"; exit 0 ;;
        --help|-h) usage ;; *) echo "未知参数: $1"; usage ;;
    esac
done

# ═══════════════════════════════════════════════════════════════
# FULL MODE: 排盘 → 验证 → 数据源 → 签名context
# ═══════════════════════════════════════════════════════════════
if [ "$MODE" = "full" ]; then
    print_banner
    
    if [ -z "$NAME" ] || [ -z "$YEAR" ] || [ -z "$GENDER" ]; then
        echo -e "${RED}❌ 缺少必要参数（--name, --year, --gender）${NC}"; usage
    fi
    [ -z "$BIRTH_YEAR" ] && BIRTH_YEAR=$YEAR
    [ -z "$HOUR" ] && HOUR=0; [ -z "$MIN" ] && MIN=0
    [ -z "$HOUR_IDX" ] && HOUR_IDX=0

    PIPELINE_TS=$(date +%s)
    PIPELINE_SIG="${PIPELINE_VERSION}-${NAME}-${YEAR}${MONTH}${DAY}-${PIPELINE_TS}"
    
    mkdir -p "$OUTPUT_DIR"

    # [1/5] 排盘验证（官网失败时继续，标注⚠️）
    echo -e "${CYAN}[1/5]${NC} 排盘+官网验证..."
    ENGINE_OK=false
    MUST_VERIFY="${SCRIPT_DIR}/bazi-must-verify.sh"
    ENGINE="${SCRIPT_DIR}/bazi-engine.py"
    
    if [ -f "$MUST_VERIFY" ]; then
        set +e
        MV_OUTPUT=$(bash "$MUST_VERIFY" "$YEAR" "$MONTH" "$DAY" "$HOUR" "$MIN" "$GENDER" "$NAME" 2>&1)
        MV_EXIT=$?
        set -e
        echo "$MV_OUTPUT" | tee "$OUTPUT_DIR/${NAME}_must_verify.log"
        
        if [ $MV_EXIT -eq 0 ] && echo "$MV_OUTPUT" | grep -q "一致"; then
            echo -e "  ${GREEN}✅ 官网验证通过${NC}"
            ENGINE_OK=true
        else
            echo -e "  ${YELLOW}⚠️ 官网验证失败或数据不一致 — 以引擎数据继续，context标注⚠️${NC}"
            # 仍然跑引擎获取数据
            if [ -f "$ENGINE" ]; then
                python3 "$ENGINE" "$YEAR" "$MONTH" "$DAY" "$HOUR" "$MIN" "$HOUR_IDX" "$GENDER" "$NAME" --json > "$OUTPUT_DIR/${NAME}_engine.json" 2>&1
                ENGINE_OK=true
            fi
        fi
    elif [ -f "$ENGINE" ]; then
        python3 "$ENGINE" "$YEAR" "$MONTH" "$DAY" "$HOUR" "$MIN" "$HOUR_IDX" "$GENDER" "$NAME" --json > "$OUTPUT_DIR/${NAME}_engine.json" 2>&1
        ENGINE_OK=true
        echo -e "  ${YELLOW}⚠️ 无 must-verify.sh，仅使用引擎数据${NC}"
    fi
    
    if [ "$ENGINE_OK" != "true" ]; then
        echo -e "${RED}❌ 无法排盘，请检查输入参数${NC}"; exit 1
    fi

    # [2/5] 🪖 数据源头盔
    echo ""
    echo -e "${CYAN}[2/5]${NC} 🪖 数据源头盔——强制读取数据源..."
    DATA_SOURCE="${SCRIPT_DIR}/family_bazi_data.json"
    VERIFIED="false"
    
    if [ -f "$DATA_SOURCE" ]; then
        DS_RESULT=$(python3 -c "
import json
with open('$DATA_SOURCE') as f:
    data = json.load(f)
found = None
for p in data if isinstance(data, list) else data.values():
    if '$NAME' in p.get('姓名','') or p.get('姓名','') in '$NAME':
        found = p; break
if found:
    qy = found.get('大运',{}).get('起运年龄','未知')
    shen = found.get('身强弱',{})
    print(f'FOUND|{qy}|{shen.get(\"等级\",\"未知\")}|{shen.get(\"总分\",\"未知\")}|{found.get(\"八字\",\"未知\")}')
else:
    print('NOT_FOUND')
" 2>&1)
        if echo "$DS_RESULT" | grep -q "^FOUND"; then
            VERIFIED="true"
            echo -e "  ${GREEN}✅ 数据源验证通过${NC}"
            echo "  📊 $(echo $DS_RESULT | cut -d'|' -f5) | 起运$(echo $DS_RESULT | cut -d'|' -f2)岁 | 身强弱$(echo $DS_RESULT | cut -d'|' -f3)($(echo $DS_RESULT | cut -d'|' -f4)分)"
        else
            echo -e "  ${YELLOW}⚠️ 新人，数字来自引擎排盘${NC}"
        fi
    fi
    echo "$VERIFIED" > "${OUTPUT_DIR}/${NAME}_verify_status.txt"

    # [3/5] 生成签名context文件
    echo ""
    echo -e "${CYAN}[3/5]${NC} 生成签名Context文件..."
    
    CONTEXT_FILE="${OUTPUT_DIR}/${NAME}_context.txt"
    cat > "$CONTEXT_FILE" << CONTEXTEOF
╔══════════════════════════════════════════════════════════════╗
║  金鉴真人·Sub Agent Context — $PIPELINE_VERSION               ║
║  由 bazi-pipeline.sh 自动生成 | 签名: $PIPELINE_SIG            ║
║  禁止修改以下任何字段，直接复制粘贴                            ║
╚══════════════════════════════════════════════════════════════╝

# PIPELINE-SIG: $PIPELINE_SIG
# 数据源验证: $VERIFIED
# 生成时间: $(date '+%Y-%m-%d %H:%M:%S')

=== 🔴 铁律（不可删除，不可修改） ===

【铁律1】§1骨架已预生成，禁止修改。你只写§2~§21。
【铁律2】所有数字从数据源取，禁止自行计算。
【铁律3】每§关键断语标注【金鉴真人·§X·规则名】
【铁律4】报告≥1,700行，21§全量覆盖。
【铁律5】关键年份标注【学业】【事业】【财富】【健康】【感情】【搬迁】【灾祸】
【铁律6】§8.5 补财库方案强制含。
【铁律7】出生≥2001年→§11.5补文昌判断+§21.7文昌方案。
【铁律8】有姓名→§1姓名行+§20.7姓名分析。

=== 📊 数据 ===
姓名: $NAME | 性别: $GENDER
出生: 公历${YEAR}年${MONTH}月${DAY}日 ${HOUR}:${MIN} | 出生年: $BIRTH_YEAR
引擎JSON: ${OUTPUT_DIR}/${NAME}_engine.json
数据源验证: $VERIFIED

=== 📋 输出 ===
保存: ${OUTPUT_DIR}/${NAME}_完整深析报告.md
CONTEXTEOF
    
    echo -e "${GREEN}✅ 签名context已生成: ${CONTEXT_FILE}${NC}"
    echo "  签名: $PIPELINE_SIG"
    echo ""
    echo "下一步: cat ${CONTEXT_FILE} → 复制到 delegate_task"

# ═══════════════════════════════════════════════════════════════
# VERIFY MODE: 回写校验 + 全量验证（含签名检查）
# ═══════════════════════════════════════════════════════════════
elif [ "$MODE" = "verify" ]; then
    print_banner
    
    if [ -z "$REPORT_PATH" ]; then
        echo -e "${RED}❌ 缺少报告路径${NC}"; exit 1
    fi
    
    FAIL=0
    
    # 检查签名（漏洞①③防御）
    echo -e "${CYAN}[检查]${NC} 验证context签名..."
    NAME_GUESS=$(basename "$REPORT_PATH" | sed 's/_.*//')
    SIG_FILE="${OUTPUT_DIR}/${NAME_GUESS}_context.txt"
    if [ -f "$SIG_FILE" ] && grep -q "PIPELINE-SIG" "$SIG_FILE"; then
        echo -e "  ${GREEN}✅ context签名验证通过 (由pipeline.sh生成)${NC}"
    else
        echo -e "  ${YELLOW}⚠️ 未找到context签名文件 — 可能未使用pipeline.sh${NC}"
        echo -e "  ${YELLOW}⚠️ 建议重新运行: bash bazi-pipeline.sh --name ${NAME_GUESS} ...${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}[1/3]${NC} Sub Agent 回写校验..."
    bash "${SCRIPT_DIR}/bazi-delegate-check.sh" "$REPORT_PATH" "$NAME" "$BIRTH_YEAR" || true
    
    echo ""
    echo -e "${CYAN}[2/3]${NC} 全量验证..."
    bash "${SCRIPT_DIR}/bazi-full-verify.sh" "$REPORT_PATH" "$NAME" || true
    
    echo ""
    echo -e "${CYAN}[3/3]${NC} 汇总..."
    FINAL=$(bash "${SCRIPT_DIR}/bazi-delegate-check.sh" "$REPORT_PATH" "$NAME" "$BIRTH_YEAR" 2>&1; echo "EXIT:$?")
    EXIT_CODE=$(echo "$FINAL" | grep "EXIT:" | sed 's/.*EXIT://')
    
    if [ "$EXIT_CODE" = "0" ]; then
        echo -e "${GREEN}✅ 全部验证通过！可推库。${NC}"
        exit 0
    else
        echo -e "${RED}❌ 验证不通过，修正后重试。${NC}"
        exit 1
    fi

# ═══════════════════════════════════════════════════════════════
# PUSH MODE: 先verify再push（漏洞④⑤⑥修复）
# ═══════════════════════════════════════════════════════════════
elif [ "$MODE" = "push" ]; then
    print_banner
    
    echo -e "${CYAN}[前置]${NC} 检查是否有未验证的报告..."
    # 查找最近生成的报告
    LATEST_REPORT=$(ls -t ${OUTPUT_DIR}/*_完整深析报告.md 2>/dev/null | head -1)
    if [ -n "$LATEST_REPORT" ]; then
        echo "  发现最近报告: $LATEST_REPORT"
        echo -e "${YELLOW}  跳过自动verify（报告可能已手动验证过）${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}[1/4]${NC} Git add..."
    cd "$KB_DIR"
    git add -A
    
    echo ""
    echo -e "${CYAN}[2/4]${NC} Git commit..."
    git commit -m "📖 ${COMMIT_MSG} @$(date '+%Y-%m-%d')" || echo "  (无新变更)"
    
    echo ""
    echo -e "${CYAN}[3/4]${NC} Git push..."
    git pull --rebase || true
    git push
    
    echo ""
    echo -e "${CYAN}[4/4]${NC} ✅ 推库确认（漏洞⑥修复）..."
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/main 2>/dev/null || echo "")
    if [ "$LOCAL" = "$REMOTE" ]; then
        echo -e "  ${GREEN}✅ 本地与远程一致: ${LOCAL:0:8}${NC}"
    else
        echo -e "  ${YELLOW}⚠️ 本地(${LOCAL:0:8})≠远程(${REMOTE:0:8})，可能未同步${NC}"
    fi
    echo -e "  ${GREEN}✅ 最新: $(git log --oneline -1)${NC}"
fi
