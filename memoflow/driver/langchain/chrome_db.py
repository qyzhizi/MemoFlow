__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from chromadb import PersistentClient
import logging
from langchain.vectorstores import Chroma

from memoflow.conf import CONF
from memoflow.api.azure_openai_api import LangAzureOpenAIEmbedding

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
PERSIST_DIRECTORY = CONF.diary_log['CHROMA_PERSIST_DIRECTORY']
azure_openai_embedding = LangAzureOpenAIEmbedding()

class ChromeDBDriver(object):
    def __init__(self) -> None:
        self.persist_directory = PERSIST_DIRECTORY 
        self.azure_openai_embedding = azure_openai_embedding
        self.embedding_function = self.azure_openai_embedding.embedding

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
    
    def delete_items_by_ids(self, ids: List[str]):
            self.vector_db.delete(ids=ids)

    def add_texts(self,
                  texts: Iterable[str],
                  metadatas: Optional[List[dict]]=None,
                  ids: Optional[List[str]]=None,
                  **kwargs: Any):
        return self.vector_db.add_texts(texts, metadatas, ids, **kwargs)
        