from oslo_config import cfg
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

CHROMA_VECTOR_DB = bool(int(env_vars.get("CHROMA_VECTOR_DB", None)))
PINECONE_VECTOR_DB = bool(int(env_vars.get("PINECONE_VECTOR_DB", None)))
PINECONE_API_KEY = env_vars.get("PINECONE_API_KEY", None)

# 声明配置项
CONF_OPTS = []


ASYN_TASK_DRIVER = cfg.StrOpt(
    'ASYN_TASK_DRIVER',
    default='asyn_task_driver',
    help='The driver to use for manager : AsynTaskManager',
)

LLM_API_DRIVER = cfg.StrOpt(
    'LLM_API_DRIVER',
    default='llm_driver',
    help='The driver to use for manager : LLMAPIManager',
)

# online pinecone db service
if PINECONE_VECTOR_DB and PINECONE_API_KEY:
    vector_db_collectiion_driver = "pinecone_index_db_driver"
# chroma db
elif CHROMA_VECTOR_DB:
    vector_db_collectiion_driver = "langchain_chrome_db_collection_driver"

VECTOR_DB_COLLECTIION_DRIVER = cfg.StrOpt(
    'VECTOR_DB_COLLECTIION_DRIVER',
    default=vector_db_collectiion_driver,
    help='The driver to use for manager : VectorDBCollectionManager',
)

CONF_OPTS.extend([ASYN_TASK_DRIVER,
                 LLM_API_DRIVER,
                 VECTOR_DB_COLLECTIION_DRIVER])
GROUP_NAME = "driver_manager"
ALL_OPTS = CONF_OPTS


def register_opts(conf):
    conf.register_opts(CONF_OPTS, group=GROUP_NAME)


def list_opts():
    return {GROUP_NAME: ALL_OPTS}
