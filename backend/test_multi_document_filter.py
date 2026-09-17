from services.embedding_service import (
    embedding_service
)

from services.chroma_service import (
    chroma_service
)


print()
print("==============================")
print("MemoryOS Multi-Document Filter Test")
print("==============================")
print()


# --------------------------------------------------
# Test document definitions
# --------------------------------------------------

document_a_id = "filter-test-document-A"

document_b_id = "filter-test-document-B"


chunk_a = {
    "chunk_id": f"{document_a_id}_chunk_1",
    "document_id": document_a_id,
    "page_number": 1,
    "text": (
        "Python is a programming language "
        "used to build software applications."
    )
}


chunk_b = {
    "chunk_id": f"{document_b_id}_chunk_1",
    "document_id": document_b_id,
    "page_number": 1,
    "text": (
        "MongoDB is a NoSQL database used "
        "to store document-oriented data."
    )
}


# --------------------------------------------------
# Generate embeddings
# --------------------------------------------------

print("Generating test embeddings...")

embeddings = (
    embedding_service.embed_texts(
        [
            chunk_a["text"],
            chunk_b["text"]
        ]
    )
)


# --------------------------------------------------
# Store both documents
# --------------------------------------------------

print("Storing test documents...")

stored_count = (
    chroma_service.add_chunks(
        chunks=[
            chunk_a,
            chunk_b
        ],
        embeddings=embeddings
    )
)


print(
    f"Chunks stored: {stored_count}"
)


# --------------------------------------------------
# Verify document counts
# --------------------------------------------------

print()
print("==============================")
print("Document Chunk Counts")
print("==============================")

print(
    "Document A:",
    chroma_service.count_document_chunks(
        document_a_id
    )
)

print(
    "Document B:",
    chroma_service.count_document_chunks(
        document_b_id
    )
)


# --------------------------------------------------
# Create query embedding
# --------------------------------------------------

query = "What is Python?"

query_embedding = (
    embedding_service.embed_text(
        query
    )
)


# --------------------------------------------------
# Test unrestricted search
# --------------------------------------------------

print()
print("==============================")
print("Unrestricted Search")
print("==============================")

all_results = (
    chroma_service.search(
        query_embedding=query_embedding,
        n_results=2
    )
)


for index, document in enumerate(
    all_results["documents"][0],
    start=1
):

    metadata = (
        all_results["metadatas"][0][index - 1]
    )

    print(
        f"Result {index}: "
        f"Document ID = "
        f"{metadata['document_id']}"
    )

    print(
        f"Text = {document}"
    )

    print()


# --------------------------------------------------
# Test Document A filter
# --------------------------------------------------

print("==============================")
print("Document A Filter")
print("==============================")


document_a_results = (
    chroma_service.search(
        query_embedding=query_embedding,
        n_results=2,
        document_ids=[
            document_a_id
        ]
    )
)


for index, document in enumerate(
    document_a_results["documents"][0],
    start=1
):

    metadata = (
        document_a_results[
            "metadatas"
        ][0][index - 1]
    )

    print(
        f"Result {index}: "
        f"Document ID = "
        f"{metadata['document_id']}"
    )

    print(
        f"Text = {document}"
    )

    print()


# --------------------------------------------------
# Test Document B filter
# --------------------------------------------------

print("==============================")
print("Document B Filter")
print("==============================")


document_b_results = (
    chroma_service.search(
        query_embedding=query_embedding,
        n_results=2,
        document_ids=[
            document_b_id
        ]
    )
)


for index, document in enumerate(
    document_b_results["documents"][0],
    start=1
):

    metadata = (
        document_b_results[
            "metadatas"
        ][0][index - 1]
    )

    print(
        f"Result {index}: "
        f"Document ID = "
        f"{metadata['document_id']}"
    )

    print(
        f"Text = {document}"
    )

    print()


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

print("==============================")
print("Cleaning Test Documents")
print("==============================")


deleted_a = (
    chroma_service.delete_document(
        document_a_id
    )
)

deleted_b = (
    chroma_service.delete_document(
        document_b_id
    )
)


print(
    f"Deleted Document A chunks: {deleted_a}"
)

print(
    f"Deleted Document B chunks: {deleted_b}"
)


print()
print(
    "Remaining ChromaDB chunks:",
    chroma_service.count()
)


print()
print("==============================")
print("Multi-Document Filter Test Completed")
print("==============================")