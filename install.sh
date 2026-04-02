#!/bin/bash
# ============================================================
# my-ai-teams 一键安装脚本
# 将三支团队的 agent 文件安装到 ~/.claude/agents/
# 换电脑后：git clone <仓库地址> && cd my-ai-teams && ./install.sh
# ============================================================

set -e

DEST="$HOME/.claude/agents"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/agents"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
RESET='\033[0m'

echo ""
echo -e "${CYAN}🚀 my-ai-teams 安装脚本${RESET}"
echo "=================================================="

# 创建目标目录
mkdir -p "$DEST"

count=0

# 安装团队一：产品研发团队
echo ""
echo -e "${YELLOW}📦 安装团队一：产品研发团队${RESET}"
for f in "$AGENTS_DIR/team1-product/"*.md; do
  [ -f "$f" ] || continue
  cp "$f" "$DEST/"
  echo "  ✓ $(basename "$f")"
  (( count++ )) || true
done

# 安装团队二：技术研发团队
echo ""
echo -e "${YELLOW}📦 安装团队二：技术研发团队${RESET}"
for f in "$AGENTS_DIR/team2-tech/"*.md; do
  [ -f "$f" ] || continue
  cp "$f" "$DEST/"
  echo "  ✓ $(basename "$f")"
  (( count++ )) || true
done

# 安装团队三：推广营销团队
echo ""
echo -e "${YELLOW}📦 安装团队三：推广营销团队${RESET}"
for f in "$AGENTS_DIR/team3-marketing/"*.md; do
  [ -f "$f" ] || continue
  cp "$f" "$DEST/"
  echo "  ✓ $(basename "$f")"
  (( count++ )) || true
done

echo ""
echo "=================================================="
echo -e "${GREEN}✅ 安装完成！共安装 $count 个 agent${RESET}"
echo ""
echo "安装位置：$DEST"
echo ""
echo -e "${CYAN}团队成员一览：${RESET}"
echo "  团队一（产品研发）：志远(Leader)、晓敏、建国、思远、慧敏、明远、雅琳、佳欣"
echo "  团队二（技术研发）：子豪(Leader)、浩然、雨欣、博文、晨曦、鹏程、思琦、建平"
echo "  团队三（推广营销）：嘉琪(Leader)、诗涵、宇航、文静、晓彤、梦琪、志强、雅文、博涛"
echo ""
echo -e "${CYAN}使用方式：${RESET}"
echo "  在 Claude Code 中直接 @成员名 即可调用对应角色"
echo "  例如：@志远 帮我分析这个产品方向"
echo ""
echo -e "${CYAN}团队记忆文件：${RESET}"
echo "  memory/team1-product/MEMORY.md  — 产品团队共享记忆"
echo "  memory/team2-tech/MEMORY.md     — 技术团队共享记忆"
echo "  memory/team3-marketing/MEMORY.md — 营销团队共享记忆"
echo ""
