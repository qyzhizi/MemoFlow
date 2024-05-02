import base64
import os
import re
import hashlib
import secrets
from collections.abc import Iterable
from memoflow.exception.visiable_exc import VisiblePathException

def is_base64_encoded(salt_base64):
    try:
        # 尝试将字符串解码为原始字节序列
        decoded = base64.b64decode(salt_base64.encode('utf-8'))
        # 如果成功解码，则说明是 Base64 编码的字符串
        return True
    except Exception as e:
        # 解码失败，说明不是 Base64 编码的字符串
        return False
    
def hash_password(password, salt:str=None):
    """
    salt : Base64 salt or bytes salt or None
    return : hashed_password and base64 salt
    """
    base64_salt = None
    if salt is None:
        bytes_salt = secrets.token_bytes(16)  # 生成随机盐
        # 将盐编码为 Base64 编码
        base64_salt = base64.b64encode(bytes_salt).decode('utf-8')
    try:
        # 尝试将字符串解码为原始字节序列
        if salt:
            bytes_salt = base64.b64decode(salt.encode('utf-8'))
            base64_salt = salt
        # 如果成功解码，则说明是 Base64 编码的字符串
    except Exception as e:
        # 解码失败，说明不是 Base64 编码的字符串
        bytes_salt = salt
        base64_salt = base64.b64encode(salt).decode('utf-8')
    
    # 使用 SHA-256 哈希函数对密码和盐进行加密
    hash_object = hashlib.sha256()
    hash_object.update(password.encode('utf-8') + bytes_salt)
    hashed_password = hash_object.hexdigest()

    return hashed_password, base64_salt


def filename_to_table_name(filename):
    # 去除非法字符
    cleaned_name = re.sub(r'[^\w\s]', '', filename)
    # 将空格替换为下划线
    cleaned_name = cleaned_name.replace(' ', '_')
    # 确保表名以字母开头
    if cleaned_name[0].isdigit():
        cleaned_name = '_' + cleaned_name
    return cleaned_name


def username_to_table_name(user_id, username):
    # 去除非法字符
    cleaned_name = re.sub(r'[^\w\s]', '', username)
    cleaned_user_id = user_id.replace('-', '_')
    # 将空格替换为下划线
    cleaned_name = cleaned_name.replace(' ', '_')
    # 确保表名以字母开头
    if cleaned_name[0].isdigit():
        cleaned_name = '_' + cleaned_name
    # 确保表名长度不超过 MySQL 表名长度限制
    max_length = 64 - len(cleaned_user_id) - 1  # 减去 user_id 的长度和一个连接字符
    if len(cleaned_name) > max_length:
        cleaned_name = cleaned_name[:max_length]
    # 将 cleaned_user_id 添加到表名中以确保唯一性
    table_name = f"{cleaned_name}_{cleaned_user_id}"
    return table_name


def paths_to_table_names(file_list):
    """
    :param file_list: 
        e.g.: 'pages/github_cards_2.md, pages/github_cards_test.md'
    :return: 
        e.g. : (['pages/github_cards_2.md', 'pages/github_cards_test.md'], 
               ['github_cards_2', 'github_cards_test'])
    """
    if file_list is not None:
        sync_file_paths = file_list.split(",")
        sync_table_names = []
        # remove empty string, and strip space
        for idx, file_path in enumerate(sync_file_paths):
            if file_path.strip() == "":
                sync_file_paths.remove(file_path)
            else:
                file_path = file_path.strip()
                sync_file_paths[idx] = file_path
                file_name = os.path.basename(file_path).split(".")[0]
                sync_table_names.append(filename_to_table_name(file_name))
    return sync_file_paths, sync_table_names


# 只允许简单的非迭代元素 （排除字符串）的嵌套列表
def is_nested_list(lst, exclude_type):
    if not isinstance(lst, list):
        return False

    for item in lst:
        if isinstance(item, list):
            if not is_nested_list(item, exclude_type):
                return False
        else:
            # 可迭代非列表元素，排除字符串
            if isinstance(item, Iterable) and not isinstance(item, exclude_type):
                return False

    return True


def match_file_path(file_path):
    # 确保字符串不包含特定的不合法字符：:*"?<>|\ 和 反斜杠 \，单引号 '，分号 ;，以及序列 --
    # 使用负向前瞻断言确保字符串中不包含 --
    pattern = r'^(?!.*--)'  # 确保字符串中不包含 --
    # 添加原有的排除规则
    pattern += r'[^:*"?<>|\\\'\;]+$'
    if re.match(pattern, file_path):
        return True
    else:
        return False


def match_gitrepo_path(file_path):
    pattern = r'^(?!\/)[a-zA-Z0-9_\-./]+$'
    if re.match(pattern, file_path):
        return True
    else:
        return False
    

def validate_linux_file_path(file_path):
    # 检查文件路径是否为空
    if not file_path:
        raise VisiblePathException("文件路径不能为空")

    # 检查文件名是否合法
    if not match_file_path(file_path):
        raise VisiblePathException(
            "文件名包含不合法字符：*?<>;:|\和 引号,以及序列 -- "
            )

    # 检查文件名是否以 .md 或 .txt 结尾
    if not (file_path.endswith('.md') or file_path.endswith('.txt')):
        raise VisiblePathException("文件名必须以 .md 或 .txt 结尾")
    return True


def validate_gitrepo_path(file_path):
    # 检查文件路径是否为空
    if not file_path:
        return

    # 检查文件名是否合法
    if not match_gitrepo_path(file_path):
        raise VisiblePathException(
            "github repo 格式错误！请检查后重试"
            )

    return True


if __name__ == "__main__":
    x, y =paths_to_table_names("/pages/github_cards_2.md, ")
    print(x,y)
    x, y = paths_to_table_names(" /pages/github_cards_2.md , /pages/github_cards_test.md ")
    print(x, y)
    x, y =paths_to_table_names("/pages/diary_test_2024-02-24.md, ")
    print(x,y)