from services.embedding_service import embedding_service
from services.chroma_service import chroma_service


query = "What is database normalization?"


print("\n==============================")
print("MemoryOS Semantic Retrieval")
print("==============================")


# ---------------------------------
# 1. Convert query into embedding
# ---------------------------------

print("\nGenerating query embedding...")

query_embedding = embedding_service.embed_text(
    query
)


print(
    f"Query embedding dimensions: "
    f"{len(query_embedding)}"
)


# ---------------------------------
# 2. Search ChromaDB
# ---------------------------------

print("\nSearching ChromaDB...")

results = chroma_service.search(
    query_embedding=query_embedding,
    n_results=5
)


# ---------------------------------
# 3. Display retrieved chunks
# ---------------------------------

print("\n==============================")
print("Retrieved Results")
print("==============================")


ids = results["ids"][0]
documents = results["documents"][0]
metadatas = results["metadatas"][0]
distances = results["distances"][0]


for index in range(len(ids)):

    print("\n------------------------------")

    print(f"Result: {index + 1}")
    print(f"Chunk ID: {ids[index]}")
    print(
        f"Document ID: "
        f"{metadatas[index]['document_id']}"
    )
    print(
        f"Page: "
        f"{metadatas[index]['page_number']}"
    )
    print(
        f"Distance: "
        f"{distances[index]}"
    )

    print("\nText:")
    print(documents[index][:1000])


print("\n==============================")
print("Retrieval completed")
print("==============================")