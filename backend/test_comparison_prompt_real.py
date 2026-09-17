from services.comparison_service import comparison_service


DOCUMENT_A = "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"

DOCUMENT_B = "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"

QUESTION = "Compare the indexing techniques or indexing-related approaches described in these two documents."


def main():

    print("=" * 70)
    print("MemoryOS - Real Comparison Prompt Test")
    print("=" * 70)

    # ------------------------------------------------------
    # Retrieve evidence from Document 1
    # ------------------------------------------------------

    print("\n[1] Retrieving Document 1...")

    results_a = comparison_service._retrieve_document_context(
        question=QUESTION,
        document_id=DOCUMENT_A,
        n_results=5
    )

    print(
        f"Document 1 candidates: {len(results_a)}"
    )

    selected_a = comparison_service._filter_evidence(
        results_a
    )

    print(
        f"Document 1 selected evidence: {len(selected_a)}"
    )

    # ------------------------------------------------------
    # Build Document 1 context
    # ------------------------------------------------------

    context_a = comparison_service._build_document_context(
        results=selected_a,
        document_id=DOCUMENT_A
    )

    print(
        f"Document 1 context length: {len(context_a)} characters"
    )

    # ------------------------------------------------------
    # Retrieve evidence from Document 2
    # ------------------------------------------------------

    print("\n[2] Retrieving Document 2...")

    results_b = comparison_service._retrieve_document_context(
        question=QUESTION,
        document_id=DOCUMENT_B,
        n_results=5
    )

    print(
        f"Document 2 candidates: {len(results_b)}"
    )

    selected_b = comparison_service._filter_evidence(
        results_b
    )

    print(
        f"Document 2 selected evidence: {len(selected_b)}"
    )

    # ------------------------------------------------------
    # Build Document 2 context
    # ------------------------------------------------------

    context_b = comparison_service._build_document_context(
        results=selected_b,
        document_id=DOCUMENT_B
    )

    print(
        f"Document 2 context length: {len(context_b)} characters"
    )

    # ------------------------------------------------------
    # Build the EXACT production prompt
    # ------------------------------------------------------

    print("\n[3] Building production comparison prompt...")

    prompt = comparison_service._build_prompt(
        question=QUESTION,
        document_contexts=[
            context_a,
            context_b
        ]
    )

    print(
        f"Prompt length: {len(prompt)} characters"
    )

    print("\n" + "=" * 70)
    print("GENERATED PROMPT")
    print("=" * 70)

    print(prompt)

    print("=" * 70)

    # ------------------------------------------------------
    # Send EXACT production prompt to Ollama
    # ------------------------------------------------------

    print("\n[4] Sending exact production prompt to Ollama...")
    print("Waiting for response...\n")

    answer = comparison_service.llm_service.generate(
        prompt
    )

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------

    print("=" * 70)
    print("OLLAMA RESPONSE")
    print("=" * 70)

    print(answer)

    print("=" * 70)

    if answer and answer.strip():

        print("\nRESULT: Real comparison prompt succeeded.")

    else:

        print("\nRESULT: Ollama returned an empty response.")


if __name__ == "__main__":
    main()