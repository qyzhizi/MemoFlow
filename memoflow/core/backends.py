from memoflow.app import test_demo
from memoflow.app import diary_log 
from memoflow.app import diary_log_second
from memoflow.app import predict_image
from memoflow.client_app import diary_log as diary_log_client
from memoflow.app import diary_log_second
from memoflow.driver_manager import asyn_task
from memoflow.driver_manager import vector_db
from memoflow.driver_manager import llm

def load_backends():
    DRIVERS = {}
    if DRIVERS.get('test_demo_provider_api', None) is None:
        DRIVERS['test_demo_provider_api'] = test_demo.provider.Manager()
    if DRIVERS.get('diary_log_provider_api', None) is None:
        DRIVERS['diary_log_provider_api'] = diary_log.provider.Manager()
    if DRIVERS.get('diary_db_api', None) is None:
        DRIVERS['diary_db_api'] = diary_log.provider.DiaryDBManager()
    if DRIVERS.get('llm_api', None) is None:
        DRIVERS['llm_api'] = llm.LLMAPIManager()
    if DRIVERS.get('vector_db_api', None) is None:
        DRIVERS['vector_db_api'] = vector_db.VectorDBManager()
    if DRIVERS.get('diary_log_client_api', None) is None:
        DRIVERS['diary_log_client_api'] = diary_log_client.provider.Manager()
    if DRIVERS.get('diary_log_second_provider_api', None) is None:
        DRIVERS['diary_log_second_provider_api'] = diary_log_second.provider.Manager()
    if DRIVERS.get('asyn_task_api', None) is None:
        DRIVERS['asyn_task_api'] = asyn_task.AsynTaskManager()
    if DRIVERS.get('predict_image_api', None) is None:
        DRIVERS['predict_image_api'] = predict_image.provider.Manager()


    return DRIVERS
