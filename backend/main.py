from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import reports
from app.database import Base, engine_main
import os

# 创建数据库表
Base.metadata.create_all(bind=engine_main)

app = FastAPI(title="报表配置与展示系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(reports.router, prefix="/api", tags=["reports"])

@app.get("/")
async def root():
    return {"message": "报表配置与展示系统 API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)