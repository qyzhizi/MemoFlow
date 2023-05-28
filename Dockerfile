# Use the Python 3.10 image as the base image
FROM python:3.10


# RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
#     && apt-get update --fix-missing \
#     && apt-get install -y build-essential --fix-missing \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*

# Set the working directory to /app
WORKDIR /app

# Copy all files in the current directory to /app
COPY . /app

# Dependencies required by the installation script
RUN pip install --no-cache-dir -r requirements.txt

# If you want to use Tencent Cloud mirroring, use the following command
# RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

# delete pip cache file
# RUN rm -rf $(pip cache dir)/*

# Expose the port of the container
EXPOSE 9000

# Add executable permissions to the run.sh file
RUN chmod +x web_dl/cmd/run.sh

# run script
CMD ["bash", "-c", "web_dl/cmd/run.sh"]
