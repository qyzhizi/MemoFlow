## 使用docker-compose.yml 部署
- 1、先安装好docker

    如果是windows环境，可以安装docker桌面版

    如果是linux环境，安装更简单一点，可以使用 docker 一键安装脚本(使用阿里云的源)
    ```
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    ```
- 2、拉取代码，并修改配置文件`.env`

    ```
    git pull git@github.com:qyzhizi/memocard.git
    ```
    将`.env.template` 复制一份并命名为`.env`，添加以下内容

    其中github仓库的账号token，仓库名与文件名需要配置，坚果云也时类似，具体如何配置见下文的`远程文件配置`

    ```
    CELERY_BROKER_URL=redis://redis:6379
    CELERY_RESULT_BACKEND=redis://redis:6379

    # 发送到github仓库
    #github token, @todo 如何获取token
    GITHUB_TOKEN=xxxx
    GITHUB_REPO=github用户名/仓库名
    #仓库文件路径,相对仓库的根目录，例如：xxxx/demo.md
    GITHUB_FILE_PATH=xxxx/demo.md

    # 发送到坚果云
    # 坚果云账号，例如：你的坚果云邮箱
    JIANGUOYUN_COUNT=坚果云账号
    # 坚果云api token
    JIANGUOYUN_TOKEN=xxxx
    # 文件路径,从根目录/开始
    JIANGUOYUN_TO_PATH=/xxxx/demo.md

    # 发送github仓库任务标志位， 如果不需要发送，设置为0
    SEND_TO_JIANGUOYUN=1
    # 发送坚果云任务标志位， 如果不需要发送，设置为0
    SEND_TO_GITHUB=1
    ```

- 3、启动docker服务，在终端中输入(如果是windows，则在命令提示符中输入)：
    ```
    docker-compose up -d
    ```
    该命令会自动构建镜像、拉取redis镜像，然后启动笔记服务。
- 4、访问log笔记页面

    浏览器输入：http://x.x.x.x:9000/v1/diary-log/index.html

    本地访问：http://localhost:9000/v1/diary-log/index.html