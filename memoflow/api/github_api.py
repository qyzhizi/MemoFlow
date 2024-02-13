import logging

from github import Github
from github.GithubException import UnknownObjectException

LOG = logging.getLogger(__name__)


class GitHupApi(object):
    def __init__(self, token, repo) -> None:

        # 创建一个 GitHub 对象，并使用您的 Access Token 进行身份验证
        self.g = Github(token)
        # 获取要上传文件的仓库
        self.repo = self.g.get_repo(repo)

    def update_file(self, file_path, commit_message, branch_name,
                    added_content=None, updated_content=None):
        # 获取要更新的文件
        try:
            file = self.repo.get_contents(file_path)
        # 判断异常类型，如果是未找到文件，则创建文件
        except UnknownObjectException as e:
            LOG.warning(f"Exception: {e}")
            LOG.info(f"File {file_path} not found, create it.")
            self.repo.create_file(file_path,
                                  commit_message, added_content, branch_name)
            return
        if added_content and not updated_content:
            # 获取base64解码的内容，不能直接获得源字符串吗？非要解码，有点浪费？
            existing_content = file.decoded_content.decode()
            # 添加行首 “- ” 与 logseq 保持一致
            if not existing_content.startswith("- "):
                existing_content = "- " + existing_content
            # 使用"\n"作为分隔，防止added_content不带"\n", 中间只需要写"\n"就行
            # 不能加入空格比如：" \n", 因为这会导致logseq去除该空格，引起不必要的修改
            # added_content[2:] 去除行首 “- ” 与 logseq 保持一致
            updated_content = added_content[2:] + "\n" + existing_content
        if not added_content and updated_content:
            # added_content[2:] 去除行首 “- ” 与 logseq 保持一致
            if updated_content.startswith("- "):
                updated_content = updated_content[2:]
        # 提交文件更新
        self.repo.update_file(file_path, commit_message, updated_content,
                              file.sha, branch_name)

    def get_contents(self, sync_file_path_list, branch_name):
        contents = []
        for file_path in sync_file_path_list:
            # pull file from github
            try:
                files = self.repo.get_contents(file_path, ref=branch_name)
            except UnknownObjectException as e:
                LOG.warning(f"Exception: {e}")
                LOG.info(f"File {file_path} not found, skip it.")
                continue
            if isinstance(files, list):
                for file in files:
                    contents.append(file.decoded_content.decode())
            else:
                contents.append(files.decoded_content.decode())

        return contents
