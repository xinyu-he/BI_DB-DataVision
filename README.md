# BI_DB-DataVision - 报表配置与展示系统

[![GitHub branch](https://img.shields.io/badge/branch-dev-green)](https://github.com/xinyu-he/BI_DB-DataVision/tree/dev) [![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

## 项目概述

本项目是一个基于 **Vue3 + Vite + Element Plus**（前端）和 **Python FastAPI + MySQL**（后端）的动态报表管理系统，旨在为企业提供一个灵活高效的报表平台。系统支持报表的**可视化配置**、**SQL定义**、**字段管理**与**前端展示**。管理员可以通过系统配置查询逻辑和展示字段，普通用户可按需筛选并查看数据报表。

### 核心特性
- **前后端分离**：前后端独立开发、部署，便于维护和扩展。
- **动态报表构建**：支持自定义SQL查询、字段映射和可视化组件配置。
- **安全执行**：后端SQL执行采用参数化查询和权限控制，防止SQL注入。
- **用户友好**：前端基于Element Plus，提供响应式UI，支持筛选、分页和导出。
- **多业务适配**：适用于数据分析、业务报表、仪表盘等场景。

系统架构采用现代技术栈，确保高性能和可扩展性，满足企业级数据展示需求。

## 项目结构

项目采用清晰的模块化结构，便于开发和协作：

```
.
├── backend                  # 后端服务（FastAPI + MySQL）
│   ├── app                  # 核心应用代码
│   │   ├── __init__.py      # 包初始化
│   │   ├── api              # API路由和端点定义
│   │   │   └── reports.py   # 报表相关接口
│   │   ├── models           # SQLAlchemy ORM数据模型（报表、字段等）
│   │   ├── schemas          # Pydantic数据验证模型
│   │   └── database.py      # 数据库连接和会话管理
│   ├── main.py              # FastAPI应用入口
│   ├── requirements.txt     # Python依赖（fastapi, sqlalchemy, pymysql等）
│   └── venv/                # 虚拟环境（可选，手动创建）
├── frontend                 # 前端应用（Vue3 + Vite）
│   ├── public               # 静态资源（图标、标题等）
│   ├── src                  # 源代码
│   │   ├── App.vue          # 根组件（包含头部导航）
│   │   ├── components/      # 公共组件（表格、图表等）
│   │   ├── router/          # 路由配置（首页、报表展示、配置页面）
│   │   ├── views/           # 页面视图（Home.vue, Reports.vue, Config.vue）
│   │   └── main.js          # 应用入口（Vue实例化）
│   ├── package.json         # NPM依赖和脚本
│   ├── vite.config.js       # Vite构建配置
│   └── index.html           # 入口HTML
├── scripts                  # 辅助脚本
│   ├── start-dev.sh         # 开发环境一键启动脚本
│   └── stop.sh              # 服务停止脚本
├── README.md                # 本文档
├── LICENSE                  # 开源许可（MIT）
└── .gitignore               # Git忽略文件
```

## 技术栈

### 后端
- **框架**：FastAPI（高性能异步API框架）
- **数据库**：MySQL（ORM: SQLAlchemy）
- **验证**：Pydantic
- **其他**：Uvicorn（ASGI服务器）

### 前端
- **框架**：Vue3（Composition API）
- **构建工具**：Vite（快速开发服务器）
- **UI库**：Element Plus（响应式组件库）
- **路由**：Vue Router
- **HTTP**：Axios（API调用）
- **图标**：@element-plus/icons-vue

### 环境要求
- **Python**：3.8+
- **Node.js**：16+
- **MySQL**：5.7+（需手动配置数据库）
- **Git**：用于克隆仓库

## 快速开始

### 前置准备
1. **克隆仓库**：
   ```
   git clone https://github.com/xinyu-he/BI_DB-DataVision.git
   cd BI_DB-DataVision
   git checkout dev  # 切换到开发分支
   ```

2. **配置数据库**：
   - 创建MySQL数据库（例如 `datavision_db`）。
   - 在 `backend/app/database.py` 中更新数据库连接字符串（`SQLALCHEMY_DATABASE_URL`）。
   - 运行数据库迁移（如果有 Alembic 配置）或手动创建表（基于 models）。

3. **安装依赖**：
   - 后端：`cd backend && pip install -r requirements.txt`
   - 前端：`cd frontend && npm install`

### 方法一：使用启动脚本（推荐，适用于开发）
脚本会自动启动后端（端口 8000）和前端（端口 5173），并处理虚拟环境。

```
# 确保脚本可执行
chmod +x scripts/start-dev.sh

# 启动开发环境
./scripts/start-dev.sh

# 在新终端停止服务
./scripts/stop.sh
```

### 方法二：手动启动
1. **启动后端**：
   ```
   cd backend
   python3 -m venv venv  # 创建虚拟环境（可选）
   source venv/bin/activate  # 激活环境（Linux/Mac）
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **启动前端**（在新终端）：
   ```
   cd frontend
   npm run dev
   ```

### 访问系统
- **前端**：http://localhost:5173
- **后端API文档**：http://localhost:8000/docs（Swagger UI）

## 功能模块

### 1. 报表配置（管理员专属）
- **路径**：`/config`
- **功能**：
  - 创建报表：定义SQL查询、字段映射（标题、类型、格式）。
  - 编辑/删除报表：支持可视化拖拽配置展示字段。
  - 权限管理：仅管理员可访问。

### 2. 报表展示（用户视图）
- **路径**：`/reports`
- **功能**：
  - 查看报表列表：点击进入详情。
  - 数据查询：支持参数筛选（日期、类别等）、分页和排序。
  - 可视化：表格、图表（集成 ECharts 或 Element Plus 表格）。
  - 导出：CSV/Excel 下载。

### 3. 首页（导航入口）
- **路径**：`/`
- **功能**：
  - 系统概览：快速链接到配置和展示页面。
  - 公告/统计：显示报表使用统计（可选扩展）。

### API 接口文档
系统提供 RESTful API，支持 CRUD 操作。详细接口见后端 Swagger 文档。

| 方法 | 端点                  | 描述             | 参数/响应 |
|------|-----------------------|------------------|-----------|
| GET  | `/api/reports`       | 获取报表列表    | 查询参数：page, limit<br>响应：JSON 列表 |
| GET  | `/api/reports/{id}`  | 获取报表详情    | 路径：id<br>响应：报表配置 |
| POST | `/api/reports`       | 创建报表        | Body：报表 schema<br>响应：创建 ID |
| PUT  | `/api/reports/{id}`  | 更新报表        | 路径：id, Body：更新数据 |
| DELETE | `/api/reports/{id}` | 删除报表      | 路径：id<br>响应：成功消息 |
| POST | `/api/reports/{id}/data` | 查询报表数据 | 路径：id, Body：筛选参数<br>响应：数据数组 |

## 开发指南

### 后端开发
- **添加模型**：在 `app/models/` 中定义新表，使用 SQLAlchemy。
- **新API**：在 `app/api/` 中创建路由，集成依赖注入（数据库会话）。
- **测试**：使用 `pytest` 运行单元测试（需安装 pytest）。

### 前端开发
- **组件开发**：在 `src/components/` 添加 Vue 单文件组件。
- **路由扩展**：修改 `src/router/index.js` 添加新页面。
- **状态管理**：使用 Pinia（可选集成）管理全局状态。
- **构建生产**：`npm run build` 生成 dist/ 目录。

### 常见问题
- **CORS 错误**：在 `backend/main.py` 中配置 CORS 中间件，允许前端域名。
- **数据库连接失败**：检查 `database.py` 中的 URL 格式（`mysql+pymysql://user:pass@localhost/db`）。
- **端口冲突**：修改 uvicorn 或 Vite 配置中的端口。
- **依赖安装失败**：确保 Python/Node 版本兼容，尝试 `pip install --upgrade pip` 或 `npm ci`。

## 部署指南

### 生产环境
1. **后端**：
   - 使用 Gunicorn + Uvicorn：`gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`
   - Docker 支持：创建 `Dockerfile`（基于 python:3.9-slim），暴露 8000 端口。

2. **前端**：
   - 构建：`npm run build`
   - 部署：Nginx 服务静态文件，代理 API 到后端。

3. **数据库**：使用云 MySQL（如阿里云 RDS），配置环境变量。

4. **完整 Docker Compose**（示例）：
   ```
   version: '3'
   services:
     backend:
       build: ./backend
       ports: ["8000:8000"]
       depends_on: [db]
     db:
       image: mysql:8.0
       environment:
         MYSQL_ROOT_PASSWORD: password
         MYSQL_DATABASE: datavision_db
     frontend:
       build: ./frontend
       ports: ["80:80"]
   ```

## 贡献指南

欢迎贡献！请遵循以下步骤：
1. Fork 项目并创建 `dev` 分支。
2. 提交变更：`git commit -m "feat: 添加新功能"`
3. Push 并创建 Pull Request 到 `dev` 分支。
4. 确保代码通过 ESLint（前端）和 Pylint（后端）检查。

## 许可证

本项目采用 **MIT License**。详见 [LICENSE](LICENSE) 文件。

## 联系与支持

- **作者**：xinyu-he（GitHub: [xinyu-he](https://github.com/xinyu-he)）
- **Issue**：在 GitHub 仓库提交问题或功能请求。
- **讨论**：欢迎在 Issues 或 Pull Requests 中讨论。

感谢您的兴趣！如果有任何问题，欢迎随时反馈。

---

*© 2025 xinyu-he. 数据驱动决策，从 BI_DB-DataVision 开始。*
