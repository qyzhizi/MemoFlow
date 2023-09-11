from memoflow.api.azure_openai_api import LangAzureOpenAIEmbedding

class AzureAPIDriver(object):
    def __init__(self) -> None:
        self.azure_openai_embedding = None
    
    def get_embedding(self, text):
        if self.azure_openai_embedding is None:
            self.azure_openai_embedding = LangAzureOpenAIEmbedding()
        return self.azure_openai_embedding.get_embedding(text)
    
    def get_embedding_function(self):
        if self.azure_openai_embedding is None:
            self.azure_openai_embedding = LangAzureOpenAIEmbedding()
        return self.azure_openai_embedding.embedding