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


class LangAzureOpenAIEmbedding(object):
    def __init__(self,
                 azure_openai_endpoint=CONF.api_conf['AZURE_OPENAI_ENDPOINT'], azure_openai_key=CONF.api_conf['AZURE_OPENAI_KEY']):
        if azure_openai_endpoint is None:
            raise Exception("azure_openai_endpoint is None")
        if azure_openai_key is None:
            raise Exception("azure_openai_key is None")
        self.embedding = OpenAIEmbeddings(
            openai_api_base = azure_openai_endpoint,
            openai_api_key = azure_openai_key,
            openai_api_type = "azure",
            chunk_size=16,
            deployment="text-embedding-ada-002",
            model="text-embedding-ada-002")

    def get_embedding(self, text):
        return self.embedding.embed_query(text)

    # def get_embeddings(self, texts):
    #     return self.embedding.get_embeddings(texts)

    # def get_similarity(self, text1, text2):
    #     return self.embedding.get_similarity(text1, text2)


class AzureOpenAIEmbedding(object):
    def __init__(self,
                 azure_openai_endpoint=CONF.api_conf['AZURE_OPENAI_ENDPOINT'],
                 azure_openai_key=CONF.api_conf['AZURE_OPENAI_KEY']):

        if azure_openai_endpoint is None:
            raise Exception("azure_openai_endpoint is None")
        if azure_openai_key is None:
            raise Exception("azure_openai_key is None")

        openai.api_type = "azure"
        openai.api_key = azure_openai_key
        openai.api_base = azure_openai_endpoint
        openai.api_version = "2022-12-01"
        # engine  Defaults to "text-embedding-ada-002".
        # engine should be set to the deployment name you chose when you deployed
        # the text-embedding-ada-002 (Version 2) model
        self.engine = "text-embedding-ada-002"
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

    @retry(wait=wait_random_exponential(min=1, max=20),
           stop=stop_after_attempt(6))
    def get_embeddings(self, list_of_text: List[str]) -> List[List[float]]:
        assert len(list_of_text
                   ) <= 2048, "The batch size should not be larger than 2048."

        # replace newlines, which can negatively affect performance.
        list_of_text = [text.replace("\n", " ") for text in list_of_text]
        data: List[List[float]] = []

        _iter = range(0, len(list_of_text), self._chunk_size)
        for i in _iter:
            response = openai.Embedding.create(input=list_of_text[i:i+self._chunk_size], engine=self.engine)
            data.extend(sorted(response.data, key=lambda x: x["index"]))
            # data.extend(response.data)

        return [d["embedding"] for d in data]
