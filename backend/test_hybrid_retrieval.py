from services.hybrid_retrieval_service import (
    hybrid_retrieval_service
)


queries = [
    "What is database indexing?",
    "What is MongoDB?",
    "What is database normalization?",
    "What is NoSQL?",
    "What is an ER model?"
]


print("\n==============================")
print("MemoryOS Hybrid Retrieval v2")
print("==============================")


for query in queries:

    print("\n\n================================")
    print(f"QUERY: {query}")
    print("================================")

    results = hybrid_retrieval_service.search(
        query=query,
        n_results=5
    )

    if not results:

        print("\nNo relevant results found.")

        continue

    for index, result in enumerate(
        results
    ):

        print("\n------------------------------")

        print(
            f"Result: {index + 1}"
        )

        print(
            f"Page: "
            f"{result['metadata']['page_number']}"
        )

        print(
            f"Hybrid Score: "
            f"{result['hybrid_score']:.4f}"
        )

        print(
            f"Semantic Score: "
            f"{result['semantic_score']:.4f}"
        )

        print(
            f"Keyword Score: "
            f"{result['keyword_score']:.4f}"
        )

        print(
            f"Exact Match Bonus: "
            f"{result['exact_match_bonus']:.4f}"
        )

        print(
            f"Query Coverage: "
            f"{result['query_coverage']:.4f}"
        )

        print(
            f"Matched Words: "
            f"{result['matched_words']}"
        )

        print(
            f"Semantic Distance: "
            f"{result['semantic_distance']}"
        )

        print("\nText:")

        print(
            result["document"][:500]
        )


print("\n\n==============================")
print("Hybrid Retrieval v2 completed")
print("==============================")