#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加数据源字段
"""

import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine_main
import sqlite3

def upgrade():
    """升级数据库结构"""
    try:
        # 对于SQLite，我们需要重新创建表
        conn = sqlite3.connect('./report_system.db')
        cursor = conn.cursor()
        
        # 添加data_source列到report_config表
        try:
            cursor.execute("ALTER TABLE report_config ADD COLUMN data_source VARCHAR(50) DEFAULT 'main'")
            print("成功添加data_source字段到report_config表")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("data_source字段已存在")
            else:
                print(f"添加字段时出错: {e}")
        
        conn.commit()
        conn.close()
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