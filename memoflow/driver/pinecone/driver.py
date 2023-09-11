import logging
import pinecone
import time
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
import uuid

from memoflow.conf import CONF
from memoflow.api.azure_openai_api import AzureOpenAIEmbedding

PINECONE_INDEX_NAME = CONF.api_conf["PINECONE_INDEX_NAME"]
PINECONE_ENVIRONMENT = CONF.api_conf['PINECONE_ENVIRONMENT']
PINECONE_API_KEY = CONF.api_conf['PINECONE_API_KEY']
# 可以由open api 获得, 目前这里写死了
PINECONE_VECTOR_DIM = CONF.api_conf["PINECONE_VECTOR_DIM"]

PINECONE_COSINE = 'cosine'
PINECONE_TEXT = 'text'
DEFAULT_K = 4  # Number of Documents to return.

LOG = logging.getLogger(__name__)

class PineconeIndexHttpDriver(object):
    def __init__(self) -> None:
        pinecone.init(
            api_key=PINECONE_API_KEY,
            environment=PINECONE_ENVIRONMENT  # find next to API key in console
        )

        # only create index if it doesn't exist
        if PINECONE_INDEX_NAME not in pinecone.list_indexes():
            if len(pinecone.list_indexes()) > 0:
                LOG.warn("pinecone ready have indexes: %s " % pinecone.list_indexes())
                if PINECONE_ENVIRONMENT == "gcp-starter":
                    LOG.info("delete old index : %s " % pinecone.list_indexes()[0])
                    pinecone.delete_index(name=pinecone.list_indexes()[0])

            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=int(PINECONE_VECTOR_DIM),
                metric=PINECONE_COSINE
            )
            # wait a moment for the index to be fully initialized
            time.sleep(1)

        # now connect to the index
        self.index = pinecone.GRPCIndex(PINECONE_INDEX_NAME)
        self.embedding = AzureOpenAIEmbedding()
    
    def add_texts(self,
                  texts: Iterable[str],
                  metadatas: Optional[List[dict]] = None,
                  ids: Optional[List[str]] = None,
                  **kwargs: Any) -> List[str]:
        """Run more texts through the embeddings and add to the vectorstore.

        Args:
            texts (Iterable[str]): Texts to add to the vectorstore.
            metadatas (Optional[List[dict]], optional): Optional list of metadatas.
            ids (Optional[List[str]], optional): Optional list of IDs.

        Returns:
            List[str]: List of IDs of the added texts.
        """
        if ids is None:
            ids = [str(uuid.uuid1()) for _ in texts]
        embeddings = None      
        texts = list(texts)
        if self.embedding is not None:
            embeddings = self.embedding.get_embeddings(texts)
        else:
            LOG.info("self.embedding is None")
            raise
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
                    [embeddings[idx] for idx in non_empty_ids]
                )
                ids_with_metadata = [ids[idx] for idx in non_empty_ids]
                datas = []
                for item in zip(ids_with_metadata, embeddings_with_metadatas, texts_with_metadatas, metadatas):
                    pinecone_metadatas = {PINECONE_TEXT: item[2]}
                    pinecone_metadatas.update(item[3])
                    datas.append((item[0], item[1], pinecone_metadatas))
                # todo 按没批量100 发生, 不要一次性发送
                self.index.upsert(datas)
            if empty_ids:
                texts_without_metadatas = [texts[j] for j in empty_ids]
                embeddings_without_metadatas = (
                    [embeddings[j] for j in empty_ids]
                )
                ids_without_metadatas = [ids[j] for j in empty_ids]
                datas = []
                for item in zip(ids_without_metadatas, embeddings_without_metadatas, texts_without_metadatas):
                    datas.append(
                        (item[0], item[1], {PINECONE_TEXT: item[2]})
                    )
                self.index.upsert(datas)
        else:
            datas = []
            for item in zip(ids, embeddings, texts):
                datas.append(
                    (item[0], item[1], {PINECONE_TEXT: item[2]})
                )
            self.index.upsert(datas)

    def similarity_search(
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
        if self.embedding is not None:
            embeddings = self.embedding.get_embeddings([query])
        else:
            LOG.info("self.embedding is None")
            raise 
        if kwargs.get("include_metadata", None) is not None:
            include_metadata = kwargs['include_metadata']
        else:
            include_metadata = True    
        query_result = self.index.query(
            vector=embeddings[0],
            filter=filter,
            top_k=k,
            include_metadata=include_metadata
        )
        query_result_matches = query_result.get("matches", None)
        if query_result_matches is not None:
            doc_result = [item.get("metadata").get(PINECONE_TEXT, None) for item in query_result_matches]
            return doc_result
        return []
    
    def rm_coll_all_itmes(self):
        if PINECONE_INDEX_NAME in pinecone.list_indexes():
            # todo 是否可以不删除整个index, 而是删除其中的所有向量
            pinecone.delete_index(name=PINECONE_INDEX_NAME)
            pinecone.create_index(
                name=PINECONE_INDEX_NAME,
                dimension=int(PINECONE_VECTOR_DIM),
                metric=PINECONE_COSINE
            )
            # wait a moment for the index to be fully initialized
            time.sleep(1)


