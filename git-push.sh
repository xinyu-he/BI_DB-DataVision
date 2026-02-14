#!/bin/bash

# Git 自动提交和推送脚本
# 使用方法: ./git-push.sh "提交信息"

# 检查是否提供了提交信息
if [ $# -eq 0 ]; then
    echo "错误: 请提供提交信息"
    echo "使用方法: ./git-push.sh \"你的提交信息\""
    exit 1
fi

# 获取当前时间
current_time=$(date "+%Y-%m-%d %H:%M:%S")

# 显示当前状态
echo "====================="
echo "Git 状态检查"
echo "====================="
git status

# 添加所有更改的文件
echo "====================="
echo "添加所有更改的文件..."
echo "====================="
git add .

# 提交更改
commit_message="$1 ($current_time)"
echo "====================="
echo "提交更改: $commit_message"
echo "====================="
git commit -m "$commit_message"

# 推送到远程仓库
echo "====================="
echo "推送到远程仓库..."
echo "====================="
git push

echo "====================="
echo "完成! 代码已成功推送。"
echo "====================="