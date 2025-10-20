from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os
from dotenv import load_dotenv
import pymysql
from typing import Dict, Callable

# 配置PyMySQL
pymysql.install_as_MySQLdb()

# 加载环境变量
load_dotenv()

# 主数据库配置（存储报表配置）
MAIN_DATABASE_URL = os.getenv("MAIN_DATABASE_URL", "sqlite:///./report_system.db")

# 创建主数据库引擎
engine_main = create_engine(MAIN_DATABASE_URL, connect_args={"check_same_thread": False} if MAIN_DATABASE_URL.startswith("sqlite") else {})
SessionLocalMain = sessionmaker(autocommit=False, autoflush=False, bind=engine_main)

# 业务数据库配置
BUSINESS_DATABASE_URL = os.getenv("BUSINESS_DATABASE_URL", "sqlite:///./business.db")

# 创建业务数据库引擎
engine_business = create_engine(BUSINESS_DATABASE_URL, connect_args={"check_same_thread": False} if BUSINESS_DATABASE_URL.startswith("sqlite") else {})
SessionLocalBusiness = sessionmaker(autocommit=False, autoflush=False, bind=engine_business)

# 不需要订单数据库，使用业务数据库作为默认
engine_order = engine_business
SessionLocalOrder = SessionLocalBusiness

# 数据源映射
DATABASE_ENGINES: Dict[str, object] = {
    "main": engine_main,
    "business": engine_business,
    "order": engine_business  # 订单数据源使用业务数据库
}

DATABASE_SESSIONS: Dict[str, Callable[[], Session]] = {
    "main": lambda: SessionLocalMain(),
    "business": lambda: SessionLocalBusiness(),
    "order": lambda: SessionLocalBusiness()  # 订单数据源使用业务数据库会话
}

Base = declarative_base()

# 获取主数据库会话（用于报表配置）
def get_db():
    db = SessionLocalMain()
    try:
        yield db
    finally:
        db.close()

# 根据数据源获取会话
def get_db_session(data_source: str = "main"):
    session_factory = DATABASE_SESSIONS.get(data_source, lambda: SessionLocalMain())
    return session_factory()