from web_dl.app import test_demo
from web_dl.app import diary_log 
from web_dl.app import diary_log_second

def load_backends():

    DRIVERS = dict(
        test_demo_provider_api=test_demo.provider.Manager(),
        diary_log_provider_api=diary_log.provider.Manager(),
        diary_log_second_provider_api = diary_log_second.provider.Manager()
        )

    return DRIVERS

