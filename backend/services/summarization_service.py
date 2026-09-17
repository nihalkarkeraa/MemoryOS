from services.llm_service import llm_service


class SummarizationService:
    """
    Service responsible for generating concise summaries
    from document content.

    The service uses the existing Ollama LLM service.
    It does not modify the existing RAG or retrieval pipeline.
    """

    def __init__(self):
        self.llm_service = llm_service

    # ======================================================
    # VALIDATE INPUT
    # ======================================================

    def _validate_input(self, text):
        """
        Validate document text before summarization.
        """

        if not isinstance(text, str):
            raise ValueError(
                "Text must be a string."
            )

        text = text.strip()

        if not text:
            raise ValueError(
                "Text cannot be empty."
            )

        return text

    # ======================================================
    # BUILD SUMMARY PROMPT
    # ======================================================

    def _build_prompt(self, text):
        """
        Build a grounded summarization prompt.

        The model is instructed to summarize only the
        supplied document content.
        """

        prompt = f"""
You are MemoryOS, a source-grounded research assistant.

Summarize the document content provided below.

DOCUMENT CONTENT:
{text}

STRICT RULES:

1. Use ONLY the information provided in the document content.

2. Do not use outside knowledge.

3. Do not invent facts.

4. Do not add information that is not present in the document.

5. Preserve the important technical terminology used in
   the document.

6. Focus on the main concepts, important explanations,
   techniques, definitions, and conclusions.

7. Remove unnecessary repetition.

8. If the document content does not provide enough
   information to summarize a topic, do not invent it.

RESPONSE FORMAT:

Overview:
Write a concise overview of the provided content.

Key Concepts:
- List the important concepts discussed.

Important Points:
- List the most important technical or factual points.

Keep the summary concise, clear, and faithful to the
provided document content.
"""

        return prompt

    # ======================================================
    # SUMMARIZE
    # ======================================================

    def summarize(self, text):
        """
        Generate a summary from supplied document content.

        Returns:

        {
            "summary": ...
        }
        """

        text = self._validate_input(
            text
        )

        prompt = self._build_prompt(
            text
        )

        answer = self.llm_service.generate(
            prompt
        )

        return {
            "summary": answer
        }


# ==========================================================
# SINGLETON
# ==========================================================

summarization_service = SummarizationService()