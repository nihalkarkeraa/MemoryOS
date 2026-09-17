from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
import json

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException
)

from pydantic import BaseModel

from services.document_service import (
    extract_text_from_pdf
)

from services.ingestion_service import (
    ingestion_service
)

from services.document_hash_service import (
    document_hash_service
)

from services.document_registry_service import (
    document_registry_service
)

from services.chroma_service import (
    chroma_service
)

from services.rag_service import (
    rag_service
)

from services.hybrid_retrieval_service import (
    hybrid_retrieval_service
)

from services.summarization_service import (
    summarization_service
)

from services.comparison_service import (
    comparison_service
)


app = FastAPI(
    title="MemoryOS API"
)


UPLOAD_DIR = Path(
    "data/uploads"
)

DOCUMENT_DIR = Path(
    "data/documents"
)

EXTRACTED_DIR = Path(
    "data/extracted"
)


UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DOCUMENT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EXTRACTED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# REQUEST MODELS
# ==========================================================


class ChatRequest(BaseModel):

    question: str

    n_results: int = 5

    document_ids: list[str] | None = None


class SearchRequest(BaseModel):

    query: str

    n_results: int = 5

    document_ids: list[str] | None = None


class CompareRequest(BaseModel):

    question: str

    document_ids: list[str]

    n_results: int = 5


# ==========================================================
# HEALTH CHECK
# ==========================================================


@app.get("/health")
def health_check():

    return {
        "status": "ok"
    }


# ==========================================================
# DOCUMENT UPLOAD
# ==========================================================


@app.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF files are supported "
                "right now."
            )
        )

    temporary_id = str(
        uuid4()
    )

    temporary_filename = (
        f"{temporary_id}.pdf"
    )

    file_path = (
        UPLOAD_DIR
        / temporary_filename
    )

    try:

        file_content = await file.read()

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(
                file_content
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save uploaded file: "
                f"{str(error)}"
            )
        )

    try:

        file_hash = (
            document_hash_service.calculate_hash(
                str(file_path)
            )
        )

    except Exception as error:

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to calculate file hash: "
                f"{str(error)}"
            )
        )

    existing_document = (
        document_registry_service.find_by_hash(
            file_hash
        )
    )

    if existing_document:

        if file_path.exists():
            file_path.unlink()

        return {
            "status": "duplicate",
            "message": (
                "This document has already "
                "been uploaded."
            ),
            "document": existing_document
        }

    document_id = str(
        uuid4()
    )

    stored_filename = (
        f"{document_id}.pdf"
    )

    permanent_file_path = (
        UPLOAD_DIR
        / stored_filename
    )

    file_path.rename(
        permanent_file_path
    )

    try:

        ingestion_result = (
            ingestion_service.ingest_pdf(
                file_path=str(
                    permanent_file_path
                ),
                document_id=document_id
            )
        )

    except Exception as error:

        if permanent_file_path.exists():
            permanent_file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document ingestion failed: "
                f"{str(error)}"
            )
        )

    try:

        pages = extract_text_from_pdf(
            str(permanent_file_path)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to extract document text: "
                f"{str(error)}"
            )
        )

    metadata = {

        "document_id": document_id,

        "filename": file.filename,

        "stored_filename": stored_filename,

        "file_hash": file_hash,

        "file_type": "pdf",

        "upload_time": datetime.now(
            timezone.utc
        ).isoformat(),

        "total_pages": (
            ingestion_result[
                "total_pages"
            ]
        ),

        "total_chunks": (
            ingestion_result[
                "total_chunks"
            ]
        ),

        "embeddings_generated": (
            ingestion_result[
                "embeddings_generated"
            ]
        ),

        "chunks_stored": (
            ingestion_result[
                "chunks_stored"
            ]
        ),

        "status": "processed"
    }

    metadata_path = (
        DOCUMENT_DIR
        / f"{document_id}.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file_handle:

        json.dump(
            metadata,
            file_handle,
            indent=4,
            ensure_ascii=False
        )

    extracted_path = (
        EXTRACTED_DIR
        / f"{document_id}.json"
    )

    with open(
        extracted_path,
        "w",
        encoding="utf-8"
    ) as file_handle:

        json.dump(
            pages,
            file_handle,
            indent=4,
            ensure_ascii=False
        )

    try:

        document_registry_service.register_document(
            metadata
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Document was ingested but "
                "registration failed: "
                f"{str(error)}"
            )
        )

    return metadata


