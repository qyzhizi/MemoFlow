from PIL import Image
import io
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


def validate_image(image_file):
    # 验证图片类型
    allowed_formats = ['JPEG', 'PNG']
    image = Image.open(image_file)
    if image.format not in allowed_formats:
        return "Invalid image format. Only JPEG and PNG are allowed."

    # 验证图片大小
    max_size = 5 * 1024 * 1024  # 5MB
    # 将文件指针移动到文件开头
    image_file.seek(0)
    if len(image_file.read()) > max_size:
        return "Image size exceeds the maximum limit of 5MB."

    # 裁剪图片为正方形
    width, height = image.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    cropped_image = image.crop((left, top, right, bottom))

    # 调整图片尺寸为100x100像素
    resized_image = cropped_image.resize((100, 100))

    # 清除元数据
    cleaned_image = Image.new(resized_image.mode, resized_image.size)
    cleaned_image.putdata(list(resized_image.getdata()))

    # 生成处理后的图片文件
    output = io.BytesIO()
    cleaned_image.save(output, format=image.format)
    output.seek(0)
    return output.read()