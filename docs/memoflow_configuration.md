# 配置
为了实现远程文件同步，这里采用了两种方式: github仓库文件同步与坚果云文件同步。

## `.env` 配置文件
将`.env.template` 修改 `.env` ， 然后按需要进行修改。

`.env` 内容：
```
# 非docker部署, celery 使用redis
#CELERY_BROKER_URL=redis://localhost:6379
#CELERY_RESULT_BACKEND=redis://localhost:6379

# docker部署, celery 使用redis
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379

# github token
GITHUB_TOKEN=xxxx
# github用户名/仓库名
GITHUB_REPO=xxxx/xxxx
# commit 对应的仓库文件路径,相对仓库的根目录，例如：xxxx/demo.md
GITHUB_CURRENT_SYNC_FILE_PATH=xxxx/demo.md
# pull 对应的仓库文件路径，可配置多个文件，文件之间用逗号分隔
GITHUB_SYNC_FILE_LIST=xxxx/demo.md, xxxx/demo2.md


# 坚果云账号，例如：你的坚果云邮箱
JIANGUOYUN_COUNT=xxxx
# 坚果云api token
JIANGUOYUN_TOKEN=xxxx
# 文件路径,从根目录/开始
JIANGUOYUN_TO_PATH=/xxxx/demo.md

# 发送github仓库任务标志位， 如果不需要发送，设置为0
SEND_TO_JIANGUOYUN=1
# 发送坚果云任务标志位， 如果不需要发送，设置为0
SEND_TO_GITHUB=1


# 以下是可选配置项
# 同步文档数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
SYNC_DATA_BASE_PATH=db_data/memoflow_sync_data.db
SYNC_TABLE_NAME=sync_data
REVIEW_TABLE_NAME=review_diary_log
# 粘贴板数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
DATA_BASE_CLIPBOARD_PATH=db_data/clipboard_data.db
CLIPBOARD_TABLE_NAME=clipboard_log
```

注意 `非docker部署` 与 `docker部署` 是不一样的，需要注释掉不需要的

## github 配置
    
github 配置配置如下
```
# github token
GITHUB_TOKEN=xxxx
# github用户名/仓库名
GITHUB_REPO=xxxx/xxxx
# commit 对应的仓库文件路径,相对仓库的根目录，例如：xxxx/demo.md
GITHUB_CURRENT_SYNC_FILE_PATH=xxxx/demo.md
# pull 对应的仓库文件路径，可配置多个文件，文件之间用逗号分隔
GITHUB_SYNC_FILE_LIST=xxxx/demo.md, xxxx/demo2.md
```
(1) GITHUB_TOKEN 是 GitHub API 的一个安全令牌。以下是创建步骤：

- 登录到你的 GitHub 帐户。

- 点击右上角的头像，选择 Settings。

- 在左侧导航栏中选择 Developer settings。

- 点击 Personal access tokens。

- 点击 Tokens(classic) , 然后点击Generate new token (New personal access token)。

- 在 "Note" 字段中输入一个描述性的名称，以便于记忆和识别。

- 在 "Select scopes" 中选择需要使用的权限。根据你使用 GitHub API 的具体情况，可以选择不同的权限，例如 repo、user、admin:org 等。如果不确定需要什么权限，可以先选择默认的权限。

- 点击 Generate token。

- 将生成的 Personal access token 复制到剪贴板中，并保存到安全的地方。

(2) GITHUB_REPO : 是github用户名/仓库名， 例如：`qyzhizi/logseqnote`

(3) GITHUB_CURRENT_SYNC_FILE_PATH: 是存在 githhub 仓库的文件，例如：`pages/demo.md`。 `pages` 是仓库根目录下一个文件夹。它对应 `commit` 操作，将卡片笔记保存到该文件。

(4) GITHUB_SYNC_FILE_LIST : 是 `pull` 操作对应的文件列表，使用用逗号进行分隔，`pull` 操作 可以将文件从github 仓库拉取到后台数据库，然后再客户端页面显示。 

## 坚果云配置

配置为：
```
# 坚果云账号，例如：你的坚果云邮箱
JIANGUOYUN_COUNT=xxxx
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
```
JIANGUOYUN_TO_PATH=/xxxx/demo.md
```

## 数据库配置（可选）
```
# 以下是可选配置项
# 同步文档数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
SYNC_DATA_BASE_PATH=db_data/memoflow_sync_data.db
SYNC_TABLE_NAME=sync_data
REVIEW_TABLE_NAME=review_diary_log
# 粘贴板数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
DATA_BASE_CLIPBOARD_PATH=db_data/clipboard_data.db
CLIPBOARD_TABLE_NAME=clipboard_log
```

- SYNC_DATA_BASE_PATH : 同步数据库，也是一个文件
- SYNC_TABLE_NAME ： 同步数据库中的数据表，`commit` 提交的卡片笔记也会再该表保存一份。`pull` 操作 也会将数据保存到该表
- REVIEW_TABLE_NAME ： 同步数据库中的数据表， 保存 review 页面的数据表
- DATA_BASE_CLIPBOARD_PATH ： clipboard（粘贴板）页面所在的数据库
- CLIPBOARD_TABLE_NAME ： 同理，保存 clipboard（粘贴板）页面的数据表
