import os
import sqlite3
import re


def find_matching_lines(contents: list):
    # split contents to lines, splitlines() 方法用于按照行('\r', '\r\n', \n')分隔,
    # 返回一个包含各行作为元素的列表
    lines = []
    for content in contents:
        # lines.extend(content.split('\n'))
        lines.extend(content.splitlines())

    # 使用正则表达式匹配每一行，记录匹配到的行号和内容
    matches = []
    for i, line in enumerate(lines):
        if re.match(r'^##.*:$', line) or re.match(r'^- ##.*:$', line):
            matches.append((i, line))

    return matches, lines


def get_card_note_line_nextline(matches):
    res = []
    for i, item in enumerate(matches):
        item_line = item[0]
        if i < len(matches)-1:
            next_item_line = matches[i+1][0]
        else:
            next_item_line = None

        res.append([item_line, next_item_line])
    return res


def get_card_content(card_note_line_nextline, all_lines):
    card_content = []
    for line, nextline in card_note_line_nextline:
        nextline = nextline if nextline is not None else len(all_lines)

        content_list = all_lines[line:nextline]
        card_content.append('\n'.join(content_list))

    return card_content


def get_tags_from_content(content):
    """get tags

    Args:
        content (string): diary content

    Returns:
        list: tag list
    """
    # 匹配标签，找到所有的标签
    matches = re.findall(r"(?<!#)#\w+(?<!#)\s", content)
    tags = [match.strip('# \n') for match in matches]
    return tags

def get_new_card_content(all_card_content):
    new_all_card_content = []
    for id, content in enumerate(all_card_content):
        tags = get_tags_from_content(content)
        new_tags = ','.join(tags)
        new_all_card_content.append((id, content, new_tags))
    return new_all_card_content


def init_db_diary_log(data_base_path, table_name):

    if not os.path.exists(data_base_path):
        # 初始化数据库
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        c.execute(f'CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, tags TEXT)')
        conn.commit()
        conn.close()
    else:
        # delete all data
        conn = sqlite3.connect(data_base_path)
        c = conn.cursor()
        c.execute(f'DELETE FROM {table_name}')
        conn.commit()
        conn.close()


def crate_table(table_name, data_base_path, new_all_card_content):
    conn = sqlite3.connect(data_base_path)
    cursor = conn.cursor()
    for row in new_all_card_content:
        id ,content, tags = row
        # 构造 SQL 更新语句
        # 构造INSERT语句，并将数据绑定到占位符
        insert_sql = f"INSERT INTO {table_name} (content, tags) VALUES (?, ?)"
        cursor.execute(insert_sql, (content, tags))
        conn.commit()
    # 关闭数据库连接
    conn.close()


def process_file_content_2_db(contents: list, table_name, data_base_path):

    # 正则匹配，根据时间标题，找到所有的标题的位置
    # 调用函数并输出匹配到的行号和内容
    # filename = FILENAME
    matches, all_lines = find_matching_lines(contents)

    # 获取笔记的间隔点
    line_nextline = get_card_note_line_nextline(matches=matches)

    # 获取了所有笔记列表
    all_card_content = get_card_content(card_note_line_nextline=line_nextline,
                                        all_lines=all_lines)

    # 逆序
    all_card_content.reverse()
    # 生成新的内容，添加了tags
    new_all_card_content = get_new_card_content(all_card_content=all_card_content)
    
    # delete all data
    init_db_diary_log(data_base_path, table_name)
    
    #生成数据表
    crate_table(table_name, data_base_path,
                new_all_card_content=new_all_card_content)
