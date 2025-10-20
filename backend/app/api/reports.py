from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from app import schemas, models
from app.schemas import report as schemas
from app.models import report as models
from app.database import get_db, get_db_session

router = APIRouter()

@router.get("/reports", response_model=List[schemas.ReportConfig])
def get_reports(
    name: Optional[str] = None,
    type: Optional[str] = None,
    enable: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    获取报表列表
    """
    query = db.query(models.ReportConfig)
    
    if name:
        query = query.filter(models.ReportConfig.name.contains(name))
    if type:
        query = query.filter(models.ReportConfig.type == type)
    if enable is not None:
        query = query.filter(models.ReportConfig.enable == enable)
        
    return query.all()

@router.get("/reports/{report_id}", response_model=schemas.ReportDetail)
def get_report_detail(report_id: int, db: Session = Depends(get_db)):
    """
    获取报表详情
    """
    report = db.query(models.ReportConfig).filter(models.ReportConfig.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表未找到")
    
    fields = db.query(models.ReportField).filter(models.ReportField.report_id == report_id).all()
    
    # 构建响应模型
    report_config = schemas.ReportConfig.from_orm(report)
    report_fields = [schemas.ReportField.from_orm(field) for field in fields]
    
    return schemas.ReportDetail(
        **report_config.model_dump(),
        fields=report_fields
    )

@router.post("/reports", response_model=schemas.ReportConfig)
def create_report(report: schemas.ReportCreate, db: Session = Depends(get_db)):
    """
    创建报表
    """
    try:
        # 创建报表配置
        report_data = report.dict(exclude={'fields'})
        db_report = models.ReportConfig(**report_data)
        db.add(db_report)
        db.flush()  # 先刷新获取ID，但不提交事务
        
        # 创建字段配置
        if report.fields:
            for field_data in report.fields:
                # 确保字段数据有效
                if field_data.field_name and field_data.display_name:
                    db_field = models.ReportField(
                        report_id=db_report.id,
                        field_name=field_data.field_name,
                        display_name=field_data.display_name,
                        filterable=field_data.filterable or False,
                        order=field_data.order or 0
                    )
                    db.add(db_field)
        
        db.commit()
        db.refresh(db_report)
        return db_report
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建报表失败: {str(e)}")

@router.put("/reports/{report_id}", response_model=schemas.ReportConfig)
def update_report(report_id: int, report: schemas.ReportCreate, db: Session = Depends(get_db)):
    """
    更新报表
    """
    try:
        db_report = db.query(models.ReportConfig).filter(models.ReportConfig.id == report_id).first()
        if not db_report:
            raise HTTPException(status_code=404, detail="报表未找到")
        
        # 更新报表配置
        report_data = report.dict(exclude={'fields'})
        for key, value in report_data.items():
            setattr(db_report, key, value)
                
        # 更新字段配置
        # 先删除现有的字段配置
        db.query(models.ReportField).filter(models.ReportField.report_id == report_id).delete()
        
        # 添加新的字段配置
        if report.fields:
            for field_data in report.fields:
                # 确保字段数据有效
                if field_data.field_name and field_data.display_name:
                    db_field = models.ReportField(
                        report_id=report_id,
                        field_name=field_data.field_name,
                        display_name=field_data.display_name,
                        filterable=field_data.filterable or False,
                        order=field_data.order or 0
                    )
                    db.add(db_field)
        
        db.commit()
        db.refresh(db_report)
        return db_report
    except HTTPException:
        # 重新抛出已知的HTTP异常
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新报表失败: {str(e)}")

@router.delete("/reports/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    """
    删除报表
    """
    db_report = db.query(models.ReportConfig).filter(models.ReportConfig.id == report_id).first()
    if not db_report:
        raise HTTPException(status_code=404, detail="报表未找到")
    
    # 删除相关的字段配置
    db.query(models.ReportField).filter(models.ReportField.report_id == report_id).delete()
    
    # 删除报表配置
    db.delete(db_report)
    db.commit()
    return {"message": "报表删除成功"}

@router.post("/reports/{report_id}/data")
def get_report_data(
    report_id: int, 
    filters: schemas.ReportDataFilter,
    db: Session = Depends(get_db)
):
    """
    查询报表数据
    """
    report = db.query(models.ReportConfig).filter(models.ReportConfig.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="报表未找到")
    
    # 根据报表配置的数据源获取对应的数据库会话
    data_source = str(report.data_source) if report.data_source is not None else "main"
    
    try:
        # 使用上下文管理器确保数据库连接正确关闭
        with get_db_session(data_source) as data_db:
            # 获取报表字段
            fields = db.query(models.ReportField).filter(models.ReportField.report_id == report_id).all()
            
            # 解析SQL并执行查询
            sql_text = report.sql_text
            page = filters.page or 1
            page_size = filters.page_size or 20
            # 过滤掉空字符串和null值的筛选条件
            filter_conditions = {k: v for k, v in (filters.filters or {}).items() if v is not None and v != ''}
            
            # 应用筛选条件到SQL
            if filter_conditions:
                # 简单的WHERE条件添加（实际应用中需要更复杂的SQL解析）
                if "WHERE" in sql_text.upper():
                    # 如果SQL中已包含WHERE子句
                    where_clause = " AND ".join([f"{key} = :{key}" for key in filter_conditions.keys()])
                    sql_text = sql_text + f" AND {where_clause}"
                else:
                    # 如果SQL中不包含WHERE子句
                    where_clause = " AND ".join([f"{key} = :{key}" for key in filter_conditions.keys()])
                    sql_text = sql_text + f" WHERE {where_clause}"
            
            # 添加分页
            offset = (page - 1) * page_size
            sql_with_pagination = f"{sql_text} LIMIT {page_size} OFFSET {offset}"
            
            print(f"执行SQL: {sql_with_pagination}")
            print(f"参数: {filter_conditions}")
            
            # 执行查询
            result = data_db.execute(text(sql_with_pagination), filter_conditions)
            rows = result.fetchall()
            
            # 转换为字典格式
            column_names = result.keys()
            data = [dict(zip(column_names, row)) for row in rows]
            
            # 获取总记录数
            count_sql = f"SELECT COUNT(*) FROM ({sql_text}) as count_table"
            count_result = data_db.execute(text(count_sql), filter_conditions)
            total = count_result.scalar()
            
            return {
                "data": data,
                "total": total,
                "page": page,
                "page_size": page_size
            }
    except Exception as e:
        # 打印详细的错误信息
        print(f"查询数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 如果执行出错，返回更友好的错误信息
        error_msg = str(e)
        if "no such table" in error_msg:
            raise HTTPException(status_code=500, detail=f"查询数据时出错: 指定的数据表不存在，请检查SQL语句中的表名是否正确。错误详情: {error_msg}")
        else:
            raise HTTPException(status_code=500, detail=f"查询数据时出错: {error_msg}")
