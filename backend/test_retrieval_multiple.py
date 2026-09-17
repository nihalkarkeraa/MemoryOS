from services.embedding_service import embedding_service
from services.chroma_service import chroma_service


queries = [
    "What is database normalization?",
    "What is an ER model?",
    "What is NoSQL?",
    "What is MongoDB?",
    "What is database indexing?"
]


print("\n==============================")
print("MemoryOS Retrieval Evaluation")
print("==============================")


for query in queries:

    print("\n\n================================")
    print(f"QUERY: {query}")
    print("================================")

    # Generate query embedding
    query_embedding = embedding_service.embed_text(
        query
    )

    # Search ChromaDB
    results = chroma_service.search(
        query_embedding=query_embedding,
        n_results=3
    )

    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Display results
    for index in range(len(ids)):

        print("\n------------------------------")

        print(f"Result: {index + 1}")

        print(
            f"Page: "
            f"{metadatas[index]['page_number']}"
        )

        print(
            f"Distance: "
            f"{distances[index]:.4f}"
        )

        print("\nText:")

        print(
            documents[index][:500]
        )


print("\n\n==============================")
print("Evaluation completed")
print("==============================")