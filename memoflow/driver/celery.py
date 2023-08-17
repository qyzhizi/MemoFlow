from memoflow.tasks import celery_task

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

class CeleryDriver(object):
    def __init__(self) -> None:
        pass

    def asyn_add_texts_to_vector_db(self, texts: List[str],
                                    metadatas: Optional[List[dict]]=None,
                                    ids: Optional[List[str]] = None):
        celery_task.add_texts_to_vector_db.delay(texts, metadatas, ids)