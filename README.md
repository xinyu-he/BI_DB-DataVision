# 报表配置与展示系统

本项目是一个基于Vue3+Vite+Element Plus和Python FastAPI的报表管理系统，支持动态报表配置与展示。

## 项目结构

```
.
├── backend              # 后端服务
│   ├── app              # 应用代码
│   │   ├── api          # API接口
│   │   ├── models       # 数据模型
│   │   ├── schemas      # 数据验证模型
│   │   └── database.py  # 数据库配置
│   ├── main.py          # 应用入口
│   └── requirements.txt # 依赖包
├── frontend             # 前端应用
│   ├── public           # 静态资源
│   └── src              # 源代码
└── README.md            # 项目说明
```

## 运行项目

### 方法一：使用启动脚本（推荐）

```bash
# 启动开发环境
./start-dev.sh

# 停止服务
./stop.sh
```

### 方法二：手动启动

1. 启动后端服务：
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

2. 启动前端服务：
```bash
cd frontend
npm install
npm run dev
```

## 访问地址

- 前端界面：http://localhost:3002
- 后端API：http://localhost:8000

## 功能说明

### 后端API接口

- `GET /api/reports` - 获取报表列表
- `GET /api/reports/{id}` - 获取报表详情
- `POST /api/reports` - 创建报表
- `PUT /api/reports/{id}` - 更新报表
- `DELETE /api/reports/{id}` - 删除报表
- `POST /api/reports/{id}/data` - 查询报表数据

### 前端功能

1. 报表配置页面：管理员可以创建、编辑、删除报表配置
2. 报表展示页面：用户可以查看报表数据，支持筛选和分页
3. 首页：系统导航入口