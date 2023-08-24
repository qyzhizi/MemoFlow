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

@dependency.provider('vector_db_api')
class VectorDBManager(manager.Manager):
    driver_namespace = "memoflow.driver.driver_manager"

    def __init__(self):
        super(VectorDBManager, self).__init__(CONF.driver_manager.VECTOR_DB_DRIVER)

    def add_texts(self,
                  texts: Iterable[str],
                  metadatas: Optional[List[dict]]=None,
                  ids: Optional[List[str]]=None,
                  **kwargs: Any):
        self.driver.vector_db.add_texts(texts, metadatas, ids, **kwargs)
        self.driver.vector_db.persist()

    def search_texts(self,
                     query: str,
                     top_k: int,
                     **kwargs: Any):
        return self.driver.vector_db.similarity_search(query, top_k, **kwargs)

    def delete_collection(self):
        self.driver.delete_collection()

    def peek_collection(self, limit: int = 10):
        return self.driver.peek_collection(limit)

    def get_collection_items(self, limit: int = 10,
                             include=["embeddings", "metadatas", "documents"]):
        return self.driver.vector_db.get(limit=limit, include=include)

    def get_collection_ids(self, include=[]):
        return self.driver.vector_db.get(include=include)

    def get_collection_size(self):
        return self.driver.get_collection_size()

    def delete_items_by_ids(self, ids: List[str]):
        return self.driver.delete_items_by_ids(ids)
    
    def get_vector_db(self):
        return self.driver.get_vector_db()

    def get_items_by_ids(self, ids: List[str]):
        return self.driver.vector_db.get(ids=ids)
    


class CeleryVectorDBManager(VectorDBManager):
    def __init__(self):
        super(VectorDBManager,
              self).__init__(CONF.driver_manager.VECTOR_DB_DRIVER)
