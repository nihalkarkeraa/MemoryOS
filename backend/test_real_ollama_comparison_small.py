from services.comparison_service import comparison_service


# ==========================================================
# DOCUMENTS
# ==========================================================

DOCUMENT_A = "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"
DOCUMENT_B = "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"


# ==========================================================
# TEST
# ==========================================================

print("\n" + "=" * 70)
print("REAL OLLAMA — SMALL DOCUMENT COMPARISON TEST")
print("=" * 70)

question = "What is database indexing?"

print("\nQuestion:")
print(question)

print("\nSelected documents:")
print(f"Document 1: {DOCUMENT_A}")
print(f"Document 2: {DOCUMENT_B}")

print("\nRetrieving 3 chunks per document...")
print("Generating comparison using Ollama...")
print("This may take some time on CPU.\n")


result = comparison_service.compare(
    question=question,
    document_ids=[
        DOCUMENT_A,
        DOCUMENT_B
    ],
    n_results=3
)


# ==========================================================
# DISPLAY ANSWER
# ==========================================================

print("=" * 70)
print("COMPARISON ANSWER")
print("=" * 70)

print(result["answer"])


# ==========================================================
# DISPLAY SOURCES
# ==========================================================

print("\n" + "=" * 70)
print("SOURCES")
print("=" * 70)

for index, source in enumerate(
    result["sources"],
    start=1
):

    print(f"\nSource {index}")

    print(
        f"Document ID: "
        f"{source.get('document_id')}"
    )

    print(
        f"Filename: "
        f"{source.get('filename')}"
    )

    print(
        f"Page: "
        f"{source.get('page_number')}"
    )

    print(
        f"Reranker Score: "
        f"{source.get('reranker_score')}"
    )

    print(
        f"Hybrid Score: "
        f"{source.get('hybrid_score')}"
    )


# ==========================================================
# VALIDATION
# ==========================================================

source_document_ids = {
    source["document_id"]
    for source in result["sources"]
}


print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)


assert source_document_ids.issubset(
    {
        DOCUMENT_A,
        DOCUMENT_B
    }
)

assert DOCUMENT_A in source_document_ids
assert DOCUMENT_B in source_document_ids

print(
    "PASS: Sources belong only to the selected documents."
)


assert len(result["sources"]) == 6

print(
    "PASS: Retrieved 3 sources from each document."
)


assert isinstance(
    result["answer"],
    str
)

assert result["answer"].strip()

print(
    "PASS: Ollama returned a non-empty comparison."
)


# ==========================================================
# FINAL
# ==========================================================

print("\n" + "=" * 70)
print("REAL OLLAMA SMALL COMPARISON TEST COMPLETED")
print("=" * 70)