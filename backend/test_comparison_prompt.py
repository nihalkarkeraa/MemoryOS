from services.comparison_service import comparison_service


# ==========================================================
# DOCUMENTS
# ==========================================================

DOCUMENT_A = "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"
DOCUMENT_B = "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"


# ==========================================================
# RETRIEVE RESULTS
# ==========================================================

question = "What is database indexing?"

print("\n" + "=" * 70)
print("MEMORYOS COMPARISON PROMPT INSPECTION")
print("=" * 70)

print("\nQuestion:")
print(question)


document_contexts = []

for index, document_id in enumerate(
    [
        DOCUMENT_A,
        DOCUMENT_B
    ],
    start=1
):

    print(
        f"\nRetrieving document {index}..."
    )

    results = (
        comparison_service._retrieve_document_context(
            question=question,
            document_id=document_id,
            n_results=3
        )
    )

    print(
        f"Retrieved chunks: {len(results)}"
    )

    context = (
        comparison_service._build_document_context(
            results=results,
            document_id=document_id
        )
    )

    document_contexts.append(
        context
    )


# ==========================================================
# BUILD PROMPT
# ==========================================================

prompt = (
    comparison_service._build_prompt(
        question=question,
        document_contexts=document_contexts
    )
)


# ==========================================================
# PROMPT STATISTICS
# ==========================================================

print("\n" + "=" * 70)
print("PROMPT STATISTICS")
print("=" * 70)

print(
    f"\nCharacters: {len(prompt)}"
)

print(
    f"Approximate tokens: {len(prompt) // 4}"
)


# ==========================================================
# PRINT PROMPT
# ==========================================================

print("\n" + "=" * 70)
print("FULL PROMPT")
print("=" * 70)

print(prompt)


# ==========================================================
# DONE
# ==========================================================

print("\n" + "=" * 70)
print("PROMPT INSPECTION COMPLETED")
print("=" * 70)