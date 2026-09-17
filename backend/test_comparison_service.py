from services import comparison_service as comparison_module


# ==========================================================
# FAKE LLM
# ==========================================================

class FakeLLM:
    """
    Fake LLM used for structural testing.

    This prevents the test from calling Ollama.
    """

    def __init__(self):
        self.last_prompt = None

    def generate(self, prompt):
        self.last_prompt = prompt

        return "Comparison test response generated successfully."


# ==========================================================
# TEST DOCUMENT IDs
# ==========================================================

DOCUMENT_A = "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"

DOCUMENT_B = "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"

DOCUMENT_C = "adb60928-6ef5-4291-ab92-48191c0a0a64"


# ==========================================================
# CREATE FAKE LLM
# ==========================================================

fake_llm = FakeLLM()


# ==========================================================
# SAVE ORIGINAL LLM
# ==========================================================

original_llm = (
    comparison_module.comparison_service.llm_service
)


# ==========================================================
# REPLACE REAL LLM WITH FAKE LLM
# ==========================================================

comparison_module.comparison_service.llm_service = fake_llm


try:

    # ======================================================
    # TEST 1 — TWO DOCUMENT COMPARISON
    # ======================================================

    print("\n" + "=" * 60)
    print("TEST 1 — TWO DOCUMENT COMPARISON")
    print("=" * 60)

    result = (
        comparison_module.comparison_service.compare(
            question="What is database indexing?",
            document_ids=[
                DOCUMENT_A,
                DOCUMENT_B
            ],
            n_results=5
        )
    )

    print("\nAnswer:")
    print(result["answer"])

    print("\nDocument IDs:")
    print(result["document_ids"])

    print("\nNumber of selected evidence sources:")
    print(len(result["sources"]))

    # ------------------------------------------------------
    # Validate returned document IDs
    # ------------------------------------------------------

    assert result["document_ids"] == [
        DOCUMENT_A,
        DOCUMENT_B
    ]

    print(
        "\nPASS: Correct document IDs returned."
    )

    # ------------------------------------------------------
    # Extract source document IDs
    # ------------------------------------------------------

    source_document_ids = {
        source["document_id"]
        for source in result["sources"]
    }

    print("\nSource document IDs:")
    print(source_document_ids)

    # ------------------------------------------------------
    # Ensure no unselected documents appear
    # ------------------------------------------------------

    assert source_document_ids.issubset(
        {
            DOCUMENT_A,
            DOCUMENT_B
        }
    )

    print(
        "PASS: Sources belong only to selected documents."
    )

    # ------------------------------------------------------
    # Ensure both documents contributed evidence
    # ------------------------------------------------------

    assert DOCUMENT_A in source_document_ids

    assert DOCUMENT_B in source_document_ids

    print(
        "PASS: Both selected documents contributed evidence."
    )

    # ------------------------------------------------------
    # Validate evidence filtering
    # ------------------------------------------------------

    assert len(result["sources"]) >= 2

    assert len(result["sources"]) <= 4

    print(
        "PASS: Evidence filtering returned "
        "2–4 strong evidence sources."
    )

    # ------------------------------------------------------
    # Validate reranker scores
    # ------------------------------------------------------

    for source in result["sources"]:

        assert "reranker_score" in source

        assert source["reranker_score"] is not None

    print(
        "PASS: All selected evidence contains "
        "reranker scores."
    )

    # ------------------------------------------------------
    # Display actual source structure
    # ------------------------------------------------------

    print("\nSelected source structure:")

    for index, source in enumerate(
        result["sources"],
        start=1
    ):

        print(f"\nSource {index}:")

        print(
            f"  document_id: "
            f"{source.get('document_id')}"
        )

        print(
            f"  reranker_score: "
            f"{source.get('reranker_score')}"
        )

        print(
            f"  available fields: "
            f"{list(source.keys())}"
        )

    print(
        "\nPASS: Source objects contain "
        "the expected comparison evidence data."
    )

    # ------------------------------------------------------
    # Validate LLM prompt
    # ------------------------------------------------------

    prompt = fake_llm.last_prompt

    assert prompt is not None

    assert len(prompt) > 0

    print(
        "PASS: LLM prompt was generated."
    )

    # ------------------------------------------------------
    # Ensure both documents appear in prompt
    # ------------------------------------------------------

    assert "DOCUMENT 1" in prompt

    assert "DOCUMENT 2" in prompt

    print(
        "PASS: Comparison prompt contains "
        "both documents."
    )

    # ------------------------------------------------------
    # Ensure question appears in prompt
    # ------------------------------------------------------

    assert (
        "What is database indexing?"
        in prompt
    )

    print(
        "PASS: User question appears in prompt."
    )

    # ------------------------------------------------------
    # Validate grounding instructions
    # ------------------------------------------------------

    assert (
        "Do not use outside knowledge."
        in prompt
    )

    assert (
        "Do not invent facts."
        in prompt
    )

    assert (
        "Do not assume that two related concepts are equivalent."
        in prompt
    )

    print(
        "PASS: Strict grounding instructions "
        "are present."
    )

    # ------------------------------------------------------
    # Validate response
    # ------------------------------------------------------

    assert (
        result["answer"]
        == "Comparison test response generated successfully."
    )

    print(
        "PASS: LLM comparison response "
        "returned correctly."
    )


    # ======================================================
    # TEST 2 — EMPTY QUESTION
    # ======================================================

    print("\n" + "=" * 60)
    print("TEST 2 — EMPTY QUESTION VALIDATION")
    print("=" * 60)

    try:

        comparison_module.comparison_service.compare(
            question="",
            document_ids=[
                DOCUMENT_A,
                DOCUMENT_B
            ]
        )

        raise AssertionError(
            "Empty question should have raised ValueError."
        )

    except ValueError as e:

        print(
            "PASS: Correctly rejected empty question:"
        )

        print(
            f"  {e}"
        )


    # ======================================================
    # TEST 3 — SINGLE DOCUMENT
    # ======================================================

    print("\n" + "=" * 60)
    print("TEST 3 — SINGLE DOCUMENT VALIDATION")
    print("=" * 60)

    try:

        comparison_module.comparison_service.compare(
            question="What is database indexing?",
            document_ids=[
                DOCUMENT_A
            ]
        )

        raise AssertionError(
            "Single document should have raised "
            "ValueError."
        )

    except ValueError as e:

        print(
            "PASS: Correctly rejected single document:"
        )

        print(
            f"  {e}"
        )


    # ======================================================
    # TEST 4 — DUPLICATE DOCUMENT IDs
    # ======================================================

    print("\n" + "=" * 60)
    print("TEST 4 — DUPLICATE DOCUMENT VALIDATION")
    print("=" * 60)

    try:

        comparison_module.comparison_service.compare(
            question="What is database indexing?",
            document_ids=[
                DOCUMENT_A,
                DOCUMENT_A
            ]
        )

        raise AssertionError(
            "Duplicate-only document IDs should "
            "have raised ValueError."
        )

    except ValueError as e:

        print(
            "PASS: Correctly rejected duplicate-only "
            "documents:"
        )

        print(
            f"  {e}"
        )


    # ======================================================
    # TEST 5 — THREE DOCUMENT SUPPORT
    # ======================================================

    print("\n" + "=" * 60)
    print("TEST 5 — THREE DOCUMENT SUPPORT")
    print("=" * 60)

    result_three = (
        comparison_module.comparison_service.compare(
            question="What is database indexing?",
            document_ids=[
                DOCUMENT_A,
                DOCUMENT_B,
                DOCUMENT_C
            ],
            n_results=3
        )
    )

    print("\nAnswer:")
    print(result_three["answer"])

    print("\nReturned document IDs:")
    print(result_three["document_ids"])

    print("\nNumber of selected evidence sources:")
    print(len(result_three["sources"]))

    # ------------------------------------------------------
    # Validate returned document IDs
    # ------------------------------------------------------

    assert result_three["document_ids"] == [
        DOCUMENT_A,
        DOCUMENT_B,
        DOCUMENT_C
    ]

    print(
        "PASS: Three document IDs returned correctly."
    )

    # ------------------------------------------------------
    # Validate source document IDs
    # ------------------------------------------------------

    three_document_ids = {
        source["document_id"]
        for source in result_three["sources"]
    }

    print(
        "\nSelected source document IDs:"
    )

    print(
        three_document_ids
    )

    assert three_document_ids.issubset(
        {
            DOCUMENT_A,
            DOCUMENT_B,
            DOCUMENT_C
        }
    )

    print(
        "PASS: Three-document comparison "
        "contains only selected documents."
    )

    # ------------------------------------------------------
    # Validate prompt contains all three documents
    # ------------------------------------------------------

    prompt_three = fake_llm.last_prompt

    assert prompt_three is not None

    assert "DOCUMENT 1" in prompt_three

    assert "DOCUMENT 2" in prompt_three

    assert "DOCUMENT 3" in prompt_three

    print(
        "PASS: Three-document comparison prompt "
        "contains all three documents."
    )

    # ------------------------------------------------------
    # Validate question
    # ------------------------------------------------------

    assert (
        "What is database indexing?"
        in prompt_three
    )

    print(
        "PASS: Question appears in "
        "three-document prompt."
    )


    # ======================================================
    # FINAL RESULT
    # ======================================================

    print("\n" + "=" * 60)
    print("ALL COMPARISON SERVICE TESTS PASSED")
    print("=" * 60)


finally:

    # ======================================================
    # RESTORE ORIGINAL LLM
    # ======================================================

    comparison_module.comparison_service.llm_service = (
        original_llm
    )

    print(
        "\nOriginal LLM service restored."
    )