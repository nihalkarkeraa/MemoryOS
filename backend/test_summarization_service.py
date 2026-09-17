from services.summarization_service import (
    SummarizationService
)


class FakeLLMService:

    def generate(self, prompt):
        return (
            "Overview:\n"
            "This document discusses database systems.\n\n"
            "Key Concepts:\n"
            "- Database management\n"
            "- Data models\n\n"
            "Important Points:\n"
            "- Databases organize and manage data."
        )


def main():

    print("=" * 70)
    print("MemoryOS - Summarization Service Test")
    print("=" * 70)

    service = SummarizationService()

    # ------------------------------------------------------
    # Replace real LLM with fake LLM
    # ------------------------------------------------------

    service.llm_service = FakeLLMService()

    sample_text = """
    A database management system is software used to
    create, manage, and organize databases.

    Database systems provide mechanisms for storing,
    retrieving, updating, and managing data efficiently.

    Different data models can be used to represent
    relationships between data.
    """

    # ------------------------------------------------------
    # Test validation
    # ------------------------------------------------------

    print("\n[1] Testing input validation...")

    validated_text = service._validate_input(
        sample_text
    )

    assert validated_text == sample_text.strip()

    print("Input validation: PASSED")

    # ------------------------------------------------------
    # Test prompt generation
    # ------------------------------------------------------

    print("\n[2] Testing prompt generation...")

    prompt = service._build_prompt(
        validated_text
    )

    assert "DATABASE CONTENT" not in prompt
    assert "DOCUMENT CONTENT" in prompt
    assert "STRICT RULES" in prompt
    assert "Overview:" in prompt
    assert "Key Concepts:" in prompt
    assert "Important Points:" in prompt
    assert validated_text in prompt

    print("Prompt generation: PASSED")

    # ------------------------------------------------------
    # Test summarization
    # ------------------------------------------------------

    print("\n[3] Testing summarization...")

    result = service.summarize(
        sample_text
    )

    assert isinstance(
        result,
        dict
    )

    assert "summary" in result

    assert result["summary"]

    print("Summarization: PASSED")

    # ------------------------------------------------------
    # Test empty input
    # ------------------------------------------------------

    print("\n[4] Testing empty input...")

    try:

        service.summarize("")

        assert False, (
            "Expected ValueError for empty text."
        )

    except ValueError:

        print("Empty input validation: PASSED")

    # ------------------------------------------------------
    # Final result
    # ------------------------------------------------------

    print("\n" + "=" * 70)
    print("ALL SUMMARIZATION SERVICE TESTS PASSED")
    print("=" * 70)


if __name__ == "__main__":
    main()