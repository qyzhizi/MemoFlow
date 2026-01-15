#!/usr/bin/env python
# coding=utf-8

# 将旧表数据插入新表，id 从 1 开始自增，其他列的值保持不变

import sys
# sys.path.insert(0,"")

from datetime import datetime, timezone
import sqlite3

from memoflow.conf import CONF
from memoflow.driver.sqlite3_db.diary_log import DBSqliteDriver as diary_log_db
from memoflow.app.diary_log.provider import Manager

SYNC_TABLE_NAME = CONF.diary_log['SYNC_TABLE_NAME']
SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
#path = "data/diary_log/diary_log_test.db"

conn = sqlite3.connect(SYNC_DATA_BASE_PATH)
c = conn.cursor()

now = datetime.now(timezone.utc)
formatted_date = now.strftime("%Y%m%d%H%M%S%f")[:-5]

# 表名
# table_name = "diary_log"
table_col = 'tags'

# 导出数据, 导出表到文件
with open(f'{formatted_date}_dump.sql', 'w') as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

rows = diary_log_db.get_all_logs(table_name=SYNC_TABLE_NAME,
                                 columns=['id', 'content', 'tags'],
                                 data_base_path=SYNC_DATA_BASE_PATH)
diary_log_manager = Manager()
new_rows = []
for row in rows:
    id, content, tags = row
    tags = diary_log_manager.get_tags_from_content(content)
    new_tags = ','.join(tags)
    new_rows.append((id, content, new_tags))

for row in new_rows:
    id ,content, new_tags = row
    # 构造 SQL 更新语句
    query = f"UPDATE {SYNC_TABLE_NAME} SET tags = '{new_tags}' WHERE id = {id}"
    # 执行更新操作
    c.execute(query)
    conn.commit()
    conn.close()  # 关闭连接

