import math
import re
from collections import Counter

from services.chroma_service import chroma_service


class KeywordSearchService:

    STOP_WORDS = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "can",
        "do",
        "does",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "was",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }

    def __init__(self):
        self.collection = chroma_service.collection

    def _tokenize(self, text: str):
        """
        Convert text into normalized keyword tokens.
        """

        words = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower()
        )

        return [
            word
            for word in words
            if word not in self.STOP_WORDS
        ]

    def _calculate_document_frequency(
        self,
        documents
    ):
        """
        Calculate how many documents contain each word.
        """

        document_frequency = Counter()

        for document in documents:

            unique_words = set(
                self._tokenize(document)
            )

            for word in unique_words:
                document_frequency[word] += 1

        return document_frequency

    def _calculate_idf(
        self,
        word,
        total_documents,
        document_frequency
    ):
        """
        Calculate inverse document frequency.

        Rare terms receive higher weights.
        Common terms receive lower weights.
        """

        frequency = document_frequency.get(
            word,
            0
        )

        return math.log(
            (1 + total_documents)
            / (1 + frequency)
        ) + 1

    def search(
        self,
        query: str,
        n_results: int = 5,
        document_ids=None
    ):
        """
        Search stored document chunks using
        weighted keyword matching.

        If document_ids is None, search all documents.

        If document_ids is supplied, search only
        chunks belonging to those documents.
        """

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return []

        # --------------------------------------------------
        # Retrieve stored chunks
        # --------------------------------------------------

        if document_ids:

            results = self.collection.get(
                where={
                    "document_id": {
                        "$in": document_ids
                    }
                },
                include=[
                    "documents",
                    "metadatas"
                ]
            )

        else:

            results = self.collection.get(
                include=[
                    "documents",
                    "metadatas"
                ]
            )

        documents = results.get(
            "documents",
            []
        )

        metadatas = results.get(
            "metadatas",
            []
        )

        ids = results.get(
            "ids",
            []
        )

        if not documents:
            return []

        # Calculate document frequency.
        document_frequency = (
            self._calculate_document_frequency(
                documents
            )
        )

        total_documents = len(documents)

        query_counter = Counter(
            query_tokens
        )

        scored_results = []

        for index, document in enumerate(documents):

            document_tokens = self._tokenize(
                document
            )

            document_counter = Counter(
                document_tokens
            )

            if not document_tokens:
                continue

            score = 0.0
            matched_words = []

            # Weighted keyword matching.
            for word in query_counter:

                if word not in document_counter:
                    continue

                matched_words.append(word)

                idf = self._calculate_idf(
                    word,
                    total_documents,
                    document_frequency
                )

                # Term-frequency component.
                term_frequency = (
                    document_counter[word]
                    / len(document_tokens)
                )

                # Give exact keyword occurrences
                # a useful but controlled contribution.
                score += (
                    idf
                    * (1 + math.log(
                        1 + document_counter[word]
                    ))
                )

                # Slightly reward documents where
                # the query term occurs frequently.
                score += term_frequency

            if not matched_words:
                continue

            # Exact phrase bonus.
            normalized_query = " ".join(
                query_tokens
            )

            normalized_document = " ".join(
                document_tokens
            )

            if normalized_query in normalized_document:
                score += 2.0

            # Full query coverage bonus.
            coverage = (
                len(set(matched_words))
                / len(set(query_tokens))
            )

            score += coverage

            scored_results.append(
                {
                    "chunk_id": ids[index],
                    "document": document,
                    "metadata": metadatas[index],
                    "keyword_score": score,
                    "matched_words": sorted(
                        set(matched_words)
                    ),
                    "query_coverage": coverage
                }
            )

        # Highest score first.
        scored_results.sort(
            key=lambda item: item["keyword_score"],
            reverse=True
        )

        return scored_results[:n_results]


keyword_search_service = KeywordSearchService()