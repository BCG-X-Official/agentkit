# -*- coding: utf-8 -*-
# mypy: disable-error-code="call-arg"
# TODO: Change langchain param names to match the new langchain version

import logging
from typing import List, Optional, Union

from langchain.embeddings import CacheBackedEmbeddings
from langchain_openai.embeddings import OpenAIEmbeddings

from app.api.deps import get_redis_store
from app.core.config import settings

logger = logging.getLogger(__name__)


class CacheBackedEmbeddingsExtended(CacheBackedEmbeddings):
    def embed_query(self, text: str) -> List[float]:
        """
        Embed query text.

        Extended to support caching

        Args:
            text: The text to embed.

        Returns:
            The embedding for the given text.
        """
        vectors: List[Union[List[float], None]] = self.document_embedding_store.mget([text])
        text_embeddings = vectors[0]

        if text_embeddings is None:
            text_embeddings = self.underlying_embeddings.embed_query(text)
            self.document_embedding_store.mset(list(zip([text], [text_embeddings])))

        return text_embeddings


def get_embedding_model(emb_model: Optional[str]) -> CacheBackedEmbeddings:
    """
    Get the embedding model from the embedding model type.

    If "OPENAI_API_BASE" is set, it will load Azure GPT models, otherwise it will load
    OpenAI GPT models.
    """
    if emb_model is None:
        emb_model = "text-embedding-ada-002"

    underlying_embeddings = None
    match emb_model:
        case "text-embedding-ada-002":
            if settings.OPENAI_API_BASE is not None:
                underlying_embeddings = OpenAIEmbeddings(
                    deployment="text-embedding-ada-002-2",
                    model="text-embedding-ada-002",
                    openai_api_base=settings.OPENAI_API_BASE,
                    openai_api_type="azure",
                    openai_api_key=settings.OPENAI_API_KEY,
                    chunk_size=1,  # Maximum number of texts to embed in each batch
                )
            else:
                underlying_embeddings = OpenAIEmbeddings()
        case _:
            logger.warning(f"embedding model {emb_model} not found, using default emb_model")
            underlying_embeddings = OpenAIEmbeddings()

    store = get_redis_store()
    embedder = CacheBackedEmbeddingsExtended.from_bytes_store(
        underlying_embeddings, store, namespace=underlying_embeddings.model
    )
    return embedder
