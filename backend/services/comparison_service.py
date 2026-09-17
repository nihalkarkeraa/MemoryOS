from services.hybrid_retrieval_service import (
    hybrid_retrieval_service
)

from services.llm_service import (
    llm_service
)


class ComparisonService:
    """
    Service responsible for comparing information
    retrieved from two or more selected documents.

    The service reuses the existing:
        Hybrid Retrieval
        Cross-Encoder Reranker
        Ollama LLM

    Comparison is strictly grounded in retrieved evidence.

    Evidence selection:
        Each document is retrieved independently.
        Weak candidates are filtered relative to the
        strongest reranked result from that document.

    This prevents the LLM from receiving large amounts of
    unrelated material when a document does not contain
    sufficient evidence for the question.
    """

    # Number of candidates retrieved before evidence filtering.
    RETRIEVAL_CANDIDATES = 5

    # Maximum number of evidence chunks passed to the LLM
    # from each document.
    MAX_EVIDENCE_PER_DOCUMENT = 2

    # Maximum allowed drop from the best reranker score
    # when deciding whether another result is relevant.
    #
    # Example:
    #
    # Best score = -2.8
    # Another score = -3.5
    # Difference = 0.7
    #
    # Since 0.7 <= 2.0, the second result is retained.
    #
    # A result far below the best candidate is discarded.
    RERANKER_SCORE_MARGIN = 2.0

    def __init__(self):

        self.hybrid_retrieval_service = (
            hybrid_retrieval_service
        )

        self.llm_service = (
            llm_service
        )

    # ======================================================
    # VALIDATE INPUT
    # ======================================================

    def _validate_input(
        self,
        question,
        document_ids
    ):
        """
        Validate the comparison request.
        """

        if not isinstance(
            question,
            str
        ):
            raise ValueError(
                "Question must be a string."
            )

        question = question.strip()

        if not question:
            raise ValueError(
                "Question cannot be empty."
            )

        if not document_ids:
            raise ValueError(
                "At least two document IDs are required."
            )

        if not isinstance(
            document_ids,
            list
        ):
            raise ValueError(
                "document_ids must be a list."
            )

        if len(document_ids) < 2:
            raise ValueError(
                "Comparison requires at least two documents."
            )

        cleaned_ids = []

        for document_id in document_ids:

            if not isinstance(
                document_id,
                str
            ):
                raise ValueError(
                    "Every document ID must be a string."
                )

            document_id = document_id.strip()

            if not document_id:
                raise ValueError(
                    "Document IDs cannot be empty."
                )

            if document_id not in cleaned_ids:
                cleaned_ids.append(
                    document_id
                )

        if len(cleaned_ids) < 2:
            raise ValueError(
                "Comparison requires at least two unique documents."
            )

        return (
            question,
            cleaned_ids
        )

    # ======================================================
    # RETRIEVE DOCUMENT CANDIDATES
    # ======================================================

    def _retrieve_document_context(
        self,
        question,
        document_id,
        n_results=None
    ):
        """
        Retrieve candidate chunks from exactly one document.

        Retrieval remains independent for every document.
        """

        if n_results is None:
            n_results = (
                self.RETRIEVAL_CANDIDATES
            )

        results = (
            self.hybrid_retrieval_service.search(
                query=question,
                n_results=n_results,
                document_ids=[
                    document_id
                ]
            )
        )

        return results

    # ======================================================
    # GET RERANKER SCORE
    # ======================================================

    def _get_reranker_score(
        self,
        result
    ):
        """
        Safely retrieve the cross-encoder reranker score.
        """

        score = result.get(
            "reranker_score"
        )

        if isinstance(
            score,
            (int, float)
        ):
            return float(score)

        return None

    # ======================================================
    # FILTER EVIDENCE
    # ======================================================

    def _filter_evidence(
        self,
        results
    ):
        """
        Select the strongest evidence from one document.

        Strategy:

        1. If no results exist, return [].
        2. Sort candidates by reranker score.
        3. Always retain the strongest candidate.
        4. Retain additional candidates only when their
           score is within RERANKER_SCORE_MARGIN of the
           strongest candidate.
        5. Limit the final evidence to
           MAX_EVIDENCE_PER_DOCUMENT.

        This is a relative filtering strategy rather than
        an absolute score threshold because cross-encoder
        scores are not probabilities.
        """

        if not results:
            return []

        # --------------------------------------------------
        # Separate candidates with and without scores
        # --------------------------------------------------

        scored_results = []

        unscored_results = []

        for result in results:

            score = (
                self._get_reranker_score(
                    result
                )
            )

            if score is None:

                unscored_results.append(
                    result
                )

            else:

                scored_results.append(
                    (
                        score,
                        result
                    )
                )

        # --------------------------------------------------
        # If reranker scores are unavailable
        # --------------------------------------------------

        if not scored_results:

            return results[
                :self.MAX_EVIDENCE_PER_DOCUMENT
            ]

        # --------------------------------------------------
        # Sort strongest first
        # --------------------------------------------------

        scored_results.sort(
            key=lambda item: item[0],
            reverse=True
        )

        best_score = (
            scored_results[0][0]
        )

        selected = []

        # --------------------------------------------------
        # Select evidence close to best result
        # --------------------------------------------------

        for score, result in scored_results:

            score_difference = (
                best_score - score
            )

            if (
                score_difference
                <= self.RERANKER_SCORE_MARGIN
            ):

                selected.append(
                    result
                )

            if len(selected) >= (
                self.MAX_EVIDENCE_PER_DOCUMENT
            ):
                break

        # --------------------------------------------------
        # Guarantee at least one result
        # --------------------------------------------------

        if not selected:

            selected.append(
                scored_results[0][1]
            )

        # --------------------------------------------------
        # Fill remaining slots with unscored results
        # only if necessary.
        # --------------------------------------------------

        if len(selected) < (
            self.MAX_EVIDENCE_PER_DOCUMENT
        ):

            for result in unscored_results:

                if result not in selected:

                    selected.append(
                        result
                    )

                if len(selected) >= (
                    self.MAX_EVIDENCE_PER_DOCUMENT
                ):
                    break

        return selected

    # ======================================================
    # BUILD DOCUMENT CONTEXT
    # ======================================================

    def _build_document_context(
        self,
        results,
        document_id
    ):
        """
        Convert selected evidence chunks into a clearly
        labelled context block for the LLM.

        Full chunk text is retained.
        """

        if not results:

            return (
                "NO RELEVANT INFORMATION WAS RETRIEVED "
                "FROM THIS DOCUMENT."
            )

        context_parts = []

        for index, result in enumerate(
            results,
            start=1
        ):

            metadata = result.get(
                "metadata",
                {}
            )

            document_text = result.get(
                "document",
                ""
            )

            page_number = metadata.get(
                "page_number",
                "Unknown"
            )

            filename = metadata.get(
                "filename",
                "Unknown document"
            )

            result_document_id = metadata.get(
                "document_id",
                document_id
            )

            reranker_score = result.get(
                "reranker_score"
            )

            context_parts.append(
                f"""
[EVIDENCE {index}]
Document: {filename}
Document ID: {result_document_id}
Page: {page_number}
Reranker Score: {reranker_score}

Content:
{document_text}
"""
            )

        return "\n".join(
            context_parts
        )

    # ======================================================
    # BUILD COMPARISON PROMPT
    # ======================================================

    def _build_prompt(
        self,
        question,
        document_contexts
    ):
        """
        Build a concise, strictly grounded comparison prompt.
        """

        context_text = []

        for index, context in enumerate(
            document_contexts,
            start=1
        ):

            context_text.append(
                f"""
=== DOCUMENT {index} ===

{context}
"""
            )

        combined_context = "\n".join(
            context_text
        )

        prompt = f"""
You are MemoryOS, a source-grounded research assistant.

Answer the user's question using ONLY the retrieved evidence.

QUESTION:
{question}

RETRIEVED EVIDENCE:
{combined_context}

STRICT RULES:

1. Treat each document as an independent evidence source.

2. Never transfer a fact from one document to another.

3. Do not use outside knowledge.

4. Do not invent facts.

5. Do not assume that two related concepts are equivalent.

6. Only state a similarity if the supplied evidence supports
   that similarity.

7. Only state a difference if the supplied evidence supports
   that difference.

8. A database technology, schema, storage model, architecture,
   or other related concept must NOT be described as an
   indexing technique unless the evidence explicitly
   establishes that relationship.

9. If a document does not contain enough evidence, say:
   "The retrieved evidence from this document is insufficient
   to establish this."

10. Do not fill missing information using general knowledge.

11. Do not invent page numbers.

12. Every factual statement must be traceable to the supplied
    evidence.

13. If the documents do not provide enough evidence for a
    comparison, explicitly state that the comparison cannot
    be established from the retrieved evidence.

CITATION FORMAT:

[Document 1, Page X]
[Document 2, Page Y]

RESPONSE FORMAT:

Document 1:
- Relevant supported information.
- Citation.

Document 2:
- Relevant supported information.
- Citation.

Similarities:
- Only evidence-supported similarities.
- Citation(s).

Differences:
- Only evidence-supported differences.
- Citation(s).

Information not established:
- State what cannot be determined from the evidence.

Keep the answer concise, factual, and source-grounded.
"""

        return prompt

    # ======================================================
    # COMPARE DOCUMENTS
    # ======================================================

    def compare(
        self,
        question,
        document_ids,
        n_results=None
    ):
        """
        Compare information across two or more selected
        documents.

        Returns:

        {
            "question": ...,
            "document_ids": ...,
            "answer": ...,
            "sources": ...
        }
        """

        (
            question,
            document_ids
        ) = self._validate_input(
            question,
            document_ids
        )

        # --------------------------------------------------
        # Determine retrieval count
        # --------------------------------------------------

        if n_results is None:
            n_results = (
                self.RETRIEVAL_CANDIDATES
            )

        if not isinstance(
            n_results,
            int
        ):
            raise ValueError(
                "n_results must be an integer."
            )

        if n_results < 1:
            raise ValueError(
                "n_results must be at least 1."
            )

        # --------------------------------------------------
        # Retrieve and filter each document independently
        # --------------------------------------------------

        document_contexts = []

        all_sources = []

        for document_id in document_ids:

            candidates = (
                self._retrieve_document_context(
                    question=question,
                    document_id=document_id,
                    n_results=n_results
                )
            )

            selected_results = (
                self._filter_evidence(
                    candidates
                )
            )

            context = (
                self._build_document_context(
                    results=selected_results,
                    document_id=document_id
                )
            )

            document_contexts.append(
                context
            )

            # ------------------------------------------------
            # Store selected source metadata
            # ------------------------------------------------

            for result in selected_results:

                metadata = result.get(
                    "metadata",
                    {}
                )

                source = {
                    "document_id": (
                        metadata.get(
                            "document_id",
                            document_id
                        )
                    ),
                    "filename": (
                        metadata.get(
                            "filename",
                            "Unknown document"
                        )
                    ),
                    "page_number": (
                        metadata.get(
                            "page_number",
                            "Unknown"
                        )
                    ),
                    "chunk_id": (
                        result.get(
                            "chunk_id"
                        )
                    ),
                    "reranker_score": (
                        result.get(
                            "reranker_score"
                        )
                    ),
                    "hybrid_score": (
                        result.get(
                            "hybrid_score"
                        )
                    )
                }

                all_sources.append(
                    source
                )

        # --------------------------------------------------
        # Build comparison prompt
        # --------------------------------------------------

        prompt = self._build_prompt(
            question=question,
            document_contexts=document_contexts
        )

        # --------------------------------------------------
        # Generate comparison
        # --------------------------------------------------

        answer = (
            self.llm_service.generate(
                prompt
            )
        )

        # --------------------------------------------------
        # Return structured response
        # --------------------------------------------------

        return {
            "question": question,

            "document_ids": document_ids,

            "answer": answer,

            "sources": all_sources
        }


# ==========================================================
# SINGLETON
# ==========================================================

comparison_service = ComparisonService()