# 使用 Python 3.10 镜像作为基础镜像
FROM python:3.10-slim-bookworm 

# RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
#     && apt-get update --fix-missing && apt-get install -y --fix-missing \
#     build-essential \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

RUN apt-get update --fix-missing && apt-get install -y --fix-missing \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 将工作目录设置为 /app
WORKDIR /app

# Copy all files in the current directory to /app
COPY . /app


# RUN pip install --no-cache-dir -r requirements.txt
# If you want to use Tencent Cloud mirroring, use the following command
RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple \
    && rm -rf $(pip cache dir)/* \
    && python setup.py egg_info

# delete pip cache file
# RUN rm -rf $(pip cache dir)/*

# Expose the port of the container
EXPOSE 6060

# 给 run.sh 文件添加可执行权限
RUN chmod +x memoflow/cmd/run.sh

# 运行脚本
CMD ["bash", "-c", "memoflow/cmd/run.sh"]
