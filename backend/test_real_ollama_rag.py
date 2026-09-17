import services.rag_service as rag_module


print()
print("=" * 70)
print("MemoryOS — REAL OLLAMA RAG TEST")
print("=" * 70)


# --------------------------------------------------
# Test 1: Grounded question
# --------------------------------------------------

question_1 = "What are NoSQL databases?"

print()
print("=" * 70)
print("TEST 1 — GROUNDED QUESTION")
print("=" * 70)

print()
print("Question:")
print(question_1)

print()
print("Running RAG with real Ollama...")

result_1 = rag_module.rag_service.answer(
    question=question_1,
    n_results=5
)


print()
print("Answer:")
print(result_1["answer"])


print()
print("Sources:")

for index, source in enumerate(
    result_1["sources"],
    start=1
):

    print()
    print(f"Source {index}")

    print(
        "Document ID:",
        source.get("document_id")
    )

    print(
        "Page:",
        source.get("page_number")
    )


# --------------------------------------------------
# Validation
# --------------------------------------------------

print()
print("=" * 70)
print("TEST 1 VALIDATION")
print("=" * 70)

if result_1.get("answer"):

    print()
    print("PASS: Ollama generated an answer.")

else:

    print()
    print("FAIL: Ollama returned an empty answer.")


if result_1.get("sources"):

    print(
        "PASS: RAG returned source citations."
    )

else:

    print(
        "FAIL: RAG returned no sources."
    )


pages_1 = [
    source.get("page_number")
    for source in result_1.get("sources", [])
]


print()
print(
    "Retrieved pages:",
    pages_1
)


if 6 in pages_1:

    print(
        "PASS: Reranked NoSQL page 6 "
        "is present in the final sources."
    )

else:

    print(
        "WARNING: Page 6 was not present "
        "in the final source list."
    )


# --------------------------------------------------
# Test 2: Another grounded question
# --------------------------------------------------

question_2 = "What is database indexing?"

print()
print("=" * 70)
print("TEST 2 — DATABASE INDEXING")
print("=" * 70)

print()
print("Question:")
print(question_2)

print()
print("Running RAG with real Ollama...")

result_2 = rag_module.rag_service.answer(
    question=question_2,
    n_results=5
)


print()
print("Answer:")
print(result_2["answer"])


print()
print("Sources:")

for index, source in enumerate(
    result_2["sources"],
    start=1
):

    print()
    print(f"Source {index}")

    print(
        "Document ID:",
        source.get("document_id")
    )

    print(
        "Page:",
        source.get("page_number")
    )


print()
print("=" * 70)
print("TEST 2 VALIDATION")
print("=" * 70)

if result_2.get("answer"):

    print(
        "PASS: Ollama generated an indexing answer."
    )

else:

    print(
        "FAIL: Ollama returned an empty answer."
    )


if result_2.get("sources"):

    print(
        "PASS: Indexing answer has source citations."
    )

else:

    print(
        "FAIL: Indexing answer has no sources."
    )


# --------------------------------------------------
# Test 3: Out-of-context question
# --------------------------------------------------

question_3 = (
    "Who was the first person to walk on Mars?"
)

print()
print("=" * 70)
print("TEST 3 — OUT-OF-CONTEXT QUESTION")
print("=" * 70)

print()
print("Question:")
print(question_3)

print()
print("Running RAG with real Ollama...")

result_3 = rag_module.rag_service.answer(
    question=question_3,
    n_results=5
)


print()
print("Answer:")
print(result_3["answer"])


print()
print("Sources:")

for index, source in enumerate(
    result_3["sources"],
    start=1
):

    print()
    print(f"Source {index}")

    print(
        "Document ID:",
        source.get("document_id")
    )

    print(
        "Page:",
        source.get("page_number")
    )


print()
print("=" * 70)
print("TEST 3 VALIDATION")
print("=" * 70)

print()
print(
    "This test is mainly for manual inspection."
)

print(
    "The model should avoid confidently "
    "inventing an answer when the document "
    "does not contain the requested information."
)


# --------------------------------------------------
# Final summary
# --------------------------------------------------

print()
print("=" * 70)
print("FINAL TEST SUMMARY")
print("=" * 70)

print()
print("Grounded question:")
print(
    "Answer returned:",
    bool(result_1.get("answer"))
)

print(
    "Sources returned:",
    len(result_1.get("sources", []))
)


print()
print("Database indexing:")
print(
    "Answer returned:",
    bool(result_2.get("answer"))
)

print(
    "Sources returned:",
    len(result_2.get("sources", []))
)


print()
print("Out-of-context question:")
print(
    "Answer returned:",
    bool(result_3.get("answer"))
)

print(
    "Sources returned:",
    len(result_3.get("sources", []))
)


print()
print("=" * 70)
print("REAL OLLAMA RAG TEST COMPLETE")
print("=" * 70)