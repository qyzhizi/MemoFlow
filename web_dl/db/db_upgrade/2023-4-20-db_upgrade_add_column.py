#!/usr/bin/env python
# coding=utf-8

# 将旧表数据插入新表，id 从 1 开始自增，其他列的值保持不变

import sys
sys.path.insert(0,"/root/git_rep/dl/web_dl/")

from datetime import datetime
import sqlite3

from web_dl.conf import CONF

path = CONF['diary_log']['data_base_path']
#path = "/root/git_rep/dl/web_dl/data/diary_log/diary_log_test.db"

conn = sqlite3.connect(path)
c = conn.cursor()

now = datetime.now()
formatted_date = now.strftime("%Y%m%d%H%M%S%f")[:-5]

# 表名
table_name = "diary_log"
table_col = 'tags'

# 导出数据, 导出表到文件
with open(f'{formatted_date}_dump.sql', 'w') as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

# 添加新的一列
c.execute(f"ALTER TABLE {table_name} ADD COLUMN {table_col} TEXT")


# 提交事务并关闭连接
conn.commit()
conn.close()
