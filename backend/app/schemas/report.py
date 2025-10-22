from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 报表配置基础模型
class ReportConfigBase(BaseModel):
    name: str
    type: str
    sql_text: str
    data_source: Optional[str] = "main"
    enable: Optional[bool] = True

# 报表配置响应模型
class ReportConfig(ReportConfigBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 报表配置更新模型
class ReportUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    sql_text: Optional[str] = None
    data_source: Optional[str] = None
    enable: Optional[bool] = None

# 字段配置基础模型
class ReportFieldBase(BaseModel):
    field_name: str
    display_name: str
    filterable: Optional[bool] = False
    order: Optional[int] = 0
    field_type: Optional[str] = "string"  # 字段类型：string, date, number等

# 字段配置创建模型
class ReportFieldCreate(ReportFieldBase):
    pass

# 字段配置响应模型
class ReportField(ReportFieldBase):
    id: int
    report_id: int
    
    class Config:
        from_attributes = True

# 报表详情模型
class ReportDetail(ReportConfig):
    fields: List[ReportField] = []

# 报表配置创建模型
class ReportCreate(ReportConfigBase):
    fields: Optional[List[ReportFieldBase]] = []

# 报表数据筛选模型
class ReportDataFilter(BaseModel):
    filters: Optional[dict] = {}
    page: Optional[int] = 1
    page_size: Optional[int] = 20

# 报表数据响应模型
class ReportDataResponse(BaseModel):
    data: List[dict]
    total: int
    page: int
    page_size: int