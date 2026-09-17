from services.rag_service import rag_service


print("\n==============================")
print("MemoryOS RAG Service Test")
print("==============================")


question = "What is database indexing?"


print("\nQuestion:")
print(question)

print("\nRunning hybrid retrieval + RAG generation...")

result = rag_service.answer(
    question=question,
    n_results=5
)


print("\n==============================")
print("Generated Answer")
print("==============================")

print(result["answer"])


print("\n==============================")
print("Sources")
print("==============================")


for source in result["sources"]:

    print(
        f"[Source {source['source_number']}] "
        f"Page {source['page_number']} | "
        f"Chunk {source['chunk_id']} | "
        f"Score {source['hybrid_score']:.4f}"
    )


print("\n==============================")
print("RAG test completed")
print("==============================")