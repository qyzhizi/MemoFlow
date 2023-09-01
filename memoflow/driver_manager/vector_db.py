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
class VectorDBCollectionManager(manager.Manager):
    driver_namespace = "memoflow.driver.driver_manager"

    def __init__(self):
        super(VectorDBCollectionManager,
              self).__init__(CONF.driver_manager.VECTOR_DB_COLLECTIION_DRIVER)

    def add_texts(self,
                  texts: Iterable[str],
                  metadatas: Optional[List[dict]]=None,
                  ids: Optional[List[str]]=None,
                  **kwargs: Any):
        self.driver.add_texts(texts, metadatas, ids, **kwargs)
        # self.driver.vector_db.persist()

    def search_texts(self,
                     query: str,
                     top_k: int,
                     **kwargs: Any):
        return self.driver.similarity_search(query, top_k, **kwargs)

    def delete_collection(self):
        self.driver.delete_collection()

    # def peek_collection(self, limit: int = 10):
    #     return self.driver.peek_collection(limit)

    def get_collection_items(self, ids, limit: int = 10,
                             include=["embeddings", "metadatas", "documents"]):
        return self.driver.get(ids=ids, limit=limit, include=include)

    def get_vector_db_coll_all_ids(self, include=[]):
        return self.driver.get(ids=None, limit=None, include=include)
    
    def get_collection_size(self):
        return self.driver.collection_count()

    def delete_items_by_ids(self, ids: List[str]):
        return self.driver.delete_items_by_ids(ids)

    def get_items_by_ids(self, ids: List[str],
                         include=["metadatas", "documents", "embeddings"]):
        # return self.driver.vector_db.get(ids=ids, include=include)
        return self.driver.get(ids=ids, include=include)



class CeleryVectorDBCollManager(VectorDBCollectionManager):
    # TODO pass collection name
    def __init__(self):
        super(VectorDBCollectionManager,
              self).__init__(CONF.driver_manager.VECTOR_DB_COLLECTIION_DRIVER)
