#!/usr/bin/env python3
"""
数据库迁移脚本 - 为MySQL数据库添加字段类型字段
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine_main
import pymysql

def upgrade():
    """升级数据库结构"""
    try:
        # MySQL数据库连接信息从环境变量获取
        # 这里我们直接使用pymysql连接MySQL数据库
        connection = pymysql.connect(
            host='bj-cynosdbmysql-grp-kat38osa.sql.tencentcdb.com',
            port=25388,
            user='xinyu',
            password='hxy1224...',
            database='report_system',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # 添加field_type列到report_fields表
        try:
            cursor.execute("ALTER TABLE report_fields ADD COLUMN field_type VARCHAR(50) DEFAULT 'string'")
            print("成功添加field_type字段到report_fields表")
        except pymysql.Error as e:
            if "Duplicate column name" in str(e):
                print("field_type字段已存在")
            else:
                print(f"添加字段时出错: {e}")
        
        connection.commit()
        connection.close()
        print("数据库迁移完成")
    except Exception as e:
        print(f"迁移过程中出错: {e}")

def downgrade():
    """降级数据库结构（简化实现）"""
    print("降级功能未实现")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()