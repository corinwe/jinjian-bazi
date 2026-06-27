#!/bin/bash
# ═══════════════════════════════════════════════════════
# 金鉴真人·部署配置助手
# ═══════════════════════════════════════════════════════
# 配置 GitHub Secrets + 服务器 SSH 密钥
# ═══════════════════════════════════════════════════════

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  金鉴真人·自动部署配置助手${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo ""

# ── 步骤 1: 生成 SSH 密钥（如果没有） ──
echo -e "${YELLOW}[步骤 1/4]${NC} SSH 密钥检查"

SSH_KEY_PATH="$HOME/.ssh/deploy_key_ed25519"
if [ -f "$SSH_KEY_PATH" ]; then
    echo -e "  ${GREEN}✓${NC} 部署密钥已存在: $SSH_KEY_PATH"
else
    echo "  生成新的部署密钥..."
    mkdir -p "$HOME/.ssh"
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -N "" -C "bazi-deploy@jinjian"
    echo -e "  ${GREEN}✓${NC} 密钥已生成: $SSH_KEY_PATH"
fi

echo ""
echo -e "${YELLOW}[步骤 2/4]${NC} 将公钥添加到服务器"
echo ""
echo "  执行以下命令，将公钥添加到服务器:"
echo ""
echo "  ssh-copy-id -i $SSH_KEY_PATH.pub root@43.162.90.39"
echo ""

read -p "  现在执行? [y/N] " do_copy
if [ "$do_copy" = "y" ] || [ "$do_copy" = "Y" ]; then
    ssh-copy-id -i "$SSH_KEY_PATH.pub" root@43.162.90.39
    echo -e "  ${GREEN}✓${NC} 公钥已添加到服务器"
else
    echo -e "  ${YELLOW}⚠${NC} 请手动执行上面的命令"
fi

echo ""
echo -e "${YELLOW}[步骤 3/4]${NC} 配置 GitHub Secrets"
echo ""
echo "  手动在 GitHub 仓库设置以下 Secrets:"
echo ""
echo "  仓库: https://github.com/corinwe/jinjian-bazi/settings/secrets/actions"
echo ""
echo "  ┌────────────────────┬─────────────────────────────────────────────┐"
echo "  │ Secret Name        │ Value                                      │"
echo "  ├────────────────────┼─────────────────────────────────────────────┤"
echo "  │ DEPLOY_HOST        │ 43.162.90.39                                │"
echo "  │ DEPLOY_USER        │ root                                       │"
echo "  │ DEPLOY_KEY         │ $(cat $SSH_KEY_PATH)                         │"
echo "  └────────────────────┴─────────────────────────────────────────────┘"
echo ""
echo -e "${YELLOW}[步骤 4/4]${NC} 验证 CI/CD"
echo ""
echo "  配置完成后，推送任意代码到 main 分支触发部署:"
echo ""
echo "  git push origin main"
echo ""

echo -e "${GREEN}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  配置完成!${NC}"
echo -e "${GREEN}  GitHub 配置: https://github.com/corinwe/jinjian-bazi/settings/secrets/actions${NC}"
echo -e "${GREEN}═══════════════════════════════════════════${NC}"
