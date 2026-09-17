
import tempfile
from pathlib import Path

from services.knowledge_graph_service import KnowledgeGraphService


def run_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = Path(temp_dir) / "graph.json"

        service = KnowledgeGraphService(
            storage_path=str(storage_path)
        )

        # Add concepts
        service.add_concept(
            concept_id="database",
            name="Database",
            concept_type="technology",
            description="An organized collection of data.",
            provenance={
                "source": {
                    "document_id": "doc-1",
                    "page_number": 1,
                }
            },
        )

        service.add_concept(
            concept_id="indexing",
            name="Indexing",
            concept_type="concept",
            description="A technique used to speed up data retrieval.",
            provenance={
                "source": {
                    "document_id": "doc-1",
                    "page_number": 5,
                }
            },
        )

        # Add relationship
        service.add_relationship(
            source_id="indexing",
            target_id="database",
            relationship="used_in",
            provenance={
                "source": {
                    "document_id": "doc-1",
                    "page_number": 5,
                }
            },
            confidence=0.95,
        )

        # Verify graph
        graph_data = service.get_graph()

        assert graph_data["node_count"] == 2
        assert graph_data["edge_count"] == 1

        # Verify concept lookup
        indexing = service.get_concept("indexing")

        assert indexing is not None
        assert indexing["name"] == "Indexing"
        assert len(indexing["relationships"]) == 1

        # Verify neighbors
        neighbors = service.get_neighbors("indexing")

        assert len(neighbors) == 1
        assert neighbors[0]["id"] == "database"

        # Verify persistence
        loaded_service = KnowledgeGraphService(
            storage_path=str(storage_path)
        )

        loaded_graph = loaded_service.get_graph()

        assert loaded_graph["node_count"] == 2
        assert loaded_graph["edge_count"] == 1

        # Verify deletion
        deleted = loaded_service.delete_concept("indexing")

        assert deleted is True
        assert loaded_service.get_graph()["node_count"] == 1
        assert loaded_service.get_graph()["edge_count"] == 0

        print("Knowledge Graph service tests passed.")


if __name__ == "__main__":
    run_test()