# ==========================================================
# LIST DOCUMENTS
# ==========================================================


@app.get("/documents")
def list_documents():

    documents = (
        document_registry_service.list_documents()
    )

    return {
        "total_documents": len(
            documents
        ),
        "documents": documents
    }


# ==========================================================
# GET SINGLE DOCUMENT
# ==========================================================


@app.get("/documents/{document_id}")
def get_document(
    document_id: str
):

    document = (
        document_registry_service.find_by_id(
            document_id
        )
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Document not found."
            )
        )

    stored_filename = document.get(
        "stored_filename",
        f"{document_id}.pdf"
    )

    pdf_path = (
        UPLOAD_DIR
        / stored_filename
    )

    extracted_path = (
        EXTRACTED_DIR
        / f"{document_id}.json"
    )

    chroma_chunk_count = (
        chroma_service.count_document_chunks(
            document_id
        )
    )

    return {
        "document": document,
        "storage": {
            "pdf_exists": pdf_path.exists(),
            "extracted_text_exists": (
                extracted_path.exists()
            ),
            "chroma_chunks": (
                chroma_chunk_count
            )
        }
    }


# ==========================================================
# DELETE DOCUMENT
# ==========================================================


@app.delete("/documents/{document_id}")
def delete_document(
    document_id: str
):

    # --------------------------------------------------
    # 1. Find document
    # --------------------------------------------------

    document = (
        document_registry_service.find_by_id(
            document_id
        )
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Document not found."
            )
        )

    # --------------------------------------------------
    # 2. Delete ChromaDB chunks
    # --------------------------------------------------

    deleted_chunks = (
        chroma_service.delete_document(
            document_id
        )
    )

    # --------------------------------------------------
    # 3. Delete PDF
    # --------------------------------------------------

    stored_filename = document.get(
        "stored_filename",
        f"{document_id}.pdf"
    )

    pdf_path = (
        UPLOAD_DIR
        / stored_filename
    )

    pdf_deleted = False

    if pdf_path.exists():

        pdf_path.unlink()

        pdf_deleted = True

    # --------------------------------------------------
    # 4. Delete extracted text
    # --------------------------------------------------

    extracted_path = (
        EXTRACTED_DIR
        / f"{document_id}.json"
    )

    extracted_deleted = False

    if extracted_path.exists():

        extracted_path.unlink()

        extracted_deleted = True

    # --------------------------------------------------
    # 5. Delete document metadata
    # --------------------------------------------------

    metadata_path = (
        DOCUMENT_DIR
        / f"{document_id}.json"
    )

    metadata_deleted = False

    if metadata_path.exists():

        metadata_path.unlink()

        metadata_deleted = True

    # --------------------------------------------------
    # 6. Delete registry entry
    # --------------------------------------------------

    deleted_document = (
        document_registry_service.delete_document(
            document_id
        )
    )

    # --------------------------------------------------
    # 7. Return deletion information
    # --------------------------------------------------

    return {
        "status": "deleted",
        "document_id": document_id,
        "filename": document[
            "filename"
        ],
        "deleted_chunks": deleted_chunks,
        "pdf_deleted": pdf_deleted,
        "extracted_text_deleted": (
            extracted_deleted
        ),
        "metadata_deleted": (
            metadata_deleted
        ),
        "registry_deleted": (
            deleted_document is not None
        )
    }


# ==========================================================
# DOCUMENT SEARCH
# ==========================================================


