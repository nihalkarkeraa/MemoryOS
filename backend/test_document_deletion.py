from uuid import uuid4

from services.embedding_service import (
    embedding_service
)

from services.chroma_service import (
    chroma_service
)

from services.document_registry_service import (
    document_registry_service
)


print("\n==============================")
print("MemoryOS Document Deletion Test")
print("==============================")


# --------------------------------------------------
# 1. Create a temporary test document
# --------------------------------------------------

document_id = (
    f"deletion-test-{uuid4()}"
)

chunk_id = (
    f"{document_id}_chunk_1"
)

text = (
    "This is a temporary document used "
    "to test document deletion."
)


print("\nTemporary document ID:")
print(document_id)


# --------------------------------------------------
# 2. Generate embedding
# --------------------------------------------------

embedding = (
    embedding_service.embed_text(
        text
    )
)


# --------------------------------------------------
# 3. Store temporary chunk
# --------------------------------------------------

chunk = {

    "chunk_id": chunk_id,

    "document_id": document_id,

    "page_number": 1,

    "text": text
}


stored_count = (
    chroma_service.add_chunks(
        chunks=[chunk],
        embeddings=[embedding]
    )
)


print("\n==============================")
print("ChromaDB Insert")
print("==============================")


print(
    f"Chunks stored: {stored_count}"
)


chunks_before = (
    chroma_service.count_document_chunks(
        document_id
    )
)


print(
    f"Chunks belonging to test document: "
    f"{chunks_before}"
)


# --------------------------------------------------
# 4. Register temporary document
# --------------------------------------------------

temporary_document = {

    "document_id": document_id,

    "filename": "deletion_test.pdf",

    "file_hash": (
        f"temporary-{uuid4()}"
    ),

    "upload_time": "test",

    "status": "processed",

    "total_pages": 1,

    "total_chunks": 1
}


document_registry_service.register_document(
    temporary_document
)


print("\n==============================")
print("Registry Insert")
print("==============================")


print(
    "Temporary document registered."
)


# --------------------------------------------------
# 5. Delete ChromaDB chunks
# --------------------------------------------------

deleted_chunks = (
    chroma_service.delete_document(
        document_id
    )
)


print("\n==============================")
print("ChromaDB Deletion")
print("==============================")


print(
    f"Chunks deleted: {deleted_chunks}"
)


chunks_after = (
    chroma_service.count_document_chunks(
        document_id
    )
)


print(
    f"Chunks remaining: {chunks_after}"
)


# --------------------------------------------------
# 6. Delete registry entry
# --------------------------------------------------

deleted_document = (
    document_registry_service.delete_document(
        document_id
    )
)


print("\n==============================")
print("Registry Deletion")
print("==============================")


if deleted_document:

    print(
        "Registry document deleted successfully."
    )

else:

    print(
        "ERROR: Registry document was not deleted."
    )


registry_check = (
    document_registry_service.find_by_id(
        document_id
    )
)


# --------------------------------------------------
# 7. Final verification
# --------------------------------------------------

print("\n==============================")
print("Final Verification")
print("==============================")


print(
    f"ChromaDB chunks remaining: "
    f"{chunks_after}"
)

print(
    f"Registry document exists: "
    f"{registry_check is not None}"
)


if (
    deleted_chunks == 1
    and chunks_after == 0
    and deleted_document is not None
    and registry_check is None
):

    print(
        "\nSUCCESS: Document deletion "
        "works correctly."
    )

else:

    print(
        "\nERROR: Document deletion "
        "verification failed."
    )


print("\n==============================")
print("Deletion test completed")
print("==============================")