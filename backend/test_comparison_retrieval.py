from services.comparison_service import comparison_service


# ==========================================================
# DOCUMENTS
# ==========================================================

DOCUMENT_A = "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"
DOCUMENT_B = "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"


QUESTION = "What is database indexing?"


# ==========================================================
# TEST RETRIEVAL
# ==========================================================

print("\n" + "=" * 70)
print("COMPARISON RETRIEVAL ANALYSIS")
print("=" * 70)

print(f"\nQuestion: {QUESTION}")


for document_number, document_id in enumerate(
    [
        DOCUMENT_A,
        DOCUMENT_B
    ],
    start=1
):

    print("\n" + "=" * 70)
    print(
        f"DOCUMENT {document_number}"
    )
    print("=" * 70)

    results = (
        comparison_service._retrieve_document_context(
            question=QUESTION,
            document_id=document_id,
            n_results=5
        )
    )

    for rank, result in enumerate(
        results,
        start=1
    ):

        metadata = result.get(
            "metadata",
            {}
        )

        filename = metadata.get(
            "filename",
            "Unknown"
        )

        page = metadata.get(
            "page_number",
            "Unknown"
        )

        hybrid_score = result.get(
            "hybrid_score"
        )

        reranker_score = result.get(
            "reranker_score"
        )

        document_text = result.get(
            "document",
            ""
        )

        print("\n" + "-" * 60)

        print(
            f"Rank: {rank}"
        )

        print(
            f"Page: {page}"
        )

        print(
            f"Filename: {filename}"
        )

        print(
            f"Hybrid Score: {hybrid_score}"
        )

        print(
            f"Reranker Score: {reranker_score}"
        )

        print("\nText preview:")

        print(
            document_text[:500]
        )


print("\n" + "=" * 70)
print("RETRIEVAL ANALYSIS COMPLETED")
print("=" * 70)