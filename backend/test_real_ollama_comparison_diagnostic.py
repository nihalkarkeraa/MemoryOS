import time

from services import comparison_service as comparison_module


# ==========================================================
# CONFIGURATION
# ==========================================================

DOCUMENT_A = "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"

DOCUMENT_B = "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"

QUESTION = "What is database indexing?"

RETRIEVAL_RESULTS = 3


# ==========================================================
# RETRIEVE DOCUMENT EVIDENCE
# ==========================================================

def retrieve_document_evidence(
    service,
    document_id,
    document_number
):

    print("\n" + "-" * 70)

    print(
        f"DOCUMENT {document_number} — RETRIEVAL"
    )

    print("-" * 70)

    start_time = time.time()

    results = (
        service.hybrid_retrieval_service.search(
            query=QUESTION,
            n_results=RETRIEVAL_RESULTS,
            document_ids=[document_id]
        )
    )

    retrieval_time = time.time() - start_time

    print(
        f"\nRetrieval time: "
        f"{retrieval_time:.2f} seconds"
    )

    print(
        f"Retrieved candidates: "
        f"{len(results)}"
    )

    for index, result in enumerate(
        results,
        start=1
    ):

        print(f"\nCandidate {index}")

        print(
            f"  Document ID: "
            f"{result.get('document_id')}"
        )

        print(
            f"  Filename: "
            f"{result.get('filename')}"
        )

        print(
            f"  Page: "
            f"{result.get('page_number')}"
        )

        print(
            f"  Chunk ID: "
            f"{result.get('chunk_id')}"
        )

        print(
            f"  Reranker score: "
            f"{result.get('reranker_score')}"
        )

        print(
            f"  Hybrid score: "
            f"{result.get('hybrid_score')}"
        )

    # ------------------------------------------------------
    # Filter evidence
    # ------------------------------------------------------

    filtered_results = (
        service._filter_evidence(
            results
        )
    )

    print(
        f"\nSelected evidence: "
        f"{len(filtered_results)}"
    )

    for index, result in enumerate(
        filtered_results,
        start=1
    ):

        print(
            f"\nSelected Evidence {index}"
        )

        print(
            f"  Document ID: "
            f"{result.get('document_id')}"
        )

        print(
            f"  Page: "
            f"{result.get('page_number')}"
        )

        print(
            f"  Chunk ID: "
            f"{result.get('chunk_id')}"
        )

        print(
            f"  Reranker score: "
            f"{result.get('reranker_score')}"
        )

    return filtered_results


# ==========================================================
# MAIN DIAGNOSTIC
# ==========================================================

