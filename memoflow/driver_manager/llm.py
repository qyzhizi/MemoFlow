from memoflow.core import dependency
from memoflow.core import manager
from memoflow.conf import CONF

from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
)


@dependency.provider('llm_api')
class LLMAPIManager(manager.Manager):
    driver_namespace = "memoflow.driver.driver_manager"

    def __init__(self):
        super(LLMAPIManager,
              self).__init__(driver_name=CONF.driver_manager.LLM_API_DRIVER)

    def get_embedding(self, text):
        return self.driver.get_embedding(text)

    def get_embedding_function(self):
        return self.driver.get_embedding_function()
    