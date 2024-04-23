import os
import logging
import sqlite3
import uuid
from datetime import datetime, timedelta

from memoflow.conf import CONF
from memoflow.utils.common import is_nested_list

LOG = logging.getLogger(__name__)
USER_TABLE_NAME = CONF.diary_log['USER_TABLE_NAME']
SYNC_DATA_BASE_PATH = CONF.diary_log['SYNC_DATA_BASE_PATH']

class DBSqliteDriver(object):
    safe_table_names = []
    safe_table_columns = set()
    @classmethod
    def init_db_diary_log(cls, data_base_path):
        # 初始化数据库
        LOG.info("初始化diary_log数据库路径: %s", data_base_path)
        # 判断data_base_path是否存在，不存在则创建
        dir_path = os.path.dirname(data_base_path)
        if not os.path.exists(dir_path):
            LOG.info("同步数据库路径不存在，创建路径: %s", dir_path)
            os.makedirs(dir_path)

    @classmethod
    def create_table(cls, conn, table_name, table_columns):
        """Create the table based on the columns defined in table_columns."""
        columns_sql = ", ".join([" ".join(column) for column in table_columns])
        table_creation_sql = \
            f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
        
        try:
            c = conn.cursor()
            c.execute(table_creation_sql)
        except sqlite3.Error as e:
            LOG.error("Error creating table %s: %s", table_name, e)
            raise
    
    @classmethod
    def initialize_table(cls, database_path, table_name, table_columns):
        """Initialize the table by creating it if it doesn't exist."""
        LOG.info("Initializing table in database: %s", database_path)
        try:
            with sqlite3.connect(database_path) as conn:
                cls.create_table(conn, table_name, table_columns)
            LOG.info("Table %s created or already exists.", table_name)
        except sqlite3.Error as e:
            LOG.error("Failed to initialize table %s: %s", table_name, e)
    
    @classmethod
    def create_diary_log_table(cls, data_base_path, table_name):
        """Create table."""
        LOG.info("Initializing database path: %s", data_base_path)
        
        table_columns = [
            ('id', 'CHAR(36) PRIMARY KEY'),
            ('content', 'TEXT'),
            ('tags', 'TEXT'),
            ('sync_file', 'VARCHAR(512)'),
            ('update_time', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
            ('create_time', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        ]
        cls.initialize_table(data_base_path, table_name, table_columns)
        LOG.info("Table created successfully: %s", table_name)
    
    @classmethod
    def create_user_table(cls, data_base_path, user_table_name):
        """创建表
        """
        LOG.info(f"创建数据表: {user_table_name}, 所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {user_table_name} ("
                f"id CHAR(36) PRIMARY KEY, "
                f"username VARCHAR(255) NOT NULL, "
                f"password VARCHAR(255) NOT NULL, "
                f"salt VARCHAR(255) NOT NULL, "
                f"email VARCHAR(255), "
                f"diary_table_name CHAR(255) NOT NULL, "
                f"avatar_image TEXT"
                f")"
            )

    @classmethod
    def create_user_settings_table(cls, data_base_path,
                                   user_settings_table_name):
        # 使用 with 语法创建数据库连接，并自动管理连接的打开和关闭
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            # 创建 user_settings 表
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {user_settings_table_name} ("
                f"user_id INTEGER, "
                f"setting_key VARCHAR(255), "
                f"setting_value TEXT, "
                f"PRIMARY KEY (user_id, setting_key)"
                f")"
            )
            # 提交事务
            conn.commit()

    @classmethod
    def create_github_access_table(cls, data_base_path, user_table_name,
                                   github_access_table_name):
        """创建表
        """
        LOG.info(f"创建数据表: {github_access_table_name}, 所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {github_access_table_name} ("
                f"id CHAR(36) PRIMARY KEY, "
                f"user_id CHAR(36) NOT NULL, "
                f"github_repo_name VARCHAR(255), "
                f"current_sync_file VARCHAR(512), "
                f"other_sync_file_list TEXT, "
                f"access_token VARCHAR(255), "
                f"access_token_expires_at DATETIME, "
                f"refresh_token VARCHAR(255), "
                f"refresh_token_expires_at DATETIME, "
                f"github_user_name VARCHAR(255), "
                f"FOREIGN KEY (user_id) REFERENCES {user_table_name}(id)"
                f")"
            )

    @classmethod
    def create_jianguoyun_access_table(cls, data_base_path, user_table_name,
                                   jianguoyun_access_table_name):
        """创建表
        """
        LOG.info(f"创建数据表: {jianguoyun_access_table_name},"
                 f"所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"CREATE TABLE IF NOT EXISTS {jianguoyun_access_table_name} ("
                f"id CHAR(36) PRIMARY KEY, "
                f"user_id CHAR(36) NOT NULL, "
                f"jianguoyun_account VARCHAR(512), "
                f"current_sync_file VARCHAR(512), "
                f"other_sync_file_list TEXT, "
                f"jianguoyun_token VARCHAR(255), "
                f"FOREIGN KEY (user_id) REFERENCES {user_table_name}(id)"
                f")"
            )

    
    @classmethod
    def add_user(cls,
                 user_id,
                 username, password, salt, email, diary_table_name,
                 data_base_path, table_name):
        LOG.info(f"add_user: {table_name}, 所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f'INSERT INTO {table_name}'
                f"(id, username, password, salt, email, diary_table_name) "
                f'VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, username, password, salt, email, diary_table_name)
            )

    @classmethod
    def update_users_field(cls, user_id, field_dict, data_base_path, table_name):
        """更新用户表中的字段值"""
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            # 检查用户是否存在
            cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (user_id,))
            result = cursor.fetchone()
            if result is None:
                raise ValueError("用户不存在")  # 抛出异常或返回错误消息
        
            # 更新字段值
            set_clause = ", ".join([f"{key} = ?" for key in field_dict.keys()])
            values = tuple(field_dict.values()) + (user_id,)
            cursor.execute(
                f"UPDATE {table_name} SET {set_clause} WHERE id = ?",
                values
            )

    @classmethod
    def get_table_name_by_user_id(
        cls,
        user_id,
        data_base_path=SYNC_DATA_BASE_PATH,
        table_name = USER_TABLE_NAME
        ):
        # user table func

        LOG.info(f"get_table_name_by_user_id 所在数据库: "
                 f"{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            conn.row_factory = sqlite3.Row  # 设置行格式为字典
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT diary_table_name FROM {table_name} WHERE id = ?',
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                return result['diary_table_name']
            else:
                return None

    @classmethod
    def get_user_info_by_username(cls, username, data_base_path, table_name):
        LOG.info(f"get_user_info_by_username: {table_name}, \
                 所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            conn.row_factory = sqlite3.Row  # 设置行格式为字典
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT * FROM {table_name} WHERE username = ?',
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                return dict(result)
            else:
                return None
    
    @classmethod
    def get_user_info_by_id(cls, user_id, data_base_path, table_name):
        LOG.info(f"get_user_info_by_id: {table_name},\
                 所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            conn.row_factory = sqlite3.Row  # 设置行格式为字典
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT * FROM {table_name} WHERE id = ?',
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                return dict(result)
            else:
                return None
    
    @classmethod
    def update_user_settings_to_db(
        cls,
        user_id: str,
        user_settings: dict,
        data_base_path: str,
        table_name: str
    ) -> None:
        # 构建 user_settings_list 列表
        user_settings_list = [(user_id, key, str(value)) 
                              for key, value in user_settings.items()]

        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()

            # 插入或更新多个用户设置
            cursor.executemany(
                f"INSERT OR REPLACE INTO {table_name} "
                f"(user_id, setting_key, setting_value) VALUES (?, ?, ?)",
                  user_settings_list)

            # 提交事务
            conn.commit()
    
    @classmethod
    def get_user_settings(
        cls, user_id: str, data_base_path: str, table_name: str) -> dict:
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()

            # 查询用户设置
            cursor.execute(f"SELECT setting_key, setting_value FROM {table_name} "
                           f"WHERE user_id=?", (user_id,))
            rows = cursor.fetchall()

            # 将查询结果转换为字典形式
            user_settings = {row[0]: row[1] for row in rows}

            return user_settings

    @classmethod
    def user_add_or_update_github_access_data(
        cls,
        user_id, 
        data_dict,
        data_base_path,
        table_name):
        
        LOG.info(f"user_add_or_update_github_access_data: {table_name}, \
                所在数据库：{data_base_path}")
        
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            # Check if user_id exists in the table
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} "
                           f"WHERE user_id=?", (user_id,))
            result = cursor.fetchone()
            count = result[0] if result else 0

            if count > 0:  # User exists, perform update
                columns = ','.join([f"{key}=?" for key in data_dict.keys()])
                values = tuple(data_dict.values()) + (user_id,)
                cursor.execute(
                    f"UPDATE {table_name} SET {columns} WHERE user_id=?",
                    values
                )
            else:  # User does not exist, perform insert
                columns = ','.join(data_dict.keys())
                placeholders = ','.join(['?'] * len(data_dict))
                values =  (str(uuid.uuid4()), user_id) + tuple(data_dict.values())
                cursor.execute(
                    f"INSERT INTO {table_name} (id, user_id, {columns}) "
                    f"VALUES (?, ?, {placeholders})",
                    values
                )

        return True
    
    @classmethod
    def user_add_or_update_data_to_db(
        cls,
        user_id: str,
        data_dict: dict,
        data_base_path: str,
        table_name: str):

        LOG.info(f"user_add_jianguoyun_access_data: {table_name}, \
                所在数据库：{data_base_path}")

        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            # Check if user_id exists in the table
            cursor.execute(f"SELECT COUNT(*) FROM {table_name} "
                           f"WHERE user_id=?", (user_id, ))
            result = cursor.fetchone()
            count = result[0] if result else 0

            if count > 0:  # User exists, perform update
                columns = ','.join([f"{key}=?" for key in data_dict.keys()])
                values = tuple(data_dict.values()) + (user_id,)
                cursor.execute(
                    f"UPDATE {table_name} SET {columns} WHERE user_id=?",
                    values
                )
            else:  # User does not exist, perform insert
                columns = ','.join(data_dict.keys())
                placeholders = ','.join(['?'] * len(data_dict))
                values =  (str(uuid.uuid4()), user_id) + tuple(data_dict.values())
                cursor.execute(
                    f"INSERT INTO {table_name} (id, user_id,{columns}) "
                    f"VALUES (?, ?, {placeholders})",
                    values
                )

    @classmethod
    def user_partial_update_github_access_data_to_db(
        cls,
        update_values,
        conditions,
        table_name,
        data_base_path
        ):
        LOG.info(f"db update,  user_partial_update_github_access_data_to_db: \
                 {table_name}, data_base_path: {data_base_path}")
        
        with sqlite3.connect(data_base_path) as conn:
            cursor = conn.cursor()
            # 构建 SQL 查询语句
            set_clause = ', '.join([f"{key} = ?" for key in update_values.keys()])
            condition_clause = ' AND '.join([f"{key} = ?" for key in conditions.keys()])
            # 构建更新语句
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition_clause}"
            # 执行更新
            cursor.execute(
                sql, 
                tuple(update_values.values()) + tuple(conditions.values()))
            
    @classmethod
    def get_github_access_info_by_user_id(
        cls, user_id, data_base_path, table_name):
        """_summary_

        Args:
            user_id (_type_): _description_
            data_base_path (_type_): _description_
            table_name (_type_): _description_

        Returns:
            dict: dict type
        """
        LOG.info(f"get_github_access_info_by_user_id: {table_name}, \
                所在数据库：{data_base_path}")
        with sqlite3.connect(data_base_path) as conn:
            conn.row_factory = sqlite3.Row  # 设置行格式为字典
            cursor = conn.cursor()
            cursor.execute(
                f'SELECT * FROM {table_name} WHERE user_id = ?',
                (user_id,)
            )
            result = cursor.fetchone()

            if result:
                return dict(result)
            else:
                return {}
    
    @classmethod
    def get_record_by_filters(
        cls, filters:dict, data_base_path: str, table_name: str):
        with sqlite3.connect(data_base_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # 构建 SQL 查询中的 WHERE 子句
            where_conditions = []
            values = []
            for key, value in filters.items():
                if "%" in value:
                    where_conditions.append(f"{key} LIKE ?")
                else:
                    where_conditions.append(f"{key} = ?")
                values.append(value)

            where_clause = " AND ".join(where_conditions)
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE {where_clause}",
                values
            )
            result = cursor.fetchone()

            if result:
                return dict(result)
            else:
                return {}

    @classmethod
    def search_content_by_string(
        cls, data_base_path, table_name, search_string):
        """Search for records where content contains a specific string."""
        LOG.info("Searching for records containing: %s", search_string)
        with sqlite3.connect(data_base_path) as conn:
            c = conn.cursor()
            # 使用参数化查询来防止SQL注入
            query = f"SELECT * FROM {table_name} WHERE content LIKE ?"
            c.execute(query, (f"%{search_string}%",))
            results = c.fetchall()

        if results:
            LOG.info("Found %d records containing the string: %s", 
                     len(results), search_string)
        else:
            LOG.info("No records found containing the string: %s", 
                     search_string)

        return results

    @classmethod
    def delete_record_by_filters(
        cls, filters:dict, data_base_path: str, table_name: str):
        with sqlite3.connect(data_base_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # 构建 SQL 查询中的 WHERE 子句
            where_conditions = []
            values = []
            for key, value in filters.items():
                if "%" in value:
                    where_conditions.append(f"{key} LIKE ?")
                else:
                    where_conditions.append(f"{key} = ?")
                values.append(value)

            where_clause = " AND ".join(where_conditions)
            cursor.execute(
                f"DELETE * FROM {table_name} WHERE {where_clause}",
                values
            )

    @classmethod
    def init_db_clipboard_log(cls, data_base_path, table_name):

        # 判断data_base_path是否存在，不存在则创建
        dir_path = os.path.dirname(data_base_path)
        if not os.path.exists(dir_path):
            LOG.info("clipboard 数据库路径不存在，创建路径: %s", dir_path)
            os.makedirs(dir_path)

        # 初始化clipboard数据库
        LOG.info("初始化clipboard_log数据库路径: %s", data_base_path)
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        c.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id TEXT PRIMARY KEY, content TEXT)')
        conn.commit()
        conn.close()

    @classmethod
    def get_all_logs(cls, table_name, columns, data_base_path):
        """get all logs form one table columns

        Args:
            table_name (string): _description_
            columns (tuple or list): (content , tags)

        Returns:
            list: [[content1, tags1], [content2, tags2], ...]
        """
        try:
            conn = sqlite3.connect(data_base_path)
            c = conn.cursor()
            query = f"SELECT {', '.join(columns)} FROM {table_name}"
            rows = c.execute(query).fetchall()
            conn.commit()
            conn.close()
            return rows
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return None

    @classmethod
    def get_logs_by_filters(cls,
            filters, columns, table_name, data_base_path,
            order_by="create_time", ascending=False,
            page_size=None, page_number=None):
        """get logs by filters with pagination

        Args:
            table_name (string): _description_
            filters (dict): {key: value}
            columns (tuple or list): (content, tags)
            order_by (string, optional): Column name to order by.
                Defaults to "create_time".
            ascending (bool, optional): Whether to sort in ascending order.
                Defaults to False (descending).
            page_size (int, optional): Number of records to display per page.
            page_number (int, optional): Page number to retrieve.

        Returns:
            list: [[content1, tags1], [content2, tags2], ...]
        """
        # # 校验列名
        # for column in columns:
        #     if column not in cls.safe_table_columns:
        #         raise ValueError(f"Unsafe column name: {column}")
        # # 校验表名
        # if table_name not in cls.safe_table_names:
        #     raise ValueError(f"Unsafe table name: {table_name}")
        
        # # Construct SQL query
        if filters:
            condition_clause = []
            for key, value in filters.items():
                # # 校验列名是否安全 最好是本表的列名
                # if key not in cls.safe_table_columns:
                #     raise ValueError(
                #         f"Unsafe column name in filters: {key}")
                        
                if "%" in value:
                    condition_clause.append(f"{key} LIKE ?")
                else:
                    condition_clause.append(f"{key} = ?")
            conditions = ' AND '.join(condition_clause)
            query = \
                f"SELECT {', '.join(columns)} FROM {table_name} WHERE {conditions}"
            parameters = tuple(filters.values())
        else:
            query = f"SELECT {', '.join(columns)} FROM {table_name}"
            parameters = ()

        # Add ORDER BY clause if order_by is provided
        if order_by:
            order_direction = "ASC" if ascending else "DESC"
            query += f" ORDER BY {order_by} {order_direction}"

        # Add pagination if page_size and page_number are provided
        if page_size and page_number:
            offset = (page_number - 1) * page_size
            query += f" LIMIT {page_size} OFFSET {offset}"

        try:
            with sqlite3.connect(data_base_path) as conn:
                conn.row_factory = sqlite3.Row  # 设置行格式为字典
                c = conn.cursor()
                # Execute query
                rows = c.execute(query, parameters).fetchall()

                return [dict(row) for row in rows]
        except Exception as e:
            LOG.error(f"An error occurred: {str(e)}")
            return None
    
    @classmethod
    def get_log_by_id(cls, table_name, id, columns, data_base_path):
        """get log by id

        Args:
            table_name (string): _description_
            id (string): _description_
            columns (tuple or list): (content, tags)

        Returns:
            list: [content, tags]
        """
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        query = f"SELECT {', '.join(columns)} FROM {table_name} WHERE id = ?"
        row = c.execute(query, (id,)).fetchone()
        conn.commit()
        conn.close()
        return row if row else None
    
    @classmethod
    def update_log_to_table(
        cls, id, update_data_dict, table_name, data_base_path):
        with sqlite3.connect(data_base_path) as conn:
            c = conn.cursor()
            set_clause = ', '.join(
                [f"{key} = ?" for key in update_data_dict.keys()])
            query = f'''
                UPDATE {table_name}
                SET {set_clause}
                WHERE id = ?
            '''
            data = tuple(update_data_dict.values()) + (id,)
            c.execute(query, data)
            conn.commit()
            return True if c.rowcount > 0 else False
    
    @classmethod
    def delete_log(cls, id, table_name, data_base_path):
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        # 执行DELETE语句，删除表中的数据
        c.execute(f'DELETE FROM {table_name} WHERE id = ?', (id,))
        # 提交更改并关闭连接
        conn.commit()
        conn.close()
        return True if c.rowcount > 0 else False

    @classmethod
    def delete_records_not_in_list(cls, table_name, data_base_path,
                                   field_name, values_to_keep):
        with sqlite3.connect(data_base_path) as conn:
            c = conn.cursor()
            # 使用 NOT IN 条件删除不在给定列表中的记录
            query = f'DELETE FROM {table_name} WHERE {field_name} NOT IN \
                ({",".join("?" * len(values_to_keep))})'
            c.execute(query, values_to_keep)
            # 提交更改
            conn.commit()
            return True if c.rowcount > 0 else False
    
    @classmethod
    def delete_records_by_filters(cls, data_base_path, table_name, filters):
        """Delete records based on multiple filters conditions."""
        with sqlite3.connect(data_base_path) as conn:
            c = conn.cursor()

            # 构建 SQL 查询中的 WHERE 子句
            where_conditions = []
            values = []
            for key, value in filters.items():
                if "%" in value:
                    where_conditions.append(f"{key} LIKE ?")
                else:
                    where_conditions.append(f"{key} = ?")
                values.append(value)

            where_clause = " AND ".join(where_conditions)

            # 执行删除操作
            c.execute(f"DELETE FROM {table_name} WHERE {where_clause}", values)
            conn.commit()

    @classmethod
    def delete_all_log(cls, table_name, data_base_path):
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        # 执行DELETE语句，删除表中的所有数据
        c.execute(f'DELETE FROM {table_name}')
        # 提交更改并关闭连接
        conn.commit()
        conn.close()

    @classmethod
    def get_rows_by_tags(cls, table_name, tags, data_base_path):
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

    @classmethod
    def inser_diary_to_table(
        cls, 
        content, tags, table_name, 
        data_base_path, **kwargs):
        """Insert a record into diary_log or a table with the same structure.

        Args:
            table_name (string): Table name.
            content (string): Note content.
            tags (string): Comma-separated string of tags.
            **kwargs: Additional keyword arguments including optional parameters.

        Returns:
            string: Record id.
        """
        record_id = str(uuid.uuid4())
        try:
            LOG.info(
                f"Inserting note into diary_log database: \
                {data_base_path}, table: {table_name}, record_id: {record_id}")
            with sqlite3.connect(data_base_path) as conn:
                c = conn.cursor()
                column_names = ', '.join(kwargs.keys())
                column_names_str = f", {column_names}" if column_names else ''
                # placeholders = ', '.join([f"{key} = ?" for key in kwargs.keys()])
                placeholders = ', '.join(['?'] * len(kwargs.keys()))
                if placeholders:
                    placeholders = f", {placeholders}"
                full_column_names_str = f"id, content, tags, update_time, \
                    create_time{column_names_str}"
                values = (record_id, content, tags) + tuple(kwargs.values())
                c.execute(
                    f"INSERT INTO {table_name} "
                    f"({full_column_names_str}) "
                    f"VALUES "
                    f"(?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP{placeholders})",
                    values)
            LOG.info(f"Note inserted successfully with record_id: {record_id}")
        except Exception as e:
            LOG.error(f"Error occurred while inserting note into database: {e}")
            record_id = None

        return record_id

    @classmethod
    def insert_batch_records(
        cls, columns: list[str], records: list[list[str]], table_name: str,
        data_base_path: str):
        """Batch insert records. create_time update_time is same order 
        with records"""
        if not records:
            return

        if not is_nested_list(columns, str) or not is_nested_list(records, str):
            raise ValueError("Only allow nested lists of simple non-iterated"
                             "elements (excluding strings)")

        if len(columns) != len(records[0]):
            raise ValueError("Number of columns and records do not match.")
        
        # Check if 'create_time' and 'update_time' are present in columns
        no_create_time = 'create_time' not in columns
        no_update_time = 'update_time' not in columns
        if no_update_time:
            columns.append('update_time')
        if no_create_time:
            columns.append('create_time')

        # Check if 'id' column is present in columns
        if 'id' not in columns:
            columns.insert(0, 'id')  # Add 'id' column at the beginning
            '''Generate UUID for each record and insert it as the first 
               element of each record'''
            for record in records:
                # Insert UUID at the beginning of each record
                record.insert(0, str(uuid.uuid4()))

        # Prepare values for create_time and update_time if needed
        time_values = []
        if no_create_time or no_update_time:
            # Calculate the initial time
            current_time = datetime.now().replace(microsecond=0)-\
                 timedelta(seconds=len(records)) 
            time_values = [(current_time + timedelta(seconds=i),
                            current_time + timedelta(seconds=i)) 
                           for i in range(len(records))]

        # Generate records to be inserted using list comprehension
        records_to_insert = [
            record + ([time_values[i][0]] if no_create_time else []) + \
                ([time_values[i][1]] if no_update_time else [])
            for i, record in enumerate(records)
        ]      

        with sqlite3.connect(data_base_path) as conn:
            c = conn.cursor()
            # Construct the placeholders for the values
            placeholders = ', '.join(['?' for _ in columns])
                
            # Insert the records into the table
            c.executemany(
                f"INSERT INTO {table_name} ({', '.join(columns)}) "
                f"VALUES ({placeholders})",
                records_to_insert
            )
            conn.commit()

    @classmethod
    def insert_columns_to_table(cls, table_name, data_dict, data_base_path):
        """Inserts columns to a table in a database.

        Args:
            table_name (str): The name of the table to insert data into.
            data_dict (dict): A dictionary containing column names as keys
                             and corresponding data as values.
            data_base_path (str): The path to the database file.

        Returns:
            None
        """
        with sqlite3.connect(data_base_path) as conn:
            c = conn.cursor()
            columns = tuple(data_dict.keys())
            data = tuple(data_dict.values())
            placeholders = ', '.join(['?'] * len(columns))
            query = f"""
                INSERT INTO {table_name}
                ({', '.join(columns)})
                VALUES
                ({placeholders})
            """
            c.execute(query, data)
