#!/usr/bin/env python
# coding=utf-8
import os
import sys
import re

memoflow_parent_path = os.path.abspath(__file__).split("memoflow")[0]
os.chdir(memoflow_parent_path)
sys.path.insert(0, memoflow_parent_path)

from datetime import datetime
import sqlite3
from langchain.embeddings.openai import OpenAIEmbeddings

from memoflow.conf import CONF
from memoflow.driver.sqlite3_db.diary_log import DBSqliteDriver as diary_log_db
from memoflow.app.diary_log.provider import Manager

SYNC_TABLE_NAME = CONF.diary_log['SYNC_TABLE_NAME']
SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']
#path = "data/diary_log/diary_log_test.db"


BLOCK_SEPARATOR = r'\t+-\s'
# s is input text
def normalize_text(s, sep_token = " \n "):
    s = re.sub(BLOCK_SEPARATOR, "", s).strip()
    s = re.sub(r'@blk',  ' ', s).strip()
    s = re.sub(r'\s+',  ' ', s).strip()
    # s = re.sub(r". ,","",s)
    # remove all instances of multiple spaces
    s = s.replace("\n", "")
    s = s.replace("..",".")
    s = s.replace(". .",".")
    s = s.strip()
    
    return s




# df_bills['text']= df_bills["text"].apply(lambda x : normalize_text(x))

if __name__ == "__main__":

    rows = diary_log_db.get_all_logs(table_name=SYNC_TABLE_NAME,
                                     columns=['id', 'content', 'tags'],
                                     data_base_path=SYNC_DATA_BASE_PATH)
    
    # "#s?que" 匹配 "#que" "#sque"
    separators = ["#s?que", "#ans"]

    content_que_ans_list = []
    content_que_list = []
    clean_content_que_list = []
    for row in rows:
        id, content, tags = row
        if re.search(separators[0], content):
            content_split_0_list = re.split(f"({separators[0]})", content)
            for i in range(2, len(content_split_0_list), 2):
                content_que_ans_list.append((id, content_split_0_list[i]))
                # if re.search(separators[1], content_split_0_list[i]):
                content_split_1_list = re.split(f"({separators[1]})",
                                                content_split_0_list[i])
                content_que_list.append((id, content_split_1_list[0]))

    # normalize content_que_list
    for id, que_item in content_que_list:
        clean_content_que_list.append((id, normalize_text(que_item)))

