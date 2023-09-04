import logging
import re
import requests
import traceback
import time

from memoflow.api import db_page_payload

LOG = logging.getLogger(__name__)

TITLE_NUM = 70

def create_database_page(notion_api_key, database_id, content=None):
    if content is None or database_id is None or notion_api_key is None :
        return None

    url = "https://api.notion.com/v1/pages"
    headers = {
    "Notion-Version": "2022-06-28",
    "Authorization": f"Bearer {notion_api_key}",
    "Content-Type": "application/json",
    }

    # 正则匹配，以一个#开头空格结尾的字符串，找到标签
    pattern = r"(?<!#)#\w+(?<!#)\s"
    matches = re.findall(pattern, content)
    
    # 这一要注意除了空格，还有'\n'要去除
    tags = [match.strip('#\n').replace(' ', '') for match in matches]
    LOG.info(tags)

    # 可以根据不同的tag 选择不同的标签颜色 : "red" "gray" "yellow"
    # 不用传颜色参数，会随机选择一个颜色
    # tag_color = 'green'
    txt_content = content
    title_content = content[:TITLE_NUM].replace('\r', '').replace('\n', ' ')

    payload = db_page_payload.get_payload(database_id, title_content, txt_content, tags)
    LOG.info(f"title_content: {title_content}")
    LOG.info(f"txt_content: {txt_content}")
    LOG.info(f"payload: {payload}")
    # pprint(payload)
    try:
        """
        如果要实现异步http 请求，需要参考下面的代码，同时要修改调用方的代码
        不过太慢了，所以这里只是记录一下，就不真的写完了
        async def main():
            async with aiohttp.ClientSession() as session:
                async with session.get('http://www.example.com') as response:
                    await response.text()
        """
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload)
        end_time = time.time()
        LOG.info(f'create_database_page took {(end_time - start_time):.5f} seconds to run.')
        # LOG.info(f"notion response: {response.text}")
        
        # 可以查看返回来的错误
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            LOG.info(f"err response: {response.text}")
            LOG.info(f'{err}')
        
    except Exception as e:
        LOG.error(f"requests create_database_page error: {e}")
        LOG.info(f'{traceback.format_exc()}')