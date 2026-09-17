from services.embedding_service import (
    embedding_service
)

from services.chroma_service import (
    chroma_service
)

from services.hybrid_retrieval_service import (
    hybrid_retrieval_service
)


print()
print("==============================")
print("MemoryOS Hybrid Document Filter Test")
print("==============================")
print()


# --------------------------------------------------
# Test document definitions
# --------------------------------------------------

document_a_id = "hybrid-filter-document-A"

document_b_id = "hybrid-filter-document-B"


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
# Store test documents
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
# Test unrestricted hybrid retrieval
# --------------------------------------------------

print()
print("==============================")
print("Unrestricted Hybrid Search")
print("==============================")


all_results = (
    hybrid_retrieval_service.search(
        query="Python",
        n_results=5
    )
)


for index, result in enumerate(
    all_results,
    start=1
):

    print(
        f"Result {index}:"
    )

    print(
        f"Document ID = "
        f"{result['metadata']['document_id']}"
    )

    print(
        f"Text = "
        f"{result['document']}"
    )

    print(
        f"Hybrid Score = "
        f"{result['hybrid_score']}"
    )

    print()


# --------------------------------------------------
# Test Document A filter
# --------------------------------------------------

print("==============================")
print("Document A Hybrid Filter")
print("==============================")


document_a_results = (
    hybrid_retrieval_service.search(
        query="Python",
        n_results=5,
        document_ids=[
            document_a_id
        ]
    )
)


for index, result in enumerate(
    document_a_results,
    start=1
):

    print(
        f"Result {index}:"
    )

    print(
        f"Document ID = "
        f"{result['metadata']['document_id']}"
    )

    print(
        f"Text = "
        f"{result['document']}"
    )

    print()


# --------------------------------------------------
# Test Document B filter
# --------------------------------------------------

print("==============================")
print("Document B Hybrid Filter")
print("==============================")


document_b_results = (
    hybrid_retrieval_service.search(
        query="Python",
        n_results=5,
        document_ids=[
            document_b_id
        ]
    )
)


if not document_b_results:

    print(
        "No results returned."
    )

else:

    for index, result in enumerate(
        document_b_results,
        start=1
    ):

        print(
            f"Result {index}:"
        )

        print(
            f"Document ID = "
            f"{result['metadata']['document_id']}"
        )

        print(
            f"Text = "
            f"{result['document']}"
        )

        print()


# --------------------------------------------------
# Test multiple-document filter
# --------------------------------------------------

print("==============================")
print("Multiple-Document Hybrid Filter")
print("==============================")


multi_document_results = (
    hybrid_retrieval_service.search(
        query="database",
        n_results=5,
        document_ids=[
            document_a_id,
            document_b_id
        ]
    )
)


for index, result in enumerate(
    multi_document_results,
    start=1
):

    print(
        f"Result {index}:"
    )

    print(
        f"Document ID = "
        f"{result['metadata']['document_id']}"
    )

    print(
        f"Text = "
        f"{result['document']}"
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
print("Hybrid Document Filter Test Completed")
print("==============================")