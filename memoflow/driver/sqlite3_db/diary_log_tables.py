import logging
import sqlite3
import uuid

LOG = logging.getLogger(__name__)

class BaseTable():

    table_columns = []
    safe_columns = []
    def __init__(self, table_name, data_base_path) -> None:
       self.table_name = table_name
       self.data_base_path = data_base_path

    def initialize_table(self,  table_columns):
        """Initialize the table by creating it if it doesn't exist."""
        LOG.info("Initializing table in database: %s", self.data_base_path)
        try:
            with sqlite3.connect(self.data_base_path) as conn:
                self.create_table(conn, table_columns)
            LOG.info("Table %s created or already exists.", self.table_name)
        except sqlite3.Error as e:
            LOG.error("Failed to initialize table %s: %s", self.table_name, e)

    
    def create_table(self, conn, table_columns):
        """Create the table based on the columns defined in table_columns."""
        columns_sql = ", ".join([" ".join(column) for column in table_columns])
        table_creation_sql = \
            f"CREATE TABLE IF NOT EXISTS {self.table_name} ({columns_sql})"

        try:
            c = conn.cursor()
            c.execute(table_creation_sql)
        except sqlite3.Error as e:
            LOG.error("Error creating table %s: %s", self.table_name, e)
            raise
    
    def get_records_by_filters(
            self,
            filters, columns, 
            order_by="create_time", ascending=False,
            page_size=None, page_number=None,
            ):
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
        # 校验列名
        for column in columns:
            if column not in self.safe_columns:
                raise ValueError(f"Unsafe column name: {column}")
        # 校验表名
        if self.table_name not in self.safe_table_names:
            raise ValueError(f"Unsafe table name: {self.table_name}")

        # # Construct SQL query
        if filters:
            condition_clause = []
            for key, value in filters.items():
                # 校验列名是否安全 最好是本表的列名
                if key not in self.safe_columns:
                    raise ValueError(
                        f"Unsafe column name in filters: {key}")

                if "%" in value:
                    condition_clause.append(f"{key} LIKE ?")
                else:
                    condition_clause.append(f"{key} = ?")
            conditions = ' AND '.join(condition_clause)
            query = \
                f"SELECT {', '.join(columns)} FROM {self.table_name} WHERE {conditions}"
            parameters = tuple(filters.values())
        else:
            query = f"SELECT {', '.join(columns)} FROM {self.table_name}"
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
            with sqlite3.connect(self.data_base_path) as conn:
                conn.row_factory = sqlite3.Row  # 设置行格式为字典
                c = conn.cursor()
                # Execute query
                rows = c.execute(query, parameters).fetchall()

                return [dict(row) for row in rows]
        except Exception as e:
            LOG.error(f"An error occurred: {str(e)}")
            return None

    def insert_columns_to_table(self, data_dict):
        """Inserts columns to a table in a database.

        Args:
            table_name (str): The name of the table to insert data into.
            data_dict (dict): A dictionary containing column names as keys
                             and corresponding data as values.
            data_base_path (str): The path to the database file.

        Returns:
            None
        """
        with sqlite3.connect(self.data_base_path) as conn:
            c = conn.cursor()
            columns = tuple(data_dict.keys())
            data = tuple(data_dict.values())
            placeholders = ', '.join(['?'] * len(columns))
            query = f"""
                INSERT INTO {self.table_name}
                ({', '.join(columns)})
                VALUES
                ({placeholders})
            """
            c.execute(query, data)

    def delete_records_by_filters(self, filters):
        """Delete records based on multiple filters conditions."""
        with sqlite3.connect(self.data_base_path) as conn:
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
            c.execute(f"DELETE FROM {self.table_name} WHERE {where_clause}", values)
            conn.commit()

    def update_record_to_table_by_id(
        self, record_id, update_data_dict):
        with sqlite3.connect(self.data_base_path) as conn:
            c = conn.cursor()
            set_clause = ', '.join(
                [f"{key} = ?" for key in update_data_dict.keys()])
            query = f'''
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE id = ?
            '''
            data = tuple(update_data_dict.values()) + (record_id,)
            c.execute(query, data)
            conn.commit()
            return True if c.rowcount > 0 else False
    
    def update_record_to_table_by_filters(self, update_data_dict, filters_dict):
        with sqlite3.connect(self.data_base_path) as conn:
            c = conn.cursor()
            # 准备更新的字段
            set_clause = ', '.join([f"{key} = ?" for key in update_data_dict.keys()])
            update_values = tuple(update_data_dict.values())
        
            # 准备过滤条件
            filter_clauses = []
            filter_values = []
            for key, value in filters_dict.items():
                if '%' in value or '_' in value: # 假设值中包含%或_，则使用LIKE
                    filter_clauses.append(f"{key} LIKE ?")
                else:
                    filter_clauses.append(f"{key} = ?")
                filter_values.append(value)
        
            filter_clause = ' AND '.join(filter_clauses)
        
            # 构造完整的SQL查询
            query = f'''
                UPDATE {self.table_name}
                SET {set_clause}
                WHERE {filter_clause}
            '''
        
            # 合并更新数据和过滤条件的值
            data = tuple(update_values) + tuple(filter_values)
        
            # 执行查询
            c.execute(query, data)
            conn.commit()
        
            # 根据影响的行数返回结果
            return True if c.rowcount > 0 else False


class DiaryLogTable(BaseTable):
    table_columns = [
        ('id', 'CHAR(36) PRIMARY KEY'),
        ('content', 'TEXT'),
        ('tags', 'TEXT'),
        ('sync_file', 'VARCHAR(512)'),
        ('update_time', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
        ('create_time', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    ]
    safe_columns = {column[0] for column in table_columns}
    def __init__(self, table_name, data_base_path):
        super().__init__(table_name, data_base_path)

    def create_diary_log_table(self):
        self.initialize_table(self.table_columns)
    
    def get_logs_by_filters(self, filters, columns,
            order_by="create_time", ascending=False,
            page_size=None, page_number=None):
        self.get_records_by_filters(filters=filters,
                                   columns=columns,
                                   order_by=order_by,
                                   ascending=ascending,
                                   page_size=page_size,
                                   page_number=page_number,
                                   )
    
    def insert_log_to_table(self,  data_dict):
        self.insert_columns_to_table(data_dict)
    
    def delete_log_by_filters(self, filters):
        self.delete_records_by_filters(filters=filters)
    
    def update_log_by_id(self, update_data_dict):
        self.update_record_to_table_by_id(update_data_dict)
    
    def update_log_by_filters(self, update_data_dict, filters_dict):
        self.update_record_to_table_by_filters(
            update_data_dict, filters_dict)


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    diary_log_table = DiaryLogTable("diary_log", "example.db")
    diary_log_table.create_diary_log_table()

    diary_log_table.insert_log_to_table(
        {"id": "123454365667892",
         "tags": "3334654334",
        "content": "Hello, world!5675686798"})

    # diary_log_table.delete_log_by_filters({"content": "Hello, world!"})

    # diary_log_table.update_record_to_table_by_id("12345678", {"content": "xxxx"})

    diary_log_table.update_record_to_table_by_filters(
        update_data_dict={'tags': '2222', 'content':'333333'},
        filters_dict={'id':"%45436566%"}
    )

