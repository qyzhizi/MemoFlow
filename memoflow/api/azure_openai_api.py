import os
from memoflow.conf import CONF
from langchain.embeddings.openai import OpenAIEmbeddings


class AzureOpenAIEmbedding(object):
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
