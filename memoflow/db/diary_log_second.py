import os
import logging
import sqlite3
from memoflow.conf import CONF

LOG = logging.getLogger(__name__)

def init_db_diary_log_second():

    # 初始化数据库
    data_base_path = CONF.diary_log_second['data_base_path']
    # 判断data_base_path是否存在，不存在则创建
    dir_path = os.path.dirname(data_base_path)
    if not os.path.exists(dir_path):
        LOG.info("diary_log数据库路径不存在，创建路径: %s", dir_path)
        os.makedirs(dir_path)

    LOG.info("初始化diary_log_second数据库路径：%s", data_base_path)
    conn = sqlite3.connect(data_base_path)
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS diary_log_second (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)')
    conn.commit()
    conn.close()