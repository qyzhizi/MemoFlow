from github import Github


class GitHupApi(object):
    def __init__(self, token, repo) -> None:

        # 创建一个 GitHub 对象，并使用您的 Access Token 进行身份验证
        self.g = Github(token)
        # 获取要上传文件的仓库
        self.repo = self.g.get_repo(repo)

    def update_file(self, file_path, added_content, commit_message, branch_name):
        # 获取要更新的文件
        file = self.repo.get_contents(file_path)

        # 获取base64解码的内容，不能直接获得源字符串吗？非要解码，有点浪费？
        existing_content = file.decoded_content.decode()
        # print(existing_content)
       
        # 使用"\n"作为分隔，防止added_content不带"\n"
        updated_content = added_content + " \n" + existing_content
        # 提交文件更新
        self.repo.update_file(file_path, commit_message, updated_content,
                              file.sha, branch_name)
