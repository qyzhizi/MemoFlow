# Use the Python 3.10 image as the base image
FROM python:3.10


# RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
#     && apt-get update --fix-missing \
#     && apt-get install -y build-essential --fix-missing \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y build-essential git

# 将工作目录设置为 /app
WORKDIR /app

# Copy all files in the current directory to /app
COPY . /app

# 安装脚本所需要的依赖包
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
# RUN pip install --no-cache-dir -r requirements.txt

# If you want to use Tencent Cloud mirroring, use the following command
# RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

# delete pip cache file
# RUN rm -rf $(pip cache dir)/*

# Expose the port of the container
EXPOSE 9000

RUN python setup.py sdist

# 给 run.sh 文件添加可执行权限
RUN chmod +x memoflow/cmd/run.sh

# 运行脚本
CMD ["bash", "-c", "memoflow/cmd/run.sh"]