def main():

    print("\n" + "=" * 70)

    print(
        "MEMORYOS — REAL OLLAMA COMPARISON DIAGNOSTIC"
    )

    print("=" * 70)

    service = (
        comparison_module.comparison_service
    )

    # ======================================================
    # STEP 1 — DOCUMENT A
    # ======================================================

    document_a_results = (
        retrieve_document_evidence(
            service=service,
            document_id=DOCUMENT_A,
            document_number=1
        )
    )

    # ======================================================
    # STEP 2 — DOCUMENT B
    # ======================================================

    document_b_results = (
        retrieve_document_evidence(
            service=service,
            document_id=DOCUMENT_B,
            document_number=2
        )
    )

    # ======================================================
    # STEP 3 — BUILD DOCUMENT CONTEXT
    # ======================================================

    print("\n" + "-" * 70)

    print(
        "STEP 3 — BUILDING DOCUMENT CONTEXT"
    )

    print("-" * 70)

    start_time = time.time()

    context_a = (
        service._build_document_context(
            document_a_results,
            DOCUMENT_A
        )
    )

    context_b = (
        service._build_document_context(
            document_b_results,
            DOCUMENT_B
        )
    )

    context_time = time.time() - start_time

    print(
        f"\nContext construction time: "
        f"{context_time:.4f} seconds"
    )

    print(
        f"Document 1 context length: "
        f"{len(context_a)} characters"
    )

    print(
        f"Document 2 context length: "
        f"{len(context_b)} characters"
    )

    # ------------------------------------------------------
    # Combine contexts exactly as comparison service does
    # ------------------------------------------------------

    document_context = (
        context_a
        + "\n\n"
        + context_b
    )

    print(
        f"Combined context length: "
        f"{len(document_context)} characters"
    )

    # ======================================================
    # STEP 4 — BUILD EXACT COMPARISON PROMPT
    # ======================================================

    print("\n" + "-" * 70)

    print(
        "STEP 4 — BUILDING COMPARISON PROMPT"
    )

    print("-" * 70)

    start_time = time.time()

    prompt = service._build_prompt(
        question=QUESTION,
        document_context=document_context
    )

    prompt_time = time.time() - start_time

    print(
        f"\nPrompt construction time: "
        f"{prompt_time:.4f} seconds"
    )

    print(
        f"Prompt length: "
        f"{len(prompt)} characters"
    )

    # ------------------------------------------------------
    # Rough token estimate
    # ------------------------------------------------------

    estimated_tokens = (
        len(prompt) / 4
    )

    print(
        f"Estimated prompt tokens: "
        f"{estimated_tokens:.0f}"
    )

    # ------------------------------------------------------
    # Print prompt
    # ------------------------------------------------------

    print("\n" + "=" * 70)

    print(
        "EXACT COMPARISON PROMPT"
    )

    print("=" * 70)

    print(prompt)

    print("=" * 70)

    # ======================================================
    # STEP 5 — DIRECT OLLAMA GENERATION
    # ======================================================

    print("\n" + "-" * 70)

    print(
        "STEP 5 — DIRECT OLLAMA GENERATION"
    )

    print("-" * 70)

    print(
        "\nModel: phi3:mini"
    )

    print(
        "Sending the exact comparison prompt "
        "directly through the existing LLM service."
    )

    print(
        "\nWaiting for Ollama response..."
    )

    start_time = time.time()

    try:

        answer = (
            service.llm_service.generate(
                prompt
            )
        )

        generation_time = (
            time.time() - start_time
        )

        print(
            "\nOllama response received."
        )

        print(
            f"Generation time: "
            f"{generation_time:.2f} seconds"
        )

        print(
            f"Response length: "
            f"{len(answer)} characters"
        )

        print("\n" + "=" * 70)

        print(
            "OLLAMA COMPARISON RESPONSE"
        )

        print("=" * 70)

        print(answer)

        print("=" * 70)

        # --------------------------------------------------
        # Final diagnostic result
        # --------------------------------------------------

        print("\n" + "=" * 70)

        print(
            "DIAGNOSTIC RESULT"
        )

        print("=" * 70)

        print(
            "\nSUCCESS:"
        )

        print(
            "The exact MemoryOS comparison prompt "
            "was successfully processed by phi3:mini."
        )

        print(
            "\nThis means the comparison prompt "
            "and Ollama generation path work."
        )

        print(
            "If comparison_service.compare() still "
            "times out, we will investigate the "
            "difference between that method and "
            "this direct generation path."
        )

    except Exception as e:

        generation_time = (
            time.time() - start_time
        )

        print(
            "\nOLLAMA GENERATION FAILED"
        )

        print(
            f"Time before failure: "
            f"{generation_time:.2f} seconds"
        )

        print(
            f"Error type: "
            f"{type(e).__name__}"
        )

        print(
            f"Error: "
            f"{e}"
        )

        print("\n" + "=" * 70)

        print(
            "DIAGNOSTIC RESULT"
        )

        print("=" * 70)

        print(
            "\nThe exact comparison prompt "
            "also fails during generation."
        )

        print(
            "This would indicate that the "
            "comparison prompt/generation itself "
            "is the bottleneck."
        )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":
    main()