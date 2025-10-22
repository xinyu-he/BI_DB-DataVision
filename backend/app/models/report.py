from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class ReportConfig(Base):
    __tablename__ = "report_config"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=False)
    sql_text = Column(Text, nullable=False)
    data_source = Column(String(50), default="main")  # 数据源配置
    enable = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联字段配置
    fields = relationship("ReportField", back_populates="report", cascade="all, delete-orphan")

class ReportField(Base):
    __tablename__ = "report_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("report_config.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=False)
    filterable = Column(Boolean, default=False)
    order = Column(Integer, default=0)
    field_type = Column(String(50), default="string")  # 字段类型：string, date, number等
    
    # 关联报表配置
    report = relationship("ReportConfig", back_populates="fields")