import services.rag_service as rag_module


class FakeLLM:

    def generate(self, prompt):

        print()
        print("=" * 60)
        print("FAKE LLM RECEIVED PROMPT")
        print("=" * 60)

        print(prompt)

        print("=" * 60)

        return "Reranker → RAG integration test response."


# --------------------------------------------------
# Save the real LLM service
# --------------------------------------------------

original_llm = rag_module.llm_service


# --------------------------------------------------
# Replace module-level LLM with fake LLM
# --------------------------------------------------

rag_module.llm_service = FakeLLM()


try:

    print()
    print("=" * 60)
    print("MemoryOS Reranker → RAG Integration Test")
    print("=" * 60)

    question = "What are NoSQL databases?"

    print()
    print("Question:")
    print(question)

    print()
    print("Running RAG...")

    result = rag_module.rag_service.answer(
        question=question,
        n_results=5
    )

    print()
    print("=" * 60)
    print("RAG RESULT")
    print("=" * 60)

    print()
    print("Answer:")
    print(
        result["answer"]
    )

    print()
    print("Sources:")

    for index, source in enumerate(
        result["sources"],
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

        print(
            "Text:",
            source.get("text", "")[:500]
        )

    print()
    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)

    if not result.get("sources"):

        print()
        print("TEST FAILED:")
        print("No sources were returned.")

    else:

        pages = [
            source.get("page_number")
            for source in result["sources"]
        ]

        print()
        print("Retrieved pages:")
        print(pages)

        # Page 6 was the top NoSQL result
        # from our cross-encoder reranker test.

        if 6 in pages:

            print()
            print(
                "TEST PASSED:"
            )

            print(
                "Reranked NoSQL result "
                "reached the RAG pipeline."
            )

        else:

            print()
            print(
                "TEST WARNING:"
            )

            print(
                "Expected page 6 was not found "
                "in the final RAG sources."
            )

finally:

    # --------------------------------------------------
    # Restore the real LLM service
    # --------------------------------------------------

    rag_module.llm_service = original_llm

    print()
    print(
        "Original LLM service restored."
    )