from services.hybrid_retrieval_service import (
    hybrid_retrieval_service
)

from services.llm_service import llm_service


class RAGService:

    def __init__(
        self,
        retrieval_service=None,
        llm=None
    ):
        self.retrieval_service = (
            retrieval_service
            or hybrid_retrieval_service
        )

        self.llm = (
            llm
            or llm_service
        )

    def _build_context(
        self,
        retrieval_results
    ):
        """
        Convert retrieved chunks into a structured
        context that can be given to the LLM.
        """

        context_parts = []

        for index, result in enumerate(
            retrieval_results,
            start=1
        ):

            metadata = result["metadata"]

            document_id = metadata[
                "document_id"
            ]

            page_number = metadata[
                "page_number"
            ]

            document_text = result[
                "document"
            ]

            context_part = (
                f"[Source {index}]\n"
                f"Document ID: {document_id}\n"
                f"Page: {page_number}\n"
                f"Content:\n"
                f"{document_text}"
            )

            context_parts.append(
                context_part
            )

        return "\n\n".join(
            context_parts
        )

    def _build_prompt(
        self,
        question,
        context
    ):
        """
        Build a grounded RAG prompt.

        The model is explicitly instructed to use
        only the retrieved context.
        """

        prompt = f"""
You are MemoryOS, a document-based AI research assistant.

Your job is to answer the user's question using ONLY
the information contained in the provided context.

Important rules:

1. Use only the provided context.
2. Do not invent facts that are not supported by the context.
3. If the context does not contain enough information
   to answer the question, clearly say that the available
   documents do not contain enough information.
4. Do not use outside knowledge.
5. Give a clear and concise answer.
6. When making a claim based on a source, include its
   source number in square brackets, such as [Source 1].
7. Do not create sources that are not present in the context.

Retrieved Context:

{context}

User Question:

{question}

Answer:
"""

        return prompt.strip()

    def answer(
        self,
        question: str,
        n_results: int = 5,
        document_ids=None
    ):
        """
        Complete RAG pipeline:

        Question
            ↓
        Hybrid Retrieval
            ↓
        Context Construction
            ↓
        Grounded Prompt
            ↓
        LLM
            ↓
        Answer + Citations

        If document_ids is None, all indexed documents
        can be searched.

        If document_ids is supplied, retrieval is restricted
        to those documents.
        """

        if not question or not question.strip():

            raise ValueError(
                "Question cannot be empty."
            )

        question = question.strip()

        # --------------------------------------------------
        # Validate document IDs
        # --------------------------------------------------

        if document_ids is not None:

            if not isinstance(
                document_ids,
                list
            ):

                raise ValueError(
                    "document_ids must be a list."
                )

            document_ids = [
                document_id
                for document_id in document_ids
                if isinstance(
                    document_id,
                    str
                )
                and document_id.strip()
            ]

            if not document_ids:

                raise ValueError(
                    "document_ids cannot be empty."
                )

        # --------------------------------------------------
        # 1. Retrieve relevant document chunks
        # --------------------------------------------------

        retrieval_results = (
            self.retrieval_service.search(
                query=question,
                n_results=n_results,
                document_ids=document_ids
            )
        )

        # --------------------------------------------------
        # 2. Handle no retrieval results
        # --------------------------------------------------

        if not retrieval_results:

            return {
                "question": question,
                "answer": (
                    "The available documents do not "
                    "contain enough information to answer "
                    "this question."
                ),
                "sources": []
            }

        # --------------------------------------------------
        # 3. Build context
        # --------------------------------------------------

        context = self._build_context(
            retrieval_results
        )

        # --------------------------------------------------
        # 4. Build grounded prompt
        # --------------------------------------------------

        prompt = self._build_prompt(
            question=question,
            context=context
        )

        # --------------------------------------------------
        # 5. Generate answer
        # --------------------------------------------------

        generated_answer = self.llm.generate(
            prompt=prompt,
            temperature=0.2
        )

        # --------------------------------------------------
        # 6. Build citation information
        # --------------------------------------------------

        sources = []

        for index, result in enumerate(
            retrieval_results,
            start=1
        ):

            metadata = result[
                "metadata"
            ]

            sources.append(
                {
                    "source_number": index,
                    "document_id": metadata[
                        "document_id"
                    ],
                    "page_number": metadata[
                        "page_number"
                    ],
                    "chunk_id": result[
                        "chunk_id"
                    ],
                    "hybrid_score": result[
                        "hybrid_score"
                    ]
                }
            )

        # --------------------------------------------------
        # 7. Return complete RAG response
        # --------------------------------------------------

        return {
            "question": question,
            "answer": generated_answer,
            "sources": sources
        }


rag_service = RAGService()