from services.chroma_service import (
    chroma_service
)

from services.embedding_service import (
    embedding_service
)

from services.rag_service import (
    RAGService
)


class FakeLLM:

    def generate(
        self,
        prompt: str,
        temperature: float = 0.2
    ):

        return (
            "This is a test response based only "
            "on the retrieved document context."
        )


print()
print("==============================")
print("MemoryOS RAG Document Filter Test")
print("==============================")
print()


# --------------------------------------------------
# Test document definitions
# --------------------------------------------------

document_a_id = "rag-filter-document-A"

document_b_id = "rag-filter-document-B"


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
# Create RAG service with fake LLM
# --------------------------------------------------

rag_service = RAGService(
    llm=FakeLLM()
)


# --------------------------------------------------
# Test unrestricted RAG
# --------------------------------------------------

print()
print("==============================")
print("Unrestricted RAG")
print("==============================")


unrestricted_result = (
    rag_service.answer(
        question="What is Python?",
        n_results=5
    )
)


print(
    "Answer:"
)

print(
    unrestricted_result["answer"]
)

print()
print(
    "Sources:"
)

for source in unrestricted_result[
    "sources"
]:

    print(
        source
    )


# --------------------------------------------------
# Test Document A RAG filter
# --------------------------------------------------

print()
print("==============================")
print("Document A RAG Filter")
print("==============================")


document_a_result = (
    rag_service.answer(
        question="What is Python?",
        n_results=5,
        document_ids=[
            document_a_id
        ]
    )
)


print(
    "Answer:"
)

print(
    document_a_result["answer"]
)

print()
print(
    "Sources:"
)

for source in document_a_result[
    "sources"
]:

    print(
        source
    )


# --------------------------------------------------
# Verify Document A sources
# --------------------------------------------------

print()
print(
    "Verifying Document A sources..."
)

for source in document_a_result[
    "sources"
]:

    assert (
        source["document_id"]
        == document_a_id
    )

print(
    "Document A source verification: PASS"
)


# --------------------------------------------------
# Test Document B RAG filter
# --------------------------------------------------

print()
print("==============================")
print("Document B RAG Filter")
print("==============================")


document_b_result = (
    rag_service.answer(
        question="What is Python?",
        n_results=5,
        document_ids=[
            document_b_id
        ]
    )
)


print(
    "Answer:"
)

print(
    document_b_result["answer"]
)

print()
print(
    "Sources:"
)

for source in document_b_result[
    "sources"
]:

    print(
        source
    )


# --------------------------------------------------
# Verify Document B sources
# --------------------------------------------------

print()
print(
    "Verifying Document B sources..."
)

for source in document_b_result[
    "sources"
]:

    assert (
        source["document_id"]
        == document_b_id
    )

print(
    "Document B source verification: PASS"
)


# --------------------------------------------------
# Test multiple-document RAG filter
# --------------------------------------------------

print()
print("==============================")
print("Multiple-Document RAG Filter")
print("==============================")


multi_document_result = (
    rag_service.answer(
        question="What is a database?",
        n_results=5,
        document_ids=[
            document_a_id,
            document_b_id
        ]
    )
)


print(
    "Answer:"
)

print(
    multi_document_result["answer"]
)

print()
print(
    "Sources:"
)

for source in multi_document_result[
    "sources"
]:

    print(
        source
    )


# --------------------------------------------------
# Verify multiple-document sources
# --------------------------------------------------

print()
print(
    "Verifying multiple-document sources..."
)

allowed_document_ids = {
    document_a_id,
    document_b_id
}

for source in multi_document_result[
    "sources"
]:

    assert (
        source["document_id"]
        in allowed_document_ids
    )

print(
    "Multiple-document source verification: PASS"
)


# --------------------------------------------------
# Cleanup
# --------------------------------------------------

print()
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
print("RAG Document Filter Test Completed")
print("==============================")