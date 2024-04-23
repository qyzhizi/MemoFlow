import os
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta

from memoflow.conf import CONF
from memoflow.utils.common import is_nested_list
from memoflow.driver.sqlite3_db.diary_log_tables import DiaryLogTable

LOG = logging.getLogger(__name__)
USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']
SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']

class DiaryLogDriver(object):

    def __init__(self, data_base_path):
        self.data_base_path = data_base_path

    
    def create_user_diary_table(self, table_name):
        DiaryLogTable(table_name=table_name,
                      database_path=self.data_base_path
                      ).create_diary_log_table()
    
    def get_logs_by_filters(
        self, filters,
        columns, table_name, 
        order_by="create_time", ascending=False,
        page_size=None, page_number=None):
        return DiaryLogTable(
            table_name, self.data_base_path).get_logs_by_filters(
            filters=filters,
            columns=columns,
            order_by=order_by,
            ascending=ascending,
            page_size=page_size,
            page_number=page_number)
    
    def insert_log_to_table(self, table_name, data_dict):
        return DiaryLogTable(
            table_name, self.data_base_path).insert_log_to_table(
            data_dict = data_dict
            )
    
    def delete_log_by_filters(self, table_name, filters):
        return DiaryLogTable(
            table_name, self.data_base_path).delete_log_by_filters(
            filters = filters
            )

    def update_log_by_id(self, table_name, update_data_dict):
        return DiaryLogTable(
            table_name, self.data_base_path).update_log_by_id(
            update_data_dict = update_data_dict
            )

    def update_log_by_filters(self, table_name,
                              update_data_dict, filters_dict):
        return DiaryLogTable(
            table_name, self.data_base_path).update_log_by_filters(
            update_data_dict = update_data_dict,
            filters_dict = filters_dict
            )

