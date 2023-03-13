from web_dl.app import test_demo
from web_dl.app import diary_log 
from web_dl.app import diary_log_lrx

def load_backends():

    DRIVERS = dict(
        test_demo_provider_api=test_demo.provider.Manager(),
        diary_log_provider_api=diary_log.provider.Manager(),
        diary_log_lrx_provider_api = diary_log_lrx.provider.Manager()
        )

    return DRIVERS

