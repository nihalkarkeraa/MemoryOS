from services.embedding_service import embedding_service
from services.chroma_service import chroma_service
from services.keyword_search_service import keyword_search_service

from sentence_transformers import CrossEncoder


class HybridRetrievalService:

    def __init__(self):

        self.embedding_service = embedding_service
        self.chroma_service = chroma_service
        self.keyword_search_service = keyword_search_service

        # --------------------------------------------------
        # Cross-Encoder Reranker
        # --------------------------------------------------

        print(
            "Loading cross-encoder reranker: "
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        self.reranker = CrossEncoder(
            "cross-encoder/ms-marco-MiniLM-L-6-v2"
        )

        print(
            "Cross-encoder reranker loaded successfully."
        )

    def _normalize_scores(
        self,
        scores
    ):
        """
        Normalize scores using min-max normalization.

        Returns values between 0 and 1.
        """

        if not scores:
            return []

        minimum = min(scores)
        maximum = max(scores)

        if maximum == minimum:

            return [
                1.0
                for _ in scores
            ]

        return [
            (score - minimum)
            / (maximum - minimum)
            for score in scores
        ]

    def _calculate_semantic_score(
        self,
        distance
    ):
        """
        Convert Chroma distance into a similarity score.

        Lower distance means greater similarity.
        """

        return 1 / (1 + distance)

    def _calculate_exact_match_bonus(
        self,
        query,
        document
    ):
        """
        Give additional weight when important query
        terms appear directly in the document.
        """

        query_tokens = (
            keyword_search_service._tokenize(
                query
            )
        )

        document_tokens = (
            keyword_search_service._tokenize(
                document
            )
        )

        if not query_tokens:
            return 0.0

        document_word_set = set(
            document_tokens
        )

        matched = [
            word
            for word in query_tokens
            if word in document_word_set
        ]

        if not matched:
            return 0.0

        coverage = (
            len(set(matched))
            / len(set(query_tokens))
        )

        # Strong bonus for exact important-term coverage.
        return coverage * 0.25

    def _calculate_lexical_evidence_bonus(
        self,
        semantic_score,
        keyword_score
    ):
        """
        Give a controlled bonus when keyword evidence
        is substantially stronger than semantic evidence.

        This helps exact technical terms that may not be
        represented strongly by the embedding model.

        Example:

        Semantic score = 0.0
        Keyword score  = 1.0

        receives a useful lexical bonus.

        But a result that already has strong semantic
        evidence does not receive this bonus.
        """

        if keyword_score < 0.80:
            return 0.0

        if keyword_score <= semantic_score:
            return 0.0

        evidence_gap = (
            keyword_score
            - semantic_score
        )

        # Keep the bonus controlled.
        return min(
            evidence_gap * 0.30,
            0.30
        )

    def _is_weak_result(
        self,
        result
    ):
        """
        Filter results that have neither meaningful
        semantic nor keyword evidence.
        """

        semantic_score = result[
            "semantic_score"
        ]

        keyword_score = result[
            "keyword_score"
        ]

        exact_bonus = result[
            "exact_match_bonus"
        ]

        lexical_bonus = result[
            "lexical_evidence_bonus"
        ]

        # Keep results if at least one meaningful
        # retrieval signal exists.
        if keyword_score > 0:
            return False

        if exact_bonus > 0:
            return False

        if lexical_bonus > 0:
            return False

        if semantic_score >= 0.20:
            return False

        return True

    def _remove_duplicate_pages(
        self,
        results,
        max_per_page=2
    ):
        """
        Prevent too many chunks from the same page
        from occupying the final context.

        Page identity includes document ID so that:

        Document A / Page 1

        and

        Document B / Page 1

        are treated as different pages.
        """

        page_counts = {}
        filtered_results = []

        for result in results:

            document_id = result[
                "metadata"
            ].get(
                "document_id"
            )

            page_number = result[
                "metadata"
            ]["page_number"]

            page_key = (
                document_id,
                page_number
            )

            current_count = page_counts.get(
                page_key,
                0
            )

            if current_count >= max_per_page:
                continue

            filtered_results.append(
                result
            )

            page_counts[page_key] = (
                current_count + 1
            )

        return filtered_results

    def _rerank_results(
        self,
        query,
        results,
        rerank_candidates=10
    ):
        """
        Rerank the strongest hybrid candidates using
        a cross-encoder.

        The cross-encoder evaluates the question and
        document passage together.

        This is a second-stage reranker and does not
        replace semantic or keyword retrieval.
        """

        if not results:
            return []

        # Only rerank the strongest hybrid candidates.
        candidates = results[
            :rerank_candidates
        ]

        if not candidates:
            return []

        pairs = [
            (
                query,
                result["document"]
            )
            for result in candidates
        ]

        reranker_scores = self.reranker.predict(
            pairs
        )

        for index, result in enumerate(
            candidates
        ):

            result[
                "reranker_score"
            ] = float(
                reranker_scores[index]
            )

        # Higher cross-encoder score means greater
        # question-passage relevance.
        candidates.sort(
            key=lambda item: item[
                "reranker_score"
            ],
            reverse=True
        )

        return candidates

    def search(
        self,
        query: str,
        n_results: int = 5,
        semantic_results: int = 15,
        keyword_results: int = 15,
        semantic_weight: float = 0.45,
        keyword_weight: float = 0.35,
        exact_match_weight: float = 0.20,
        document_ids=None,
        rerank_candidates: int = 10
    ):
        """
        Perform hybrid retrieval using:

        - Semantic similarity
        - Weighted keyword matching
        - Exact query-term matching
        - Lexical evidence boosting
        - Relevance filtering
        - Page-level diversity
        - Cross-encoder reranking

        If document_ids is None, search all documents.

        If document_ids is supplied, search only
        those documents.
        """

        # --------------------------------------------------
        # 1. Generate query embedding
        # --------------------------------------------------

        query_embedding = (
            self.embedding_service.embed_text(
                query
            )
        )

        # --------------------------------------------------
        # 2. Semantic retrieval
        # --------------------------------------------------

        semantic_data = (
            self.chroma_service.search(
                query_embedding=query_embedding,
                n_results=semantic_results,
                document_ids=document_ids
            )
        )

        semantic_ids = (
            semantic_data["ids"][0]
        )

        semantic_documents = (
            semantic_data["documents"][0]
        )

        semantic_metadatas = (
            semantic_data["metadatas"][0]
        )

        semantic_distances = (
            semantic_data["distances"][0]
        )

        semantic_raw_scores = [
            self._calculate_semantic_score(
                distance
            )
            for distance in semantic_distances
        ]

        semantic_results_map = {}

        for index, chunk_id in enumerate(
            semantic_ids
        ):

            semantic_results_map[chunk_id] = {
                "chunk_id": chunk_id,
                "document": semantic_documents[index],
                "metadata": semantic_metadatas[index],
                "semantic_raw_score": (
                    semantic_raw_scores[index]
                ),
                "semantic_distance": (
                    semantic_distances[index]
                )
            }

        # --------------------------------------------------
        # 3. Keyword retrieval
        # --------------------------------------------------

        keyword_data = (
            self.keyword_search_service.search(
                query=query,
                n_results=keyword_results,
                document_ids=document_ids
            )
        )

        keyword_raw_scores = [
            result["keyword_score"]
            for result in keyword_data
        ]

        normalized_keyword_scores = (
            self._normalize_scores(
                keyword_raw_scores
            )
        )

        keyword_results_map = {}

        for index, result in enumerate(
            keyword_data
        ):

            chunk_id = result[
                "chunk_id"
            ]

            keyword_results_map[chunk_id] = {
                "chunk_id": chunk_id,
                "document": result["document"],
                "metadata": result["metadata"],
                "keyword_score": (
                    normalized_keyword_scores[index]
                ),
                "keyword_raw_score": (
                    result["keyword_score"]
                ),
                "matched_words": (
                    result["matched_words"]
                ),
                "query_coverage": (
                    result["query_coverage"]
                )
            }

        # --------------------------------------------------
        # 4. Normalize semantic scores
        # --------------------------------------------------

        semantic_score_values = [
            result["semantic_raw_score"]
            for result in semantic_results_map.values()
        ]

        normalized_semantic_scores = (
            self._normalize_scores(
                semantic_score_values
            )
        )

        semantic_score_lookup = {}

        semantic_result_list = list(
            semantic_results_map.values()
        )

        for index, result in enumerate(
            semantic_result_list
        ):

            semantic_score_lookup[
                result["chunk_id"]
            ] = normalized_semantic_scores[index]

        # --------------------------------------------------
        # 5. Combine candidates
        # --------------------------------------------------

        candidate_ids = set(
            semantic_results_map.keys()
        ).union(
            keyword_results_map.keys()
        )

        combined_results = []

        for chunk_id in candidate_ids:

            semantic_result = (
                semantic_results_map.get(
                    chunk_id
                )
            )

            keyword_result = (
                keyword_results_map.get(
                    chunk_id
                )
            )

            if semantic_result:

                document = (
                    semantic_result["document"]
                )

                metadata = (
                    semantic_result["metadata"]
                )

                semantic_score = (
                    semantic_score_lookup[
                        chunk_id
                    ]
                )

                semantic_distance = (
                    semantic_result[
                        "semantic_distance"
                    ]
                )

            else:

                document = (
                    keyword_result["document"]
                )

                metadata = (
                    keyword_result["metadata"]
                )

                semantic_score = 0.0
                semantic_distance = None

            if keyword_result:

                keyword_score = (
                    keyword_result[
                        "keyword_score"
                    ]
                )

                matched_words = (
                    keyword_result[
                        "matched_words"
                    ]
                )

                query_coverage = (
                    keyword_result[
                        "query_coverage"
                    ]
                )

            else:

                keyword_score = 0.0
                matched_words = []
                query_coverage = 0.0

            # --------------------------------------------------
            # 6. Exact match bonus
            # --------------------------------------------------

            exact_match_bonus = (
                self._calculate_exact_match_bonus(
                    query=query,
                    document=document
                )
            )

            # --------------------------------------------------
            # 7. Lexical evidence bonus
            # --------------------------------------------------

            lexical_evidence_bonus = (
                self._calculate_lexical_evidence_bonus(
                    semantic_score=semantic_score,
                    keyword_score=keyword_score
                )
            )

            # --------------------------------------------------
            # 8. Calculate final hybrid score
            # --------------------------------------------------

            hybrid_score = (
                semantic_weight
                * semantic_score
                +
                keyword_weight
                * keyword_score
                +
                exact_match_weight
                * exact_match_bonus
                +
                lexical_evidence_bonus
            )

            result = {
                "chunk_id": chunk_id,
                "document": document,
                "metadata": metadata,
                "semantic_score": semantic_score,
                "semantic_distance": semantic_distance,
                "keyword_score": keyword_score,
                "matched_words": matched_words,
                "query_coverage": query_coverage,
                "exact_match_bonus": exact_match_bonus,
                "lexical_evidence_bonus": (
                    lexical_evidence_bonus
                ),
                "hybrid_score": hybrid_score
            }

            if self._is_weak_result(result):
                continue

            combined_results.append(
                result
            )

        # --------------------------------------------------
        # 9. Sort by hybrid score
        # --------------------------------------------------

        combined_results.sort(
            key=lambda item: item[
                "hybrid_score"
            ],
            reverse=True
        )

        # --------------------------------------------------
        # 10. Cross-encoder reranking
        # --------------------------------------------------

        reranked_results = (
            self._rerank_results(
                query=query,
                results=combined_results,
                rerank_candidates=rerank_candidates
            )
        )

        # --------------------------------------------------
        # 11. Page-level diversity
        # --------------------------------------------------

        diverse_results = (
            self._remove_duplicate_pages(
                reranked_results,
                max_per_page=2
            )
        )

        # --------------------------------------------------
        # 12. Return final results
        # --------------------------------------------------

        return diverse_results[:n_results]


hybrid_retrieval_service = HybridRetrievalService() 