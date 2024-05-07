# docker-compose 服务部署
## 使用预构建镜像运行服务
所需的镜像从DockHub自动会拉取到本地，无需本地构建镜像。
- 1、先安装好docker环境

    如果是windows环境，可以安装docker桌面版

    如果是linux环境，安装更简单一点，可以使用 docker 一键安装脚本(使用阿里云的源)
    ```
    curl -fsSL https://get.docker.com | bash -s docker --mirror Aliyun
    ```
- 2、 创建一个目录, 然后创建 docker-compose.yml 文件，内容如下：
    ```
    version: "3.9"

    services:
    main_server:
        depends_on:
        - redis
        - chroma
        image: qyzhizi/memoflow:v0.1.6
        env_file:
        - ../.env
        ports:
        - "6060:6060"
        volumes:
        - "../.env:/app/.env"
        - "../log_file:/app/log_file"
        - "../db_data:/app/db_data"
        networks:
        - net    
        restart: on-failure
        command:  sh -c "python setup.py egg_info && sh memoflow/cmd/run.sh"

    redis:
        image: "redis/redis-stack-server:latest"
        networks:
        - net 
        restart: on-failure

    chroma:
        image: ghcr.io/chroma-core/chroma:latest
        volumes:
        - index_data:/chroma/chroma
        command: "--workers 1 --host 0.0.0.0 --port 8000 --proxy-headers --log-config chromadb/log_config.yml --timeout-keep-alive 30"

        environment:
        - IS_PERSISTENT=TRUE
        - ANONYMIZED_TELEMETRY=False
        - ALLOW_RESET=True
        - REBUILD_HNSWLIB=False
        networks:
        - net
        restart: on-failure

    volumes:
    index_data:
        driver: local

    networks:
    net:
        driver: bridge

    ```   
    其中 `image: qyzhizi/memoflow:v0.1.6` 是已经上传 DockHub 的镜像。

- 3、在与 docker-compose.yml 同级目录下，创建配置文件：`.env`。
    如果不配置只有空白页面，配置参考：
    [MemoFlow Configuration](./memoflow_configuration.md)
- 4、启动服务
    ```
    docker-compose up -d
    ```
    第一次运行会拉取 qyzhizi/memoflow:v0.1.6 镜像，也会拉取 redis, chroma 镜像。然后启动服务。  
- 5、访问客户端页面

    浏览器输入：http://x.x.x.x:6060/v1/diary-log

    本地访问：http://localhost:6060/v1/diary-log    

## 本地构建镜像，运行服务
需要下载源代码，构建镜像，然后使用 docker-compose 启动服务。
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
    如果不配置只有空白页面，配置参考：
    [MemoFlow Configuration](./memoflow_configuration.md)

- 3、在终端中进入工程根目录（存在配置文件`docker-compose.yml`） ，启动docker服务，输入：
    ```
    docker-compose up -d
    ```
    如果是windows，则在命令提示符中输入上面的命令。
    该命令会自动构建镜像、拉取redis镜像，然后启动笔记服务。

- 5、访问客户端页面

    浏览器输入：http://x.x.x.x:6060/v1/diary-log

    本地访问：http://localhost:6060/v1/diary-log
    
