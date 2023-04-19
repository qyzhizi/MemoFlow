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
new_table_name = "new_diary_log"

# 导出数据
# 导出表到文件
with open(f'{formatted_date}_dump.sql', 'w') as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

# 获取表结构信息
c.execute(f'PRAGMA table_info({table_name});')
table_info = c.fetchall()

# 构建新表CREATE TABLE SQL语句
col_defs = []
pk_key = None
print(table_info)
for col_index, col_name, col_type, not_null, default_value, pk in table_info:
    if pk == 1:
        pk_key = col_name
        col_defs.append(f'{col_name} INTEGER PRIMARY KEY AUTOINCREMENT')
    else:
        col_defs.append(f'{col_name} {col_type}')
create_table_sql = f'CREATE TABLE {new_table_name} ({", ".join(col_defs)})'
print(create_table_sql)

# 执行CREATE TABLE
c.execute(create_table_sql)

# 获取所有行
rows = c.execute(f'SELECT * FROM {table_name} ORDER BY rowid ASC').fetchall()

# 将每一行数据转换为字典的形式, 去除了主键
result = []
for row in rows:
    row_dict = {}
    for i, col in enumerate(c.description):
        # 去除主键
        if col[0] == pk_key:
            continue
        row_dict[col[0]] = row[i]
    result.append(row_dict)

# 创建插入语句
my_dict_one = result[0]
columns = ', '.join(my_dict_one.keys())
placeholders = ', '.join('?' * len(my_dict_one))
# 插入到diary_log_new 表中
insert_sql = f'INSERT INTO {new_table_name} ({columns}) VALUES ({placeholders})'

for my_dict in result:
    # 将字典的内容插入到数据库的一行中
    values = tuple(my_dict.values())
    c.execute(insert_sql, values)

# 删除旧表，重命名新表
c.execute(f'DROP TABLE {table_name}')
c.execute(f'ALTER TABLE {new_table_name} RENAME TO {table_name}')

# 提交事务并关闭连接
conn.commit()
conn.close()
