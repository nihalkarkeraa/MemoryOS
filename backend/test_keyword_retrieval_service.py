from services.keyword_search_service import (
    keyword_search_service
)


queries = [
    "What is database indexing?",
    "What is MongoDB?",
    "What is database normalization?",
    "What is NoSQL?",
    "database indexing",
    "MongoDB database",
    "database normalization"
]


print("\n==============================")
print("MemoryOS Keyword Retrieval v2")
print("==============================")


for query in queries:

    print("\n\n================================")
    print(f"QUERY: {query}")
    print("================================")

    results = keyword_search_service.search(
        query=query,
        n_results=5
    )

    if not results:

        print("\nNo keyword matches found.")

        continue

    for index, result in enumerate(results):

        print("\n------------------------------")

        print(
            f"Result: {index + 1}"
        )

        print(
            f"Page: "
            f"{result['metadata']['page_number']}"
        )

        print(
            f"Keyword Score: "
            f"{result['keyword_score']:.4f}"
        )

        print(
            f"Query Coverage: "
            f"{result['query_coverage']:.4f}"
        )

        print(
            f"Matched Words: "
            f"{result['matched_words']}"
        )

        print("\nText:")

        print(
            result["document"][:500]
        )


print("\n\n==============================")
print("Keyword Retrieval v2 completed")
print("==============================")