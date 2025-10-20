#!/bin/bash

# 开发环境启动脚本

echo "=== 报表配置与展示系统开发环境启动 ==="

# 创建PID文件目录
PID_DIR=".pids"
mkdir -p $PID_DIR

# 启动后端服务
echo "1. 启动后端服务..."
cd backend

# 检查是否已存在虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "安装后端依赖..."
pip install -r requirements.txt

# 设置环境变量
export DATABASE_URL="sqlite:///./report_system.db"

# 初始化数据库（如果不存在）
if [ ! -f "report_system.db" ]; then
    echo "初始化数据库..."
    python3 -c "
from app.database import Base, engine
from app.models import report
Base.metadata.create_all(bind=engine)
print('数据库初始化完成')
"
fi

# 启动后端服务（后台运行）
echo "后端服务启动中..."
nohup python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../$PID_DIR/backend.pid
echo "后端服务已启动，PID: $BACKEND_PID，访问地址: http://localhost:8000"

cd ..

# 启动前端服务
echo "2. 启动前端服务..."
cd frontend

# 检查是否已安装依赖
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 启动前端开发服务器
echo "前端服务启动中..."
npx vite &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../$PID_DIR/frontend.pid
echo "前端服务已启动，PID: $FRONTEND_PID，访问地址: http://localhost:3000"

cd ..

echo ""
echo "=== 系统启动信息 ==="
echo "后端API服务: http://localhost:8000"
echo "前端开发服务: http://localhost:3000"
echo "后端进程PID: $BACKEND_PID"
echo "前端进程PID: $FRONTEND_PID"
echo ""
echo "=== 使用说明 ==="
echo "1. 请等待约10-20秒让服务完全启动"
echo "2. 打开浏览器访问 http://localhost:3000"
echo "3. 要停止服务，请运行: ./stop.sh"