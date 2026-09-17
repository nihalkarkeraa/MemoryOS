from fastapi.testclient import TestClient

import main


# ==========================================================
# TEST DATA
# ==========================================================

DOCUMENT_ID_A = (
    "c3fe9b40-a3a0-47f5-9327-f93d95d5d6a0"
)

DOCUMENT_ID_B = (
    "91d63ac4-d6c9-47cb-a20c-a65a61bac8d3"
)


# ==========================================================
# FAKE SERVICES
# ==========================================================


class FakeRegistryService:
    """
    Fake document registry used only for API tests.

    This prevents the test from depending on the current
    registry state.
    """

    def __init__(self):

        self.documents = {
            DOCUMENT_ID_A: {
                "document_id": DOCUMENT_ID_A,
                "filename": "test.pdf",
                "stored_filename": (
                    f"{DOCUMENT_ID_A}.pdf"
                ),
                "file_type": "pdf",
                "status": "processed"
            },

            DOCUMENT_ID_B: {
                "document_id": DOCUMENT_ID_B,
                "filename": "module4.pdf",
                "stored_filename": (
                    f"{DOCUMENT_ID_B}.pdf"
                ),
                "file_type": "pdf",
                "status": "processed"
            }
        }

    def list_documents(self):

        return list(
            self.documents.values()
        )

    def find_by_id(self, document_id):

        return self.documents.get(
            document_id
        )


class FakeChromaService:

    def count_document_chunks(
        self,
        document_id
    ):

        return 124


class FakeHybridRetrievalService:

    def search(
        self,
        query,
        n_results,
        document_ids=None
    ):

        return [
            {
                "document": (
                    "Database indexing improves "
                    "data retrieval performance."
                ),
                "metadata": {
                    "document_id": DOCUMENT_ID_A,
                    "filename": "test.pdf",
                    "page_number": 14
                },
                "chunk_id": (
                    f"{DOCUMENT_ID_A}_page_14_chunk_1"
                ),
                "hybrid_score": 0.82,
                "reranker_score": 5.21
            }
        ][:n_results]


class FakeRAGService:

    def answer(
        self,
        question,
        n_results,
        document_ids=None
    ):

        return {
            "question": question,
            "answer": (
                "Database indexing improves "
                "retrieval performance."
            ),
            "sources": [
                {
                    "document_id": DOCUMENT_ID_A,
                    "filename": "test.pdf",
                    "page_number": 14
                }
            ]
        }


class FakeSummarizationService:

    def summarize(
        self,
        text
    ):

        return {
            "summary": (
                "This is a test summary generated "
                "by the API test."
            )
        }


class FakeComparisonService:

    def compare(
        self,
        question,
        document_ids,
        n_results=None
    ):

        return {
            "question": question,
            "document_ids": document_ids,
            "answer": (
                "Document 1 and Document 2 "
                "contain different indexing-related "
                "information."
            ),
            "sources": [
                {
                    "document_id": DOCUMENT_ID_A,
                    "filename": "test.pdf",
                    "page_number": 14
                },
                {
                    "document_id": DOCUMENT_ID_B,
                    "filename": "module4.pdf",
                    "page_number": 35
                }
            ]
        }


# ==========================================================
# PATCH SERVICES
# ==========================================================


main.document_registry_service = (
    FakeRegistryService()
)

main.chroma_service = (
    FakeChromaService()
)

main.hybrid_retrieval_service = (
    FakeHybridRetrievalService()
)

main.rag_service = (
    FakeRAGService()
)

main.summarization_service = (
    FakeSummarizationService()
)

main.comparison_service = (
    FakeComparisonService()
)


client = TestClient(
    main.app
)


# ==========================================================
# HEALTH TEST
# ==========================================================


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert response.json() == {
        "status": "ok"
    }


# ==========================================================
# LIST DOCUMENTS TEST
# ==========================================================


def test_list_documents():

    response = client.get(
        "/documents"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_documents"] == 2

    assert len(
        data["documents"]
    ) == 2


# ==========================================================
# GET DOCUMENT TEST
# ==========================================================


def test_get_document():

    response = client.get(
        f"/documents/{DOCUMENT_ID_A}"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["document"]["document_id"]
        == DOCUMENT_ID_A
    )

    assert (
        data["storage"]["chroma_chunks"]
        == 124
    )


# ==========================================================
# GET UNKNOWN DOCUMENT
# ==========================================================


def test_get_unknown_document():

    response = client.get(
        "/documents/does-not-exist"
    )

    assert response.status_code == 404

    assert (
        response.json()["detail"]
        == "Document not found."
    )


# ==========================================================
# SEARCH TEST
# ==========================================================


def test_search():

    response = client.post(
        "/search",
        json={
            "query": "database indexing",
            "n_results": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["query"]
        == "database indexing"
    )

    assert data["total_results"] == 1

    result = data["results"][0]

    assert (
        result["document_id"]
        == DOCUMENT_ID_A
    )

    assert (
        result["filename"]
        == "test.pdf"
    )

    assert result["page_number"] == 14

    assert (
        "content"
        in result
    )

    assert (
        "hybrid_score"
        in result
    )

    assert (
        "reranker_score"
        in result
    )


# ==========================================================
# SEARCH EMPTY QUERY
# ==========================================================


def test_search_empty_query():

    response = client.post(
        "/search",
        json={
            "query": "",
            "n_results": 5
        }
    )

    assert response.status_code == 400


# ==========================================================
# SEARCH INVALID DOCUMENT
# ==========================================================


def test_search_invalid_document():

    response = client.post(
        "/search",
        json={
            "query": "database",
            "n_results": 5,
            "document_ids": [
                "does-not-exist"
            ]
        }
    )

    assert response.status_code == 404


# ==========================================================
# CHAT TEST
# ==========================================================


def test_chat():

    response = client.post(
        "/chat",
        json={
            "question": "What is indexing?",
            "n_results": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["question"]
        == "What is indexing?"
    )

    assert data["answer"]

    assert (
        "sources"
        in data
    )


# ==========================================================
# CHAT EMPTY QUESTION
# ==========================================================


def test_chat_empty_question():

    response = client.post(
        "/chat",
        json={
            "question": "",
            "n_results": 5
        }
    )

    assert response.status_code == 400


# ==========================================================
# SUMMARY TEST
# ==========================================================


def test_summary():

    response = client.post(
        f"/documents/{DOCUMENT_ID_A}/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["document_id"]
        == DOCUMENT_ID_A
    )

    assert (
        data["filename"]
        == "test.pdf"
    )

    assert data["summary"]


# ==========================================================
# SUMMARY UNKNOWN DOCUMENT
# ==========================================================


def test_summary_unknown_document():

    response = client.post(
        "/documents/does-not-exist/summary"
    )

    assert response.status_code == 404


# ==========================================================
# COMPARISON TEST
# ==========================================================


def test_compare():

    response = client.post(
        "/compare",
        json={
            "question": (
                "Compare indexing approaches."
            ),
            "document_ids": [
                DOCUMENT_ID_A,
                DOCUMENT_ID_B
            ],
            "n_results": 5
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["question"]
        == "Compare indexing approaches."
    )

    assert (
        data["document_ids"]
        == [
            DOCUMENT_ID_A,
            DOCUMENT_ID_B
        ]
    )

    assert data["answer"]

    assert (
        len(data["sources"])
        == 2
    )


# ==========================================================
# COMPARISON REQUIRES TWO DOCUMENTS
# ==========================================================


def test_compare_one_document():

    response = client.post(
        "/compare",
        json={
            "question": "Compare these.",
            "document_ids": [
                DOCUMENT_ID_A
            ],
            "n_results": 5
        }
    )

    assert response.status_code == 400


# ==========================================================
# COMPARISON UNKNOWN DOCUMENT
# ==========================================================


def test_compare_unknown_document():

    response = client.post(
        "/compare",
        json={
            "question": "Compare these.",
            "document_ids": [
                DOCUMENT_ID_A,
                "does-not-exist"
            ],
            "n_results": 5
        }
    )

    assert response.status_code == 404


# ==========================================================
# INVALID N_RESULTS
# ==========================================================


def test_search_invalid_n_results():

    response = client.post(
        "/search",
        json={
            "query": "database",
            "n_results": 0
        }
    )

    assert response.status_code == 400


# ==========================================================
# RUN TESTS
# ==========================================================


if __name__ == "__main__":

    import pytest

    raise SystemExit(
        pytest.main(
            [
                __file__,
                "-v"
            ]
        )
    )