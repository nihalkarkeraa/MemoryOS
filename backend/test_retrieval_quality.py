from services.document_registry_service import (
    document_registry_service
)

from services.hybrid_retrieval_service import (
    hybrid_retrieval_service
)


print()
print("==============================")
print("MemoryOS Retrieval Quality Test")
print("==============================")
print()


# --------------------------------------------------
# Find available documents
# --------------------------------------------------

documents = (
    document_registry_service.list_documents()
)


if not documents:

    print(
        "No documents are registered."
    )

    print(
        "Please upload the DBMS PDF first."
    )

    raise SystemExit


print(
    f"Registered documents: {len(documents)}"
)

print()


for document in documents:

    print(
        f"Document ID: "
        f"{document['document_id']}"
    )

    print(
        f"Filename: "
        f"{document['filename']}"
    )

    print(
        f"Pages: "
        f"{document.get('total_pages')}"
    )

    print(
        f"Chunks: "
        f"{document.get('total_chunks')}"
    )

    print()


# --------------------------------------------------
# Evaluation questions
# --------------------------------------------------

questions = [

    "What is database indexing?",

    "What is MongoDB?",

    "What is database normalization?",

    "What are NoSQL databases?",

    "What is the Entity Relationship model?"
]


# --------------------------------------------------
# Run retrieval evaluation
# --------------------------------------------------

for question in questions:

    print()
    print("==============================")
    print(
        f"QUESTION: {question}"
    )
    print("==============================")
    print()

    results = (
        hybrid_retrieval_service.search(
            query=question,
            n_results=5
        )
    )

    if not results:

        print(
            "No retrieval results."
        )

        continue

    for index, result in enumerate(
        results,
        start=1
    ):

        metadata = result[
            "metadata"
        ]

        print(
            f"Rank {index}"
        )

        print(
            f"Document ID: "
            f"{metadata['document_id']}"
        )

        print(
            f"Page: "
            f"{metadata['page_number']}"
        )

        print(
            f"Hybrid Score: "
            f"{result['hybrid_score']:.6f}"
        )

        print(
            f"Semantic Score: "
            f"{result['semantic_score']:.6f}"
        )

        print(
            f"Keyword Score: "
            f"{result['keyword_score']:.6f}"
        )

        print(
            f"Exact Match Bonus: "
            f"{result['exact_match_bonus']:.6f}"
        )

        print(
            f"Matched Words: "
            f"{result['matched_words']}"
        )

        text = result[
            "document"
        ]

        # Keep terminal output manageable.
        preview = text.replace(
            "\n",
            " "
        )

        if len(preview) > 300:

            preview = (
                preview[:300]
                + "..."
            )

        print(
            f"Text: {preview}"
        )

        print(
            "-" * 60
        )


# --------------------------------------------------
# Completion
# --------------------------------------------------

print()
print("==============================")
print("Retrieval Quality Test Completed")
print("==============================")
print()