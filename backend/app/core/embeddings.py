
from typing import List

import requests

from app.config import settings
from langchain_core.embeddings import Embeddings


class OpenRouterEmbeddings(Embeddings):
    """
    LangChain-compatible embeddings implementation backed by OpenRouter's
    unified embeddings API.
    """

    def __init__(self, model: str | None = None):
        if not settings.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is not set")
        self.model = model or settings.OPENROUTER_EMBEDDING_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        self.api_key = settings.OPENROUTER_API_KEY

    def _embed(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        response = requests.post(
            f"{self.base_url}/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": texts,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return [item["embedding"] for item in data["data"]]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> List[float]:
        vectors = self._embed([text])
        return vectors[0]


def get_embedding(text: str) -> List[float]:
    """Helper used by other modules to get a single-text embedding."""
    return OpenRouterEmbeddings().embed_query(text)
