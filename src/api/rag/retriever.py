from __future__ import annotations

import uuid

from langchain_openai import OpenAIEmbeddings

from src.api.config import settings
from src.api.rag.ingest import collection_name_for_business, get_chroma_client


async def retrieve_relevant_chunks(
    business_id: uuid.UUID,
    query: str,
    n_results: int = 5,
) -> list[str]:
    embeddings_model = OpenAIEmbeddings(api_key=settings.openai_api_key)
    query_embedding = await embeddings_model.aembed_query(query)

    client = get_chroma_client()
    col_name = collection_name_for_business(business_id)

    try:
        collection = client.get_collection(name=col_name)
    except Exception:
        return []

    results = collection.query(query_embeddings=[query_embedding], n_results=n_results)
    documents = results.get("documents", [[]])
    return documents[0] if documents else []
