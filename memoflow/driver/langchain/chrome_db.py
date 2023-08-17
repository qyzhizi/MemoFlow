__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from chromadb import PersistentClient
import logging
from langchain.vectorstores import Chroma

from memoflow.conf import CONF
from memoflow.api.azure_openai_api import AzureOpenAIEmbedding

LOG = logging.getLogger(__name__)

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
COLLECTION_NAME = CONF.diary_log["COLLECTION_NAME"]
LOG.info("COLLECTION_NAME: %s" % COLLECTION_NAME)
PERSIST_DIRECTORY = CONF.diary_log['CHROMA_PERSIST_DIRECTORY']
LOG.info("PERSIST_DIRECTORY: %s" % PERSIST_DIRECTORY)
azure_openai_embedding = AzureOpenAIEmbedding()

class ChromeDBDriver(object):
    def __init__(self) -> None:
        # self.collection = None
        self.persist_directory = PERSIST_DIRECTORY 
        self.azure_openai_embedding = azure_openai_embedding
        self.embedding_function = self.azure_openai_embedding.embedding
        
        self.client = PersistentClient(path=self.persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME, embedding_function=self.embedding_function)

        self.vector_db = Chroma(
                collection_name=COLLECTION_NAME,
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function)
    
    def get_vector_db(self):
        return self.vector_db
    
    def persist(self):
        self.vector_db.persist()
    
    def delete_collection(self):
        self.vector_db.delete_collection()
    
    def get_collection(self):
        return self.collection
    
    def peek_collection(self, limit: int=10):
        return self.collection.peek(limit=limit)
    
    def get_collection_size(self):
        return self.collection.count()
    
    def delete_items_by_ids(self, ids: List[str]):
        self.collection.delete(ids=ids)
    
    # def reset_collection(self):
    #     client = chromadb.PersistentClient(path=self.persist_directory)
    #     client.reset()
    #     self.collection = None
    #     self.vector_db = None
        