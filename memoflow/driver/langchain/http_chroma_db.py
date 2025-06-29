__import__('pysqlite3')
import sys
import time
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from chromadb import PersistentClient
from chromadb import HttpClient
from chromadb.config import Settings
import logging
from langchain.vectorstores import Chroma
import uuid

from memoflow.conf import CONF
# from memoflow.api.azure_openai_api import AzureOpenAIEmbedding
from memoflow.api.openai_api import OpenAIEmbedding

LOG = logging.getLogger(__name__)
DEFAULT_K = 4  # Number of Documents to return.

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
# azure_openai_embedding = AzureOpenAIEmbedding()
openai_embedding = OpenAIEmbedding()

class ChromeDBCollectionHttpDriver(object):
    # TODO  need pass collection name and host name
    def __init__(self) -> None:
        self.persist_directory = PERSIST_DIRECTORY
        self._embedding_function = openai_embedding

        # self.vector_db = Chroma(
        #         collection_name=COLLECTION_NAME,
        #         persist_directory=self.persist_directory,
        #         embedding_function=self.embedding_function)

        self._client = HttpClient(host="chroma",
                                           port=8000,
                                           settings=Settings(
                                               allow_reset=True,
                                               anonymized_telemetry=False,
                                               is_persistent=True))

        MAX_RETRY = 3  # 设置最大重试次数
        retry_count = 0  # 初始化重试计数器
        # if chroma db init readly, http_client will connect it
        collection_status = False
        while retry_count < MAX_RETRY:
            try:
                self._collection = self._client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    embedding_function=self._embedding_function.get_embeddings)
                collection_status = True
                break  # 成功获取或创建集合后退出循环
            except Exception as e:
                retry_count += 1
                if retry_count >= MAX_RETRY:
                    LOG.exception("Failed to get or create collection after maximum retries.")
                    raise e
                    # break
                else:
                    # 延迟等待一段时间后再重试
                    time.sleep(1)  # 休眠2秒后再重试（可以根据需要调整等待时间）

    # def get_vector_db(self):
    #     return self.vector_db

    # def persist(self):
    #     self.vector_db.persist()
        

    def delete_collection(self) -> None:
        """Delete the collection."""
        self._client.delete_collection(self._collection.name)    

    def delete_items_by_ids(self, ids: List[str]):
        if not ids:
            return 
        self._collection.delete(ids=ids)

    def get(self, ids=None, where=None, 
            where_document=None, include=None,
            limit=None):
        return self._collection.get(
            ids=ids, where=where, where_document=where_document,
            limit=limit, include=include)
    
    def collection_count(self) -> int:
        return self._collection.count()

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.

        Args:
            texts (Iterable[str]): Texts to add to the vectorstore.
            metadatas (Optional[List[dict]], optional): Optional list of metadatas.
            ids (Optional[List[str]], optional): Optional list of IDs.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        if not texts:
            return
        if ids is None:
            ids = [str(uuid.uuid1()) for _ in texts]
        embeddings = None
        texts = list(texts)
        if self._embedding_function is not None:
            LOG.info(f"call get_embeddings,length: {len(texts)}")
            embeddings = self._embedding_function.get_embeddings(texts)
        if metadatas:
            # fill metadatas with empty dicts if somebody
            # did not specify metadata for all texts
            length_diff = len(texts) - len(metadatas)
            if length_diff:
                metadatas = metadatas + [{}] * length_diff
            empty_ids = []
            non_empty_ids = []
            for idx, m in enumerate(metadatas):
                if m:
                    non_empty_ids.append(idx)
                else:
                    empty_ids.append(idx)
            if non_empty_ids:
                metadatas = [metadatas[idx] for idx in non_empty_ids]
                texts_with_metadatas = [texts[idx] for idx in non_empty_ids]
                embeddings_with_metadatas = (
                    [embeddings[idx] for idx in non_empty_ids] if embeddings else None
                )
                ids_with_metadata = [ids[idx] for idx in non_empty_ids]
                self._collection.upsert(
                    metadatas=metadatas,
                    embeddings=embeddings_with_metadatas,
                    documents=texts_with_metadatas,
                    ids=ids_with_metadata,
                )
                LOG.info("success upsert embeddings")
            if empty_ids:
                texts_without_metadatas = [texts[j] for j in empty_ids]
                embeddings_without_metadatas = (
                    [embeddings[j] for j in empty_ids] if embeddings else None
                )
                ids_without_metadatas = [ids[j] for j in empty_ids]
                self._collection.upsert(
                    embeddings=embeddings_without_metadatas,
                    documents=texts_without_metadatas,
                    ids=ids_without_metadatas,
                )
                LOG.info("success upsert embeddings")
        else:
            self._collection.upsert(
                embeddings=embeddings,
                documents=texts,
                ids=ids,
            )
            LOG.info("success upsert embeddings")
        return ids

    def update_texts(
        self,
        ids: List[str],
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
        ) -> List[str]:
        """

        Args:
            texts (Iterable[str]): Texts to add to the vectorstore.
            metadatas (Optional[List[dict]], optional): Optional list of metadatas.
            ids (Optional[List[str]], optional): Optional list of IDs.

        Returns:
            List[str]: List of IDs of the updated texts.
        """
        if not texts:
            return
        if ids is None:
            raise ValueError("ids must be specified for update_texts")
        if len(ids) != len(texts):
            raise ValueError("ids and texts must have the same length")
        if len(texts) < len(metadatas):
            raise ValueError("texts length must greater than metadatas length")
        embeddings = None
        texts = list(texts)
        if self._embedding_function is not None:
            embeddings = self._embedding_function.get_embeddings(texts)
        if metadatas:
            # fill metadatas with empty dicts if somebody
            # did not specify metadata for all texts
            length_diff = len(texts) - len(metadatas)
            metadatas = metadatas + [{}] * length_diff
            empty_ids = []
            non_empty_ids = []
            for idx, m in enumerate(metadatas):
                if m:
                    non_empty_ids.append(idx)
                else:
                    empty_ids.append(idx)
            if non_empty_ids:
                ids_with_metadata = [ids[idx] for idx in non_empty_ids]
                metadatas = [metadatas[idx] for idx in non_empty_ids]
                texts_with_metadatas = [texts[idx] for idx in non_empty_ids]
                embeddings_with_metadatas = (
                    [embeddings[idx] for idx in non_empty_ids] if embeddings else None
                )
                self._collection.update(
                    ids=ids_with_metadata,
                    embeddings=embeddings_with_metadatas,
                    metadatas=metadatas,
                    documents=texts_with_metadatas,
                )
            if empty_ids:
                ids_without_metadatas = [ids[j] for j in empty_ids]
                embeddings_without_metadatas = (
                    [embeddings[j] for j in empty_ids] if embeddings else None
                )
                texts_without_metadatas = [texts[j] for j in empty_ids]

                self._collection.update(
                    ids=ids_without_metadatas,
                    embeddings=embeddings_without_metadatas,
                    documents=texts_without_metadatas,
                )
        else:
            self._collection.update(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
            )
        return ids

    def __query_collection(
        self,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[List[List[float]]] = None,
        n_results: int = 4,
        where: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List:
        """Query the chroma collection."""
        # try:
        #     import chromadb  # noqa: F401
        # except ImportError:
        #     raise ValueError(
        #         "Could not import chromadb python package. "
        #         "Please install it with `pip install chromadb`."
        #     )
        return self._collection.query(
            query_texts=query_texts,
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            **kwargs,
        )
    
    # def _results_to_docs(self, results: Any) -> List:
    #     return self._process_results(results)


    def _process_results(self, results: Any) -> List[Tuple[dict, float]]:
        return [
            # TODO: Chroma can do batch querying,
            # we shouldn't hard code to the 1st result
            {"document": result[0],
              "metadata": result[1] or {},
              "distance": result[2],
              "id": result[3],
             }
            # for i in len(results["distances"])
            for result in zip(
                results["documents"],
                results["metadatas"],
                results["distances"],
                results["ids"],
            )

        ]    

    def similarity_search(
        self,
        query: str,
        k: int = DEFAULT_K,
        filter: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Tuple[dict, float]]:
        """Run similarity search with Chroma with distance.

        Args:
            query (str): Query text to search for.
            k (int): Number of results to return. Defaults to 4.
            filter (Optional[Dict[str, str]]): Filter by metadata. Defaults to None.

        Returns:
            List[Tuple[dict, float]]: List of documents most similar to
            the query text and cosine distance in float for each.
            Lower score represents more similarity.
        """
        if self._embedding_function is None:
            results = self.__query_collection(
                query_texts=[query], n_results=k, where=filter
            )
        else:
            query_embedding = self._embedding_function.get_embedding(query)
            results = self.__query_collection(
                query_embeddings=[query_embedding], n_results=k, where=filter
            )

        return self._process_results(results)[0]

    def get_similarity_search_docs(
        self,
        query: str,
        k: int = DEFAULT_K,
        filter: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Run similarity search with Chroma.

        Args:
            query (str): Query text to search for.
            k (int): Number of results to return. Defaults to 4.
            filter (Optional[Dict[str, str]]): Filter by metadata. Defaults to None.

        """
        results = self.similarity_search(query, k, filter=filter)
        # return [doc for doc, _ in docs_and_scores][0]['page_content']
        return results["document"]
    
    def rm_coll_all_itmes(self):
        all_ids = self.get(ids=None, limit=None, include=[])
        # if ids is not empty, then delete
        if all_ids["ids"]:
            return self.delete_items_by_ids(all_ids["ids"])
