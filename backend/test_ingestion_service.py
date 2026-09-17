from pathlib import Path
from uuid import uuid4

from services.ingestion_service import (
    ingestion_service
)


print("\n==============================")
print("MemoryOS Ingestion Service Test")
print("==============================")


# Use the existing test PDF.
pdf_path = Path(
    "data/uploads/test.pdf"
)


if not pdf_path.exists():

    print(
        f"\nERROR: Test PDF not found:"
        f"\n{pdf_path}"
    )

    raise SystemExit(1)


# Generate a test document ID.
document_id = str(uuid4())


print("\nTest PDF:")
print(pdf_path)

print("\nDocument ID:")
print(document_id)

print("\nRunning ingestion pipeline...")


result = ingestion_service.ingest_pdf(
    file_path=str(pdf_path),
    document_id=document_id
)


print("\n==============================")
print("Ingestion Result")
print("==============================")


print(
    f"Document ID: "
    f"{result['document_id']}"
)

print(
    f"Total pages: "
    f"{result['total_pages']}"
)

print(
    f"Total chunks: "
    f"{result['total_chunks']}"
)

print(
    f"Embeddings generated: "
    f"{result['embeddings_generated']}"
)

print(
    f"Chunks stored: "
    f"{result['chunks_stored']}"
)


print("\n==============================")
print("ChromaDB Verification")
print("==============================")


print(
    f"Total chunks currently in ChromaDB: "
    f"{ingestion_service.chroma_service.count()}"
)


print("\n==============================")
print("Ingestion test completed")
print("==============================")