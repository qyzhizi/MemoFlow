## linux 环境非docker部署
- 1、环境准备
    - 一个linux环境
    - 安装 redis

- 2、拉取代码
    ```
    git pull https://github.com/qyzhizi/MemoFlow.git
    ```
    安装依赖:
    ```
    pip install -r requirements.txt
    ```
    也可以使用国内镜像加速安装：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 3、启动
    ```
    cd memoflow/memoflow/cmd
    bash run.sh &
    ```

- 4、访问log笔记页面

    浏览器输入：http://x.x.x.x:9000/v1/diary-log/index.html

    本地访问：http://localhost:9000/v1/diary-log/index.html
    
    正式使用前，需要配置，参考：
    [MemoFlow Configuration](./docs/memoflow_configuration.md)