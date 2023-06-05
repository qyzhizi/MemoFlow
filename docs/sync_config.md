为了实现远程文件同步，这里采用了两种方式:github仓库文件同步与坚果云文件同步。

- 1、github仓库文件同步
    
    配置如下
    ```
    # 发送到github仓库
    #github token, @todo 如何获取token
    GITHUB_TOKEN=xxxx
    GITHUB_REPO=github用户名/仓库名
    #仓库文件路径,相对仓库的根目录，例如：xxxx/demo.md
    GITHUB_FILE_PATH=xxxx/demo.md
    ```
    (1)github token如何获取呢？
    首先要开启GitHub API

    要使用 GitHub API，你需要先创建一个 Personal access token。Personal access token 是一个安全令牌，可以用来访问 GitHub API。以下是创建 Personal access token 的步骤：

    - 登录到你的 GitHub 帐户。

    - 点击右上角的头像，选择 Settings。

    - 在左侧导航栏中选择 Developer settings。

    - 点击 Personal access tokens。

    - 点击 Tokens(classic) , 然后点击Generate new token (New personal access token)。

    - 在 "Note" 字段中输入一个描述性的名称，以便于记忆和识别。

    - 在 "Select scopes" 中选择需要使用的权限。根据你使用 GitHub API 的具体情况，可以选择不同的权限，例如 repo、user、admin:org 等。如果不确定需要什么权限，可以先选择默认的权限。

    - 点击 Generate token。

    - 将生成的 Personal access token 复制到剪贴板中，并保存到安全的地方。

    (2) GITHUB_REPO 是github用户名/仓库名， 例如：`qyzhizi/logseqnote`

    (3) GITHUB_FILE_PATH 是待同步的文件名路径，例如：`pages/github_cards_2.md`,`pages` 是仓库根目录下一个文件夹

- 2、坚果云文件同步

    配置为：

    ```
    # 发送到坚果云
    # 坚果云账号，例如：你的坚果云邮箱
    JIANGUOYUN_COUNT=坚果云账号
    # 坚果云api token
    JIANGUOYUN_TOKEN=xxxx
    # 文件路径,从根目录/开始
    JIANGUOYUN_TO_PATH=/xxxx/demo.md
    ```
    **(1) 获取坚果云api token**

    坚果云提供了API，可以通过 API 访问坚果云的文件和文件夹。要使用坚果云 API，需要进行以下步骤：

    - 登录到坚果云官网。

    - 点击右上角的头像，选择账号信息，点击安全选项

    - 点击「点击添加应用」按钮，填写应用名称，然后点击「生成密码」。

    - 在页面中，可以看到应用密码(token)。

    **(2) 设置待同步的文件路径**

    JIANGUOYUN_TO_PATH=/xxxx/demo.md