#!/usr/bin/env python
# coding=utf-8

# 将旧表数据插入新表，id 从 1 开始自增，其他列的值保持不变

import sys
# sys.path.insert(0,"")

from datetime import datetime
import sqlite3

from memocard.conf import CONF
from memocard.db import diary_log as diary_log_db
from memocard.app.diary_log.provider import Manager

DIARY_LOG_TABLE = CONF.diary_log['diary_log_table']
DATA_BASE_PATH = CONF.diary_log['data_base_path']
#path = "data/diary_log/diary_log_test.db"

conn = sqlite3.connect(DATA_BASE_PATH)
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

rows = diary_log_db.get_all_logs(table_name=DIARY_LOG_TABLE,
                                 columns=['id', 'content', 'tags'],
                                 data_base_path=DATA_BASE_PATH)
diary_log_manager = Manager()
new_rows = []
for row in rows:
    id, content, tags = row
    tags = diary_log_manager.get_tags_from_content(content)
    new_tags = ','.join(tags)
    new_rows.append((id, content, new_tags))
print(new_rows[1:3])

for row in new_rows:
    id ,content, new_tags = row
    # 构造 SQL 更新语句
    query = f"UPDATE {table_name} SET tags = '{new_tags}' WHERE id = {id}"
    # 执行更新操作
    c.execute(query)
    conn.commit()