@app.post("/search")
def search_documents(
    request: SearchRequest
):

    # --------------------------------------------------
    # 1. Validate query
    # --------------------------------------------------

    if not isinstance(
        request.query,
        str
    ) or not request.query.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Search query cannot be empty."
            )
        )

    # --------------------------------------------------
    # 2. Validate number of results
    # --------------------------------------------------

    if request.n_results < 1:

        raise HTTPException(
            status_code=400,
            detail=(
                "n_results must be at least 1."
            )
        )

    # --------------------------------------------------
    # 3. Validate document IDs
    # --------------------------------------------------

    document_ids = request.document_ids

    if document_ids is not None:

        cleaned_document_ids = [
            document_id.strip()
            for document_id in document_ids
            if isinstance(
                document_id,
                str
            )
            and document_id.strip()
        ]

        if not cleaned_document_ids:

            raise HTTPException(
                status_code=400,
                detail=(
                    "document_ids cannot be empty."
                )
            )

        document_ids = list(
            dict.fromkeys(
                cleaned_document_ids
            )
        )

    # --------------------------------------------------
    # 4. Validate document existence
    # --------------------------------------------------

    if document_ids is not None:

        for document_id in document_ids:

            document = (
                document_registry_service.find_by_id(
                    document_id
                )
            )

            if document is None:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Document not found: "
                        f"{document_id}"
                    )
                )

    # --------------------------------------------------
    # 5. Run hybrid retrieval
    # --------------------------------------------------

    try:

        results = (
            hybrid_retrieval_service.search(
                query=request.query.strip(),
                n_results=request.n_results,
                document_ids=document_ids
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Search failed: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------
    # 6. Format search results
    # --------------------------------------------------

    formatted_results = []

    for result in results:

        metadata = result.get(
            "metadata",
            {}
        )

        document_id = metadata.get(
            "document_id"
        )

        filename = metadata.get(
            "filename"
        )

        if document_id and not filename:

            document = (
                document_registry_service.find_by_id(
                    document_id
                )
            )

            if document:

                filename = document.get(
                    "filename"
                )

        formatted_results.append(
            {
                "document_id": document_id,
                "filename": (
                    filename
                    or "Unknown document"
                ),
                "page_number": (
                    metadata.get(
                        "page_number"
                    )
                ),
                "chunk_id": (
                    result.get(
                        "chunk_id"
                    )
                ),
                "content": (
                    result.get(
                        "document",
                        ""
                    )
                ),
                "hybrid_score": (
                    result.get(
                        "hybrid_score"
                    )
                ),
                "reranker_score": (
                    result.get(
                        "reranker_score"
                    )
                )
            }
        )

    # --------------------------------------------------
    # 7. Return results
    # --------------------------------------------------

    return {
        "query": request.query.strip(),
        "total_results": len(
            formatted_results
        ),
        "results": formatted_results
    }


# ==========================================================
# DOCUMENT SUMMARY
# ==========================================================


@app.post("/documents/{document_id}/summary")
def summarize_document(
    document_id: str
):

    # --------------------------------------------------
    # 1. Find document
    # --------------------------------------------------

    document = (
        document_registry_service.find_by_id(
            document_id
        )
    )

    if document is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Document not found."
            )
        )

    # --------------------------------------------------
    # 2. Locate extracted document text
    # --------------------------------------------------

    extracted_path = (
        EXTRACTED_DIR
        / f"{document_id}.json"
    )

    if not extracted_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                "Extracted document text not found."
            )
        )

    # --------------------------------------------------
    # 3. Load extracted pages
    # --------------------------------------------------

    try:

        with open(
            extracted_path,
            "r",
            encoding="utf-8"
        ) as file_handle:

            pages = json.load(
                file_handle
            )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to load extracted "
                f"document text: {str(error)}"
            )
        )

    # --------------------------------------------------
    # 4. Build document text
    # --------------------------------------------------

    document_text_parts = []

    for page in pages:

        page_number = page.get(
            "page_number",
            "Unknown"
        )

        text = page.get(
            "text",
            ""
        )

        if text.strip():

            document_text_parts.append(
                f"""
[PAGE {page_number}]

{text}
"""
            )

    document_text = "\n".join(
        document_text_parts
    )

    if not document_text.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "The document contains no "
                "usable text."
            )
        )

    # --------------------------------------------------
    # 5. Generate summary
    # --------------------------------------------------

    try:

        result = (
            summarization_service.summarize(
                document_text
            )
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document summarization failed: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------
    # 6. Return summary
    # --------------------------------------------------

    return {
        "document_id": document_id,
        "filename": document.get(
            "filename",
            "Unknown document"
        ),
        "summary": result.get(
            "summary",
            ""
        )
    }


# ==========================================================
# DOCUMENT COMPARISON
# ==========================================================


@app.post("/compare")
def compare_documents(
    request: CompareRequest
):

    # --------------------------------------------------
    # 1. Validate question
    # --------------------------------------------------

    if not isinstance(
        request.question,
        str
    ) or not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Comparison question cannot be empty."
            )
        )

    # --------------------------------------------------
    # 2. Validate number of results
    # --------------------------------------------------

    if request.n_results < 1:

        raise HTTPException(
            status_code=400,
            detail=(
                "n_results must be at least 1."
            )
        )

    # --------------------------------------------------
    # 3. Validate document list
    # --------------------------------------------------

    if not isinstance(
        request.document_ids,
        list
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "document_ids must be a list."
            )
        )

    cleaned_document_ids = [
        document_id.strip()
        for document_id in request.document_ids
        if isinstance(
            document_id,
            str
        )
        and document_id.strip()
    ]

    cleaned_document_ids = list(
        dict.fromkeys(
            cleaned_document_ids
        )
    )

    if len(cleaned_document_ids) < 2:

        raise HTTPException(
            status_code=400,
            detail=(
                "Comparison requires at least "
                "two unique documents."
            )
        )

    # --------------------------------------------------
    # 4. Validate document existence
    # --------------------------------------------------

    for document_id in cleaned_document_ids:

        document = (
            document_registry_service.find_by_id(
                document_id
            )
        )

        if document is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    f"Document not found: "
                    f"{document_id}"
                )
            )

    # --------------------------------------------------
    # 5. Run comparison
    # --------------------------------------------------

    try:

        result = (
            comparison_service.compare(
                question=request.question.strip(),
                document_ids=cleaned_document_ids,
                n_results=request.n_results
            )
        )

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document comparison failed: "
                f"{str(error)}"
            )
        )

    # --------------------------------------------------
    # 6. Return comparison
    # --------------------------------------------------

    return result


