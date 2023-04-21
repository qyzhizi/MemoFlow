import logging
import sqlite3

LOG = logging.getLogger(__name__)

def init_db_diary_log(data_base_path, table_name):

    # 初始化数据库
    LOG.info("初始化diary_log数据库路径: %s", data_base_path)
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, tags TEXT)')
    conn.commit()
    conn.close()

def create_table(data_base_path, table_name):
    """创建表
    """
    LOG.info("初始化review_diary_log数据库路径: %s", data_base_path)
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    c.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT,  tags TEXT)')
    conn.commit()
    conn.close()

def get_all_logs(table_name, columns, data_base_path):
    """get all logs form one table columns

    Args:
        table_name (string): _description_
        columns (tuple or list): (content , tags)

    Returns:
        list: [[content1, tags1], [content2, tags2], ...]
    """
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    query = f"SELECT {', '.join(columns)} FROM {table_name}"
    rows = c.execute(query).fetchall()
    # res = [[row[0], row[1]] for row in rows]
    conn.commit()
    conn.close()
    return rows

def delete_all_log(table_name, data_base_path):
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    # 执行DELETE语句，删除表中的所有数据
    c.execute(f'DELETE FROM {table_name}')
    # 提交更改并关闭连接
    conn.commit()
    conn.close()

def get_rows_by_tags(table_name, tags, data_base_path):
    """

    Args:
        table_name (string): _description_
        tags (list): tag list

    Returns:
        list: _description_
    """
    if tags is None:
        return None
    
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    # 构造 SQL 查询语句
    query = f"SELECT * FROM {table_name} WHERE "
    for i, tag in enumerate(tags):
        if i > 0:
            query += "OR "
        query += f"tags LIKE '%{tag}%' "
    LOG.info(f"query: {query}")
    # 执行查询并获取结果
    c.execute(query)
    rows = c.fetchall()
    conn.commit()
    conn.close()
    return rows

def inser_diary_to_table(table_name, content, tags, data_base_path):
    """向diary_log 或具有相同结构的表中插入一个记录

    Args:
        table_name (string): table name
        content (string): 笔记内容
        tags (string): 逗号分割的字符串
    """
    LOG.info(f"插入笔记, diary_log数据库: {data_base_path}, 数据表: {table_name}")
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    c.execute(f'INSERT INTO {table_name}  (content, tags) VALUES (?, ?)', (content, tags))
    conn.commit()
    conn.close()
