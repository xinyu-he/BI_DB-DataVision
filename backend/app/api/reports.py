from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
import pandas as pd
import tempfile
import os
from urllib.parse import quote
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
                        order=field_data.order or 0,
                        field_type=field_data.field_type or "string"  # 添加字段类型
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
                        order=field_data.order or 0,
                        field_type=field_data.field_type or "string"  # 添加字段类型
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
            
            # 构建字段类型映射，用于处理特殊查询
            field_type_map = {field.field_name: field.field_type for field in fields} if fields else {}
            
            # 应用筛选条件到SQL
            if filter_conditions:
                where_conditions = []
                params = {}
                
                for key, value in filter_conditions.items():
                    field_type = field_type_map.get(key, "string")
                    
                    # 处理日期范围查询
                    if field_type in ["date-range", "datetime-range"] and isinstance(value, str) and "~" in value:
                        # 范围查询，格式：开始时间~结束时间
                        date_range = value.split("~")
                        start_date = date_range[0].strip()
                        end_date = date_range[1].strip() if len(date_range) > 1 else None
                        
                        if start_date and end_date:
                            where_conditions.append(f"{key} BETWEEN :{key}_start AND :{key}_end")
                            params[f"{key}_start"] = start_date
                            params[f"{key}_end"] = end_date
                        elif start_date:
                            where_conditions.append(f"{key} >= :{key}_start")
                            params[f"{key}_start"] = start_date
                        elif end_date:
                            where_conditions.append(f"{key} <= :{key}_end")
                            params[f"{key}_end"] = end_date
                    # 处理日期精确查询
                    elif field_type in ["date", "datetime"] and isinstance(value, str):
                        # 尝试解析多种日期格式
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
                    # 处理普通查询
                    else:
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
                
                # 应用WHERE条件到SQL
                if where_conditions:
                    where_clause = " AND ".join(where_conditions)
                    # 处理UNION查询的特殊情况
                    if "UNION" in sql_text.upper():
                        # 如果是UNION查询，需要将WHERE子句包装在子查询中
                        sql_text = f"SELECT * FROM ({sql_text}) AS sub_query WHERE {where_clause}"
                    elif "WHERE" in sql_text.upper():
                        sql_text = sql_text + f" AND {where_clause}"
                    else:
                        sql_text = sql_text + f" WHERE {where_clause}"
                    filter_conditions = params  # 使用处理后的参数
            
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

@router.post("/reports/{report_id}/export")
def export_report_data(
    report_id: int, 
    filters: schemas.ReportDataFilter,
    db: Session = Depends(get_db)
):
    """
    导出报表数据为Excel
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
            sql_text_str = str(report.sql_text)
            # 过滤掉空字符串和null值的筛选条件
            filter_conditions = {k: v for k, v in (filters.filters or {}).items() if v is not None and v != ''}
            
            # 构建字段类型映射，用于处理特殊查询
            field_type_map = {field.field_name: field.field_type for field in fields} if fields else {}
            
            # 应用筛选条件到SQL
            if filter_conditions:
                where_conditions = []
                params = {}
                
                for key, value in filter_conditions.items():
                    field_type = field_type_map.get(key, "string")
                    
                    # 处理日期范围查询
                    if field_type in ["date-range", "datetime-range"] and isinstance(value, str) and "~" in value:
                        # 范围查询，格式：开始时间~结束时间
                        date_range = value.split("~")
                        start_date = date_range[0].strip()
                        end_date = date_range[1].strip() if len(date_range) > 1 else None
                        
                        if start_date and end_date:
                            where_conditions.append(f"{key} BETWEEN :{key}_start AND :{key}_end")
                            params[f"{key}_start"] = start_date
                            params[f"{key}_end"] = end_date
                        elif start_date:
                            where_conditions.append(f"{key} >= :{key}_start")
                            params[f"{key}_start"] = start_date
                        elif end_date:
                            where_conditions.append(f"{key} <= :{key}_end")
                            params[f"{key}_end"] = end_date
                    # 处理日期精确查询
                    elif field_type in ["date", "datetime"] and isinstance(value, str):
                        # 尝试解析多种日期格式
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
                    # 处理普通查询
                    else:
                        where_conditions.append(f"{key} = :{key}")
                        params[key] = value
                
                # 应用WHERE条件到SQL
                if where_conditions:
                    where_clause = " AND ".join(where_conditions)
                    # 处理UNION查询的特殊情况
                    if "UNION" in sql_text_str.upper():
                        # 如果是UNION查询，需要将WHERE子句包装在子查询中
                        sql_text_str = f"SELECT * FROM ({sql_text_str}) AS sub_query WHERE {where_clause}"
                    elif "WHERE" in sql_text_str.upper():
                        sql_text_str = sql_text_str + f" AND {where_clause}"
                    else:
                        sql_text_str = sql_text_str + f" WHERE {where_clause}"
                    filter_conditions = params  # 使用处理后的参数
            
            print(f"执行SQL: {sql_text_str}")
            print(f"参数: {filter_conditions}")
            
            # 执行查询
            result = data_db.execute(text(sql_text_str), filter_conditions)
            rows = result.fetchall()
            
            # 转换为字典格式
            column_names = result.keys()
            data = [dict(zip(column_names, row)) for row in rows]
            
            # 创建DataFrame并导出为Excel
            df = pd.DataFrame(data)
            
            # 根据字段类型进行数据格式化
            if fields:
                field_type_mapping = {field_item.field_name: str(field_item.field_type) for field_item in fields}
                for column in df.columns:
                    if column in field_type_mapping:
                        field_type_val = field_type_mapping[column]
                        if field_type_val == "date":
                            df[column] = pd.to_datetime(df[column], errors='coerce').dt.date
                        elif field_type_val == "datetime":
                            df[column] = pd.to_datetime(df[column], errors='coerce')
                        elif field_type_val == "number":
                            df[column] = pd.to_numeric(df[column], errors='coerce')
            
            # 创建临时文件
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                tmp_filename = tmp_file.name
            
            # 保存到临时文件，直接使用to_excel方法
            df.to_excel(tmp_filename, engine='openpyxl', index=False, sheet_name=str(report.name)[:31])
            
            # 读取文件内容
            with open(tmp_filename, 'rb') as f:
                excel_data = f.read()
            
            # 删除临时文件
            os.unlink(tmp_filename)
            
            # 设置响应头，指定文件名为报表名称（处理中文编码问题）
            filename = f"{report.name}.xlsx"
            # 对文件名进行URL编码以支持中文
            encoded_filename = quote(filename.encode('utf-8'))
            headers = {
                'Content-Disposition': f'attachment; filename*=UTF-8\'\'{encoded_filename}',
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            }
            
            return Response(content=excel_data, headers=headers)
            
    except Exception as e:
        # 打印详细的错误信息
        print(f"导出数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 如果执行出错，返回更友好的错误信息
        error_msg = str(e)
        if "no such table" in error_msg:
            raise HTTPException(status_code=500, detail=f"导出数据时出错: 指定的数据表不存在，请检查SQL语句中的表名是否正确。错误详情: {error_msg}")
        else:
            raise HTTPException(status_code=500, detail=f"导出数据时出错: {error_msg}")
