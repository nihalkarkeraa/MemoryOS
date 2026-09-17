import json

from services.embedding_service import embedding_service


DOCUMENT_ID = "5f5b88a5-29b9-428b-b6c9-7c7f511a840e"

EXTRACTED_FILE = (
    f"data/extracted/{DOCUMENT_ID}.json"
)


# Load extracted pages
with open(EXTRACTED_FILE, "r", encoding="utf-8") as file:
    pages = json.load(file)


# Recreate chunks using the existing chunking service
from services.chunking_service import chunk_pages


chunks = chunk_pages(
    pages,
    DOCUMENT_ID
)


print("\n--------------------")
print("Document embedding test")
print("--------------------")

print(f"Document ID: {DOCUMENT_ID}")
print(f"Total pages: {len(pages)}")
print(f"Total chunks: {len(chunks)}")


# Extract chunk texts
texts = [
    chunk["text"]
    for chunk in chunks
]


print("\nGenerating embeddings...")


# Generate embeddings for all chunks
embeddings = embedding_service.embed_texts(texts)


print("Embeddings generated successfully.")


print("\n--------------------")
print("Embedding results")
print("--------------------")

print(f"Total chunks: {len(chunks)}")
print(f"Total embeddings: {len(embeddings)}")
print(f"Embedding dimensions: {len(embeddings[0])}")


# Display information about first 3 chunks
for index in range(min(3, len(chunks))):

    print("\n--------------------")

    print(f"Chunk ID: {chunks[index]['chunk_id']}")
    print(f"Document ID: {chunks[index]['document_id']}")
    print(f"Page: {chunks[index]['page_number']}")

    print(f"Text characters: {len(chunks[index]['text'])}")

    print(
        f"Embedding dimensions: "
        f"{len(embeddings[index])}"
    )

    print(
        f"First 5 values: "
        f"{embeddings[index][:5]}"
    )