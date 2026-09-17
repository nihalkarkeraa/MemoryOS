
import tempfile
from pathlib import Path

from services.knowledge_graph_service import KnowledgeGraphService
from services.knowledge_graph_extraction_service import (
    KnowledgeGraphExtractionService,
)


def run_test():
    with tempfile.TemporaryDirectory() as temp_dir:
        graph_path = Path(temp_dir) / "real_graph.json"

        graph_service = KnowledgeGraphService(
            storage_path=str(graph_path)
        )

        extraction_service = KnowledgeGraphExtractionService(
            graph_service=graph_service,
            model="phi3:mini",
            timeout=300,
        )

        text = (
            "A database index improves query performance by "
            "allowing the database to find records more efficiently. "
            "A B-tree is a common data structure used to implement "
            "database indexes."
        )

        result = extraction_service.extract_from_text(
            text=text,
            document_id="real-test-document",
            page_number=1,
        )

        print("\n--- Extraction Result ---")
        print("Concepts:", result["concepts_extracted"])
        print("Relationships:", result["relationships_extracted"])

        print("\n--- Concepts ---")
        for concept in result["graph"]["nodes"]:
            print(
                f"- {concept['name']} "
                f"({concept['id']})"
            )

        print("\n--- Relationships ---")
        for edge in result["graph"]["edges"]:
            print(
                f"- {edge['source_id']} "
                f"--[{edge['relationship']}]--> "
                f"{edge['target_id']}"
            )

        assert result["concepts_saved"] >= 1

        print("\nReal Ollama Knowledge Graph extraction passed.")


if __name__ == "__main__":
    run_test()