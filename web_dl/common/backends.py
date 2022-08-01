from web_dl.app import test_demo 


def load_backends():

    DRIVERS = dict(
        test_demo_provider_api=test_demo.provider.Manager())

    return DRIVERS

