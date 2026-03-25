#!/bin/bash
# Git 初始化脚本

# 检查 git 是否安装
if ! command -v git &> /dev/null; then
    echo "Git 未安装，正在安装..."

    # 根据系统类型安装 git
    if [ -f /etc/debian_version ]; then
        sudo apt-get update && sudo apt-get install -y git
    elif [ -f /etc/redhat-release ]; then
        sudo yum install -y git
    else
        echo "请手动安装 git"
        exit 1
    fi
fi

# 初始化 git 仓库
git init
git add .
git commit -m "Initial commit: Genome assembly multi-agent system with backtracking

- Phase 1: MVP implementation (linear pipeline)
- Phase 2: Backtracking mechanism based on QC metrics
- 4 core agents: assembly, repeat, structural, functional
- Quality control checks at each step
- Audit logging

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"

echo "Git 仓库初始化完成"
echo "下一步: git remote add origin <your-repo-url>"
echo "然后: git push -u origin main"
