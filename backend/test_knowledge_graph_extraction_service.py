
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from services.knowledge_graph_service import KnowledgeGraphService
from services.knowledge_graph_extraction_service import (
    KnowledgeGraphExtractionService,
)


def run_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "graph.json"

        graph_service = KnowledgeGraphService(
            storage_path=str(storage_path)
        )

        extraction_service = KnowledgeGraphExtractionService(
            graph_service=graph_service
        )

        mock_model_output = {
            "concepts": [
                {
                    "id": "database_index",
                    "name": "Database Index",
                    "type": "database_concept",
                    "description": (
                        "A structure used to speed up data retrieval."
                    ),
                },
                {
                    "id": "query_performance",
                    "name": "Query Performance",
                    "type": "database_concept",
                    "description": (
                        "The efficiency of executing database queries."
                    ),
                },
            ],
            "relationships": [
                {
                    "source_id": "database_index",
                    "target_id": "query_performance",
                    "relationship": "improves",
                    "confidence": 0.95,
                }
            ],
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "response": json.dumps(mock_model_output)
        }
        mock_response.raise_for_status.return_value = None

        with patch(
            "services.knowledge_graph_extraction_service.requests.post",
            return_value=mock_response,
        ) as mocked_post:

            result = extraction_service.extract_from_text(
                text=(
                    "A database index can improve query performance."
                ),
                document_id="test-document",
                page_number=3,
            )

            assert mocked_post.called

        assert result["concepts_extracted"] == 2
        assert result["relationships_extracted"] == 1
        assert result["concepts_saved"] == 2
        assert result["relationships_saved"] == 1

        graph_data = graph_service.get_graph()

        assert graph_data["node_count"] == 2
        assert graph_data["edge_count"] == 1

        concept = graph_service.get_concept("database_index")

        assert concept is not None
        assert concept["name"] == "Database Index"

        assert concept["provenance"][0]["document_id"] == (
            "test-document"
        )
        assert concept["provenance"][0]["page_number"] == 3

        relationship = graph_data["edges"][0]

        assert relationship["relationship"] == "improves"
        assert relationship["confidence"] == 0.95

        assert relationship["provenance"][0]["document_id"] == (
            "test-document"
        )

        print("Knowledge Graph extraction tests passed.")


if __name__ == "__main__":
    run_test()