from __future__ import annotations

import uuid

from src.api.rag.retriever import retrieve_relevant_chunks


async def retrieve_knowledge(business_id: uuid.UUID, query: str) -> str:
    chunks = await retrieve_relevant_chunks(business_id, query, n_results=5)
    if not chunks:
        return ""
    return "\n\n".join(chunks)
