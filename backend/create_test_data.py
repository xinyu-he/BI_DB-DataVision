#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
创建测试数据脚本
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, Base, engine
from app.models.report import ReportConfig, ReportField
from app.models import report

def create_test_data():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 检查是否已存在测试数据
        existing_reports = db.query(ReportConfig).count()
        if existing_reports > 0:
            print("测试数据已存在，跳过创建")
            return
        
        # 创建测试报表1: 用户统计报表
        report1 = ReportConfig(
            name="用户统计报表",
            type="统计报表",
            sql_text="SELECT id, username, email, created_at FROM users WHERE created_at >= :start_date",
            enable=True
        )
        db.add(report1)
        db.commit()
        db.refresh(report1)
        
        # 为报表1创建字段配置
        fields1 = [
            ReportField(
                report_id=report1.id,
                field_name="id",
                display_name="用户ID",
                filterable=True,
                order=1
            ),
            ReportField(
                report_id=report1.id,
                field_name="username",
                display_name="用户名",
                filterable=True,
                order=2
            ),
            ReportField(
                report_id=report1.id,
                field_name="email",
                display_name="邮箱",
                filterable=True,
                order=3
            ),
            ReportField(
                report_id=report1.id,
                field_name="created_at",
                display_name="注册时间",
                filterable=False,
                order=4
            )
        ]
        
        for field in fields1:
            db.add(field)
        
        # 创建测试报表2: 订单统计报表
        report2 = ReportConfig(
            name="订单统计报表",
            type="业务报表",
            sql_text="SELECT order_id, product_name, quantity, price, order_date FROM orders WHERE order_date >= :start_date AND order_date <= :end_date",
            enable=True
        )
        db.add(report2)
        db.commit()
        db.refresh(report2)
        
        # 为报表2创建字段配置
        fields2 = [
            ReportField(
                report_id=report2.id,
                field_name="order_id",
                display_name="订单ID",
                filterable=True,
                order=1
            ),
            ReportField(
                report_id=report2.id,
                field_name="product_name",
                display_name="产品名称",
                filterable=True,
                order=2
            ),
            ReportField(
                report_id=report2.id,
                field_name="quantity",
                display_name="数量",
                filterable=False,
                order=3
            ),
            ReportField(
                report_id=report2.id,
                field_name="price",
                display_name="价格",
                filterable=False,
                order=4
            ),
            ReportField(
                report_id=report2.id,
                field_name="order_date",
                display_name="订单日期",
                filterable=True,
                order=5
            )
        ]
        
        for field in fields2:
            db.add(field)
        
        # 创建测试报表3: 销售统计报表（禁用状态）
        report3 = ReportConfig(
            name="销售统计报表",
            type="统计报表",
            sql_text="SELECT sales_id, salesperson, amount, sale_date FROM sales WHERE sale_date >= :start_date",
            enable=False
        )
        db.add(report3)
        db.commit()
        db.refresh(report3)
        
        # 为报表3创建字段配置
        fields3 = [
            ReportField(
                report_id=report3.id,
                field_name="sales_id",
                display_name="销售ID",
                filterable=True,
                order=1
            ),
            ReportField(
                report_id=report3.id,
                field_name="salesperson",
                display_name="销售员",
                filterable=True,
                order=2
            ),
            ReportField(
                report_id=report3.id,
                field_name="amount",
                display_name="金额",
                filterable=False,
                order=3
            ),
            ReportField(
                report_id=report3.id,
                field_name="sale_date",
                display_name="销售日期",
                filterable=True,
                order=4
            )
        ]
        
        for field in fields3:
            db.add(field)
        
        db.commit()
        print("测试数据创建成功！")
        print(f"创建了 {db.query(ReportConfig).count()} 个报表配置")
        print(f"创建了 {db.query(ReportField).count()} 个字段配置")
        
    except Exception as e:
        db.rollback()
        print(f"创建测试数据时出错: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data()