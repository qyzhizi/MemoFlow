# log卡片笔记服务
向logseq所在的远程同步文件(github 或者坚果云)发送笔记，实现一个轻量化的卡片笔记记录页面。
启动服务后，访问：`http://localhost/:9000/v1/diary-log/index.html`
，可得到页面：

<img src="https://qyzhizi.cn/img/202305160912106.png" width="60%" height="60%">

未来也可以扩展出跟多的页面，提供给多人使用, 例如：
```
本地访问：http://localhost/:9000/v1/diary-log/index.html
本地访问：http://localhost/:9000/v1/diary-log-second/index.html
```

数据会在数据库sqlite中保留一份，然后通过异步方式向远程同步文件发送一份（插入到文件最上面），由于采用异步发送方式，所以感受不到延迟。如果后台异步发送任务失败，那么远程同步文件得不到更新。未来考虑后台发送任务失败时，给出页面提示。

相比logseq,打开速度更快，自动添加时间戳标题，使用一个简单的自定义规则实现卡片笔记。如果未来有更好且容易使用的规则就更好了。

当你输入：
```
#key1 #key2
#que 如何使用一个简单的自定义规则实现卡片笔记
#ans
就像这样, 这是一个例子
--todo 代办事项1
--todo 代办事项2
```
在本地页面的内容：
```
- ## 2023/5/16 08:36:48:
	- #key1 #key2
#que 如何使用一个简单的自定义规则实现卡片笔记
	- #ans
就像这样, 这是一个例子
	- TODO 代办事项1
	- TODO 代办事项2
```
在远程同步文件中内容：
```
- ## 2023/5/16 08:36:48:
	- #key1 #key2
	  #que 如何使用一个简单的自定义规则实现卡片笔记
	- #ans
	  就像这样, 这是一个例子
	- TODO 代办事项1
	- TODO 代办事项2      
```
自定义规则解释：
```
#key1 表示关键字标签 
#que 表示问题标签
#ans 表示答案标签
关键字标签与问题部分在一个子块，子块是logseq中的概念，表示一个段落
答案部分单独作为一个子块
--todo 表示代办事项
另外代办事项（- TODO xxxx）也是一个单独子块
本地页面的内容 与 远程同步文件中内容之所以不一样，是考虑到方便复制与粘贴本地页面的内容，因为远程同步文件中内容中子块会统一带"\t"的缩进，复制后，有时候还要去除"\t",不太方便。
```
最终markdown 渲染效果是：

<img src="https://qyzhizi.cn/img/202305160910034.png" width="60%" height="60%">


## 使用docker-compose.yml 部署
- 1、先安装好docker

    如果是windows环境，可以安装docker桌面版

    如果是linux环境，安装更简单一点，可以使用 docker 一键安装脚本(使用阿里云的源)
    ```
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    ```
- 2、拉取代码，并修改配置文件`.env`
    ```
    git pull git@github.com:qyzhizi/web_dl.git
    ```
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
- 4、访问log笔记页面

    浏览器输入：http://x.x.x.x:9000/v1/diary-log/index.html

    本地访问：http://localhost/:9000/v1/diary-log/index.html

## linux 环境启动
- 1、环境准备
    - 一个linux环境
    - 安装依赖:
    pip install -r requirements.txt
    - 安装 redis: 
    安装方法, @todo

- 2、拉取代码，并修改配置文件`.env`
    ```
    git pull git@github.com:qyzhizi/web_dl.git
    与docker-compose.yml部署相比，这里只有CELERY_BROKER_URL 与CELERY_RESULT_BACKEND 的配置改变了。
    ```
    ```
    CELERY_BROKER_URL=redis://localhost:6379
    CELERY_RESULT_BACKEND=redis://localhost:6379

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
- 3、启动
    ```
    cd web_dl/web_dl/cmd
    python3 main.py &
    ```

- 4、访问log笔记页面

    浏览器输入：http://x.x.x.x:9000/v1/diary-log/index.html

    本地访问：http://localhost/:9000/v1/diary-log/index.html
