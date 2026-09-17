from services.embedding_service import (
    embedding_service
)

from services.chroma_service import (
    chroma_service
)

from services.keyword_search_service import (
    keyword_search_service
)


print()
print("==============================")
print("MemoryOS Keyword Document Filter Test")
print("==============================")
print()


# --------------------------------------------------
# Test document definitions
# --------------------------------------------------

document_a_id = "keyword-filter-document-A"

document_b_id = "keyword-filter-document-B"


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
# Search without filter
# --------------------------------------------------

print()
print("==============================")
print("Unrestricted Keyword Search")
print("==============================")


all_results = (
    keyword_search_service.search(
        query="Python",
        n_results=5
    )
)


for index, result in enumerate(
    all_results,
    start=1
):

    print(
        f"Result {index}: "
        f"Document ID = "
        f"{result['metadata']['document_id']}"
    )

    print(
        f"Text = {result['document']}"
    )

    print(
        f"Keyword Score = "
        f"{result['keyword_score']}"
    )

    print()


# --------------------------------------------------
# Search only Document A
# --------------------------------------------------

print("==============================")
print("Document A Keyword Filter")
print("==============================")


document_a_results = (
    keyword_search_service.search(
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
        f"Result {index}: "
        f"Document ID = "
        f"{result['metadata']['document_id']}"
    )

    print(
        f"Text = {result['document']}"
    )

    print()


# --------------------------------------------------
# Search only Document B
# --------------------------------------------------

print("==============================")
print("Document B Keyword Filter")
print("==============================")


document_b_results = (
    keyword_search_service.search(
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
            f"Result {index}: "
            f"Document ID = "
            f"{result['metadata']['document_id']}"
        )

        print(
            f"Text = {result['document']}"
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
print("Keyword Document Filter Test Completed")
print("==============================")