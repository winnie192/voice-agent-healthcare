from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

from src.api.config import settings

if TYPE_CHECKING:
    import chromadb


def get_chroma_client() -> chromadb.HttpClient:
    import chromadb

    return chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)


def collection_name_for_business(business_id: uuid.UUID) -> str:
    return f"biz_{str(business_id).replace('-', '_')}"


async def ingest_document(
    business_id: uuid.UUID,
    document_id: uuid.UUID,
    content: str,
    title: str,
) -> str:
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(content)

    embeddings_model = OpenAIEmbeddings(api_key=settings.openai_api_key)
    embeddings = await embeddings_model.aembed_documents(chunks)

    client = get_chroma_client()
    col_name = collection_name_for_business(business_id)
    collection = client.get_or_create_collection(name=col_name)

    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": str(document_id), "title": title, "chunk_index": i} for i in range(len(chunks))]

    collection.add(ids=ids, embeddings=embeddings, documents=chunks, metadatas=metadatas)
    return col_name


def delete_document_vectors(business_id: uuid.UUID, document_id: uuid.UUID) -> None:
    client = get_chroma_client()
    col_name = collection_name_for_business(business_id)
    try:
        collection = client.get_collection(name=col_name)
        existing = collection.get(where={"document_id": str(document_id)})
        if existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass
