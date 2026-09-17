import json

from services.chunking_service import chunk_pages
from services.embedding_service import embedding_service
from services.chroma_service import chroma_service


DOCUMENT_ID = "5f5b88a5-29b9-428b-b6c9-7c7f511a840e"

EXTRACTED_FILE = (
    f"data/extracted/{DOCUMENT_ID}.json"
)


print("\n==============================")
print("MemoryOS Document Ingestion")
print("==============================")


# ---------------------------------
# 1. Load extracted pages
# ---------------------------------

with open(
    EXTRACTED_FILE,
    "r",
    encoding="utf-8"
) as file:

    pages = json.load(file)


print(f"Pages loaded: {len(pages)}")


# ---------------------------------
# 2. Create chunks
# ---------------------------------

chunks = chunk_pages(
    pages,
    DOCUMENT_ID
)


print(f"Chunks created: {len(chunks)}")


# ---------------------------------
# 3. Generate embeddings
# ---------------------------------

texts = [
    chunk["text"]
    for chunk in chunks
]


print("\nGenerating embeddings...")

embeddings = embedding_service.embed_texts(
    texts
)


print(
    f"Embeddings generated: "
    f"{len(embeddings)}"
)


print(
    f"Embedding dimensions: "
    f"{len(embeddings[0])}"
)


# ---------------------------------
# 4. Store in ChromaDB
# ---------------------------------

print("\nStoring chunks in ChromaDB...")


stored_count = chroma_service.add_chunks(
    chunks,
    embeddings
)


print(
    f"Chunks stored: "
    f"{stored_count}"
)


# ---------------------------------
# 5. Verify database
# ---------------------------------

database_count = chroma_service.count()


print("\n==============================")
print("Ingestion completed")
print("==============================")

print(
    f"ChromaDB collection count: "
    f"{database_count}"
)