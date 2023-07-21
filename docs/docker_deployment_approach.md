## 使用docker-compose.yml 部署
- 1、先安装好docker

    如果是windows环境，可以安装docker桌面版

    如果是linux环境，安装更简单一点，可以使用 docker 一键安装脚本(使用阿里云的源)
    ```
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    ```
- 2、拉取代码
    ```
    git pull https://github.com/qyzhizi/MemoFlow.git
    ```
    安装依赖:
    ```
    pip install -r requirements.txt
    ```
    也可以使用国内镜像加速安装：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

- 3、启动docker服务，在终端中进入工程根目录（存在配置文件`docker-compose.yml`） ， 然后输入：
    ```
    docker-compose up -d
    ```
    如果是windows，则在命令提示符中输入上面的命令。
    该命令会自动构建镜像、拉取redis镜像，然后启动笔记服务。

- 4、访问log笔记页面

    浏览器输入：http://x.x.x.x:9000/v1/diary-log/index.html

    本地访问：http://localhost:9000/v1/diary-log/index.html
    
    正式使用前，需要配置，参考：
    [MemoFlow Configuration](./memoflow_configuration.md)