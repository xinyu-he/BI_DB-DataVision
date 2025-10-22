#!/bin/bash

# 停止报表配置与展示系统

echo "=== 停止报表配置与展示系统 ==="

PID_DIR=".pids"

# 停止后端服务
if [ -f "$PID_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat $PID_DIR/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "停止后端服务 PID: $BACKEND_PID"
        kill $BACKEND_PID
        # 等待进程结束
        while ps -p $BACKEND_PID > /dev/null; do
            sleep 1
        done
        echo "后端服务已停止"
    else
        echo "后端服务进程不存在"
    fi
    rm -f $PID_DIR/backend.pid
else
    echo "未找到后端服务PID文件"
    # 查找并停止后端服务（备用方法）
    BACKEND_PIDS=$(pgrep -f "python3 main.py")
    if [ ! -z "$BACKEND_PIDS" ]; then
        echo "停止后端服务 PID: $BACKEND_PIDS"
        kill $BACKEND_PIDS
    else
        echo "未找到运行中的后端服务"
    fi
fi

# 停止前端服务
if [ -f "$PID_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat $PID_DIR/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "停止前端服务 PID: $FRONTEND_PID"
        kill $FRONTEND_PID
        # 等待进程结束
        while ps -p $FRONTEND_PID > /dev/null; do
            sleep 1
        done
        echo "前端服务已停止"
    else
        echo "前端服务进程不存在"
    fi
    rm -f $PID_DIR/frontend.pid
else
    echo "未找到前端服务PID文件"
    # 查找并停止前端服务（备用方法）
    FRONTEND_PIDS=$(pgrep -f "vite")
    if [ ! -z "$FRONTEND_PIDS" ]; then
        echo "停止前端服务 PID: $FRONTEND_PIDS"
        kill $FRONTEND_PIDS
    else
        echo "未找到运行中的前端服务"
    fi
fi

# 强制清理可能的残留进程
pkill -f "uvicorn" 2>/dev/null
pkill -f "vite" 2>/dev/null

# 清理PID目录
rmdir $PID_DIR 2>/dev/null

echo "服务停止完成！"