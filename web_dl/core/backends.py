from web_dl.app import test_demo
from web_dl.app import diary_log 
from web_dl.app import diary_log_lrx
from web_dl.app import predict_image

def load_backends():

    DRIVERS = dict(
        test_demo_provider_api=test_demo.provider.Manager(),
        diary_log_provider_api=diary_log.provider.Manager(),
        diary_log_second_provider_api = diary_log_lrx.provider.Manager(),
        predict_image_api = predict_image.provider.Manager()
        )

    return DRIVERS

