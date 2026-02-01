from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import Response

from src.api.db.engine import get_session
from src.api.db.queries import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_for_business,
)
from src.api.dependencies import get_current_business_id
from src.api_schema.schemas import DocumentCreate, DocumentResponse

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/businesses/{business_id}/knowledge-base", tags=["knowledge-base"])


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    business_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> list[DocumentResponse]:
    docs = await get_documents_for_business(session, business_id)
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    business_id: uuid.UUID,
    body: DocumentCreate,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
) -> DocumentResponse:
    doc = await create_document(
        session,
        business_id=business_id,
        title=body.title,
        content=body.content,
    )
    # TODO: trigger RAG ingest asynchronously
    return DocumentResponse.model_validate(doc)


@router.delete("/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def remove_document(
    doc_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    _current_business: uuid.UUID = Depends(get_current_business_id),
):
    doc = await get_document_by_id(session, doc_id)
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    await delete_document(session, doc)
