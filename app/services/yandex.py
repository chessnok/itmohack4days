from __future__ import annotations

from typing import List

from langchain.embeddings.base import Embeddings

from yandex_cloud_ml_sdk import YCloudML

from app.core.config import settings

sdk: YCloudML = YCloudML(
    folder_id=settings.FOLDER,
    auth=settings.LLM_API_KEY,
)
model = (
    sdk.models.completions("yandexgpt")
)


class YaGPTEmbeddings(Embeddings):

    def __init__(self):
        self.query_model = sdk.models.text_embeddings("query")
        self.doc_model = sdk.models.text_embeddings("doc")

    def embed_documents(self, texts):
        return [self.doc_model.run(text) for text in texts]

    def embed_document(self, text):
        return self.doc_model.run(text)

    def embed_query(self, text: str) -> List[float]:
        return self.query_model.run(text)


embeddings = YaGPTEmbeddings()
