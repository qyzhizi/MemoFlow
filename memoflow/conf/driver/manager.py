from oslo_config import cfg

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
    help='The driver to use for manager : AsynTaskManager',
)

VECTOR_DB_DRIVER = cfg.StrOpt(
    'VECTOR_DB_DRIVER',
    default='langchain_chrome_db_driver',
    help='The driver to use for manager : AsynTaskManager',
)

CONF_OPTS.extend([ASYN_TASK_DRIVER,
                 LLM_API_DRIVER,
                 VECTOR_DB_DRIVER])
GROUP_NAME = "driver_manager"
ALL_OPTS = CONF_OPTS


def register_opts(conf):
    conf.register_opts(CONF_OPTS, group=GROUP_NAME)


def list_opts():
    return {GROUP_NAME: ALL_OPTS}
