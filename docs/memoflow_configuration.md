# 用户配置

  <div style="flex: 1; items-start:center">
    <img src="https://qyzhizi.cn/img/202405071937403.png" alt="client" width="auto" height="auto" />
    <div align="center">
      <p>同步文件配置</p>
    </div>
  </div>

Github 仓库配置|坚果云配置
:-------------------------:|:-------------------------:
![](https://qyzhizi.cn/img/202405071940580.png)  |  ![](https://qyzhizi.cn/img/202405071942295.png)

# 网站 Host 配置

## `.env` 配置文件
这里采用了两种同步方式: github仓库同步与坚果云同步。
将本仓库根目录中`.env.template` 复制，重命名为 `.env` ， 然后按需要进行修改。

`.env` 内容：
```
# 非docker部署, celery 使用redis
#CELERY_BROKER_URL=redis://localhost:6379
#CELERY_RESULT_BACKEND=redis://localhost:6379

# docker部署, celery 使用redis
CELERY_BROKER_URL=redis://redis:6379
CELERY_RESULT_BACKEND=redis://redis:6379


# 以下是可选配置项，默认不配置
# 同步文档数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
# SYNC_DATA_BASE_PATH=db_data/memoflow_sync_data.db
# 粘贴板数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
# DATA_BASE_CLIPBOARD_PATH=db_data/clipboard_data.db
# CLIPBOARD_TABLE_NAME=clipboard_log
```

注意 `非docker部署` 与 `docker部署` 是不一样的，需要注释掉不需要的



## 数据库配置解释（可选）
```
# 以下是可选配置项
# 同步文档数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
SYNC_DATA_BASE_PATH=db_data/memoflow_sync_data.db
# 粘贴板数据库相对路径，文件不存在会自动创建，以当前工作目录为根目录
DATA_BASE_CLIPBOARD_PATH=db_data/clipboard_data.db
CLIPBOARD_TABLE_NAME=clipboard_log
```

- SYNC_DATA_BASE_PATH : 同步数据库，也是一个文件
- DATA_BASE_CLIPBOARD_PATH ： clipboard（粘贴板）页面所在的数据库
- CLIPBOARD_TABLE_NAME ： 同理，保存 clipboard（粘贴板）页面的数据表
