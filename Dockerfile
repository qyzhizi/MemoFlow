# 使用 Python 3.10 镜像作为基础镜像
FROM python:3.9-slim

# RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
#     && apt-get update \
#     && apt-get install -y  git --fix-missing

RUN apt-get update \
    && apt-get install -y git --fix-missing

# 将工作目录设置为 /app
WORKDIR /app

# Copy all files in the current directory to /app
COPY . /app


RUN pip install --no-cache-dir -r requirements.txt
# If you want to use Tencent Cloud mirroring, use the following command
# RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

# delete pip cache file
# RUN rm -rf $(pip cache dir)/*

# Expose the port of the container
EXPOSE 9000

# 给 run.sh 文件添加可执行权限
RUN chmod +x memoflow/cmd/run.sh

# 运行脚本
CMD ["bash", "-c", "memoflow/cmd/run.sh"]
