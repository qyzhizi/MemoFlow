from memoflow.conf import CONF
from memoflow.utils import common

GITHUB_OTHER_SYNC_FILE_LIST = CONF.diary_log['GITHUB_OTHER_SYNC_FILE_LIST'] or ""
GITHUB_FILE_LIST = CONF.diary_log['GITHUB_CURRENT_SYNC_FILE_PATH'] + ',' \
            + GITHUB_OTHER_SYNC_FILE_LIST

JIANGUOYUN__OTHER_SYNC_FILE_LIST = CONF.api_conf['JIANGUOYUN__OTHER_SYNC_FILE_LIST'] or ""            
JIANGUOYUN_FILE_LIST = CONF.api_conf['JIANGUOYUN_CURRENT_SYNC_FILE_PATH'] + ',' \
            + JIANGUOYUN__OTHER_SYNC_FILE_LIST 

class GithubTablePathMap():
    sync_file_paths, sync_table_names = common.paths_to_table_names(GITHUB_FILE_LIST)
    current_table_name = sync_table_names[0]
    current_table_path = sync_file_paths[0]
    other_table_path = sync_file_paths[1:]
    # other_table_name = sync_table_names[1:]
    table_path_map = dict(zip(sync_table_names, sync_file_paths))
    path_table_map = dict(zip(sync_file_paths, sync_table_names))
    other_table_path_map = dict(zip(sync_table_names[1:], sync_file_paths[1:]))

class JianguoyunTablePathMap():
    sync_file_paths, sync_table_names = common.paths_to_table_names(JIANGUOYUN_FILE_LIST)
    current_table_name = sync_table_names[0]
    current_table_path = sync_file_paths[0]
    table_path_map = dict(zip(sync_table_names, sync_file_paths))
    path_table_map = dict(zip(sync_file_paths, sync_table_names))
    other_table_path_map = dict(zip(sync_table_names[1:], sync_file_paths[1:]))
