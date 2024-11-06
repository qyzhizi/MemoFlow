import os
import openai
from memoflow.conf import CONF
from langchain.embeddings.openai import OpenAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_random_exponential
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

from memoflow.utils.async_manager.task_manager import TaskManager


class LangAzureOpenAIEmbedding(object):
    def __init__(self,
                 azure_openai_endpoint=CONF.api_conf['AZURE_OPENAI_ENDPOINT'], 
                 azure_openai_key=CONF.api_conf['AZURE_OPENAI_KEY'],
                 azure_api_version=CONF.api_conf['AZURE_API_VERSION'],
                 azure_api_deployment=CONF.api_conf['AZURE_API_DEPLOYMENT'],
                 azure_api_model=CONF.api_conf['AZURE_API_MODEL']
                 ):
        if azure_openai_endpoint is None:
            raise Exception("azure_openai_endpoint is None")
        if azure_openai_key is None:
            raise Exception("azure_openai_key is None")
        self.embedding = OpenAIEmbeddings(
            openai_api_base = azure_openai_endpoint,
            openai_api_key = azure_openai_key,
            openai_api_type = "azure",
            chunk_size=16,
            deployment=azure_api_deployment,
            model=azure_api_model,
            openai_api_version=azure_api_version)

    def get_embedding(self, text):
        return self.embedding.embed_query(text)

    # def get_embeddings(self, texts):
    #     return self.embedding.get_embeddings(texts)

    # def get_similarity(self, text1, text2):
    #     return self.embedding.get_similarity(text1, text2)


class AzureOpenAIEmbedding(object):
    def __init__(self,
                 azure_openai_endpoint=CONF.api_conf['AZURE_OPENAI_ENDPOINT'],
                 azure_openai_key=CONF.api_conf['AZURE_OPENAI_KEY'],
                 azure_api_version=CONF.api_conf['AZURE_API_VERSION'],
                 azure_api_model=CONF.api_conf['AZURE_API_MODEL']
                 ):

        if azure_openai_endpoint is None:
            raise Exception("azure_openai_endpoint is None")
        if azure_openai_key is None:
            raise Exception("azure_openai_key is None")

        openai.api_type = "azure"
        openai.api_key = azure_openai_key
        openai.api_base = azure_openai_endpoint
        openai.api_version = azure_api_version
        # engine  Defaults to "text-embedding-ada-002".
        # engine should be set to the deployment name you chose when you deployed
        # the text-embedding-ada-002 (Version 2) model
        self.engine = azure_api_model
        self._chunk_size = 16

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    def get_embedding(self, text: str) -> List[float]:
        """_summary_

        Args:
            text (str):

        Returns:
            List[float]: 
        """

        # replace newlines, which can negatively affect performance.
        text = text.replace("\n", " ")

        return openai.Embedding.create(
            input=[text], engine=self.engine)["data"][0]["embedding"]

    def get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        # use async to save time
        if len(list_of_text) > self._chunk_size:
            return self.get_embeddings_use_async_loop(
                list_of_text=list_of_text)

        # replace newlines, which can negatively affect performance.
        list_of_text = [text.replace("\n", " ") for text in list_of_text]
        data: List[List[float]] = []

        _iter = range(0, len(list_of_text), self._chunk_size)
        for i in _iter:
            chunk_embeddings = self.get_chunk_embeddings(chunk_text=list_of_text[i:i+self._chunk_size])
            data.extend(chunk_embeddings)
        return [d["embedding"] for d in data]

    @retry(wait=wait_random_exponential(min=1, max=20),
           stop=stop_after_attempt(6))
    def get_chunk_embeddings(self, chunk_text: List[str]) -> List[List[float]]:
        response = openai.Embedding.create(input=chunk_text, engine=self.engine)
        return sorted(response.data, key=lambda x: x["index"])
    
    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
    async def aget_chunk_embeddings(self, chunk_text: List[str]) -> List[List[float]]:
        response = await openai.Embedding.acreate(input=chunk_text, engine=self.engine)
        return sorted(response['data'], key=lambda x: x["index"])

    def get_embeddings_use_async_loop(self, list_of_text: List[str]) -> List[List[float]]:
        # replace newlines, which can negatively affect performance.
        list_of_text = [text.replace("\n", " ") for text in list_of_text]
        data: List[List[float]] = []

        _iter = range(0, len(list_of_text), self._chunk_size)
        # Create a list of tasks for concurrent execution
        tasks = [
            self.aget_chunk_embeddings(chunk_text=list_of_text[i:i + self._chunk_size])
            for i in _iter
        ]
        # Gather results from all tasks concurrently
        manager = TaskManager()
        results = manager.run_multiple_tasks(tasks)
        # close event loop
        manager.close()
        # Flatten the list of results
        for chunk_embeddings in results:
            data.extend(chunk_embeddings)

        return [d["embedding"] for d in data]
