"""Re-ingest existing KB documents into ChromaDB.

Usage:
    python3 -m scripts.ingest_kb
"""
from __future__ import annotations

import asyncio

from src.api.db.engine import async_session_factory
from src.api.db.models import KnowledgeBaseDocument
from src.api.rag.ingest import ingest_document
from sqlalchemy import select


async def main() -> None:
    async with async_session_factory() as session:
        result = await session.execute(select(KnowledgeBaseDocument))
        docs = result.scalars().all()
        if not docs:
            print("No KB documents found in database.")
            return
        for doc in docs:
            col = await ingest_document(doc.business_id, doc.id, doc.content, doc.title)
            print(f"Ingested: {doc.title} -> {col}")
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