# ==========================================================
# CHAT / RAG
# ==========================================================


@app.post("/chat")
def chat(
    request: ChatRequest
):

    # --------------------------------------------------
    # 1. Validate question
    # --------------------------------------------------

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail=(
                "Question cannot be empty."
            )
        )

    # --------------------------------------------------
    # 2. Validate number of results
    # --------------------------------------------------

    if request.n_results < 1:

        raise HTTPException(
            status_code=400,
            detail=(
                "n_results must be at least 1."
            )
        )

    # --------------------------------------------------
    # 3. Validate document IDs
    # --------------------------------------------------

    document_ids = request.document_ids

    if document_ids is not None:

        cleaned_document_ids = [
            document_id.strip()
            for document_id in document_ids
            if isinstance(
                document_id,
                str
            )
            and document_id.strip()
        ]

        if not cleaned_document_ids:

            raise HTTPException(
                status_code=400,
                detail=(
                    "document_ids cannot be empty."
                )
            )

        document_ids = list(
            dict.fromkeys(
                cleaned_document_ids
            )
        )

    # --------------------------------------------------
    # 4. Validate document existence
    # --------------------------------------------------

    if document_ids is not None:

        for document_id in document_ids:

            document = (
                document_registry_service.find_by_id(
                    document_id
                )
            )

            if document is None:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Document not found: "
                        f"{document_id}"
                    )
                )

    # --------------------------------------------------
    # 5. Run RAG pipeline
    # --------------------------------------------------

    result = rag_service.answer(
        question=request.question,
        n_results=request.n_results,
        document_ids=document_ids
    )

    # --------------------------------------------------
    # 6. Return answer
    # --------------------------------------------------

    return result