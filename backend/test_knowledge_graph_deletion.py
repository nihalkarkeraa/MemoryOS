
from services.knowledge_graph_service import KnowledgeGraphService


def make_service(tmp_path):
    return KnowledgeGraphService(
        storage_path=str(tmp_path / "graph.json")
    )


def add_source(service, concept_id, name, document_id):
    service.add_concept(
        concept_id=concept_id,
        name=name,
        provenance={
            "source": {
                "document_id": document_id,
                "page_number": 1,
            }
        },
    )


def test_delete_document_removes_its_unique_concept(tmp_path):
    service = make_service(tmp_path)

    add_source(
        service,
        "unique_concept",
        "Unique Concept",
        "doc_a",
    )

    result = service.delete_document_provenance("doc_a")

    assert result["node_provenance_removed"] == 1
    assert result["nodes_removed"] == 1
    assert service.get_concept("unique_concept") is None


def test_shared_concept_keeps_other_document_provenance(tmp_path):
    service = make_service(tmp_path)

    add_source(
        service,
        "database_index",
        "Database Index",
        "doc_a",
    )
    add_source(
        service,
        "database_index",
        "Database Index",
        "doc_b",
    )

    result = service.delete_document_provenance("doc_a")

    concept = service.get_concept("database_index")

    assert result["node_provenance_removed"] == 1
    assert result["nodes_removed"] == 0
    assert concept is not None
    assert concept["provenance"] == [
        {
            "document_id": "doc_b",
            "page_number": 1,
        }
    ]


def test_relationship_is_removed_only_after_last_source(tmp_path):
    service = make_service(tmp_path)

    add_source(service, "index", "Index", "doc_a")
    add_source(service, "index", "Index", "doc_b")
    add_source(service, "performance", "Performance", "doc_a")
    add_source(service, "performance", "Performance", "doc_b")

    service.add_relationship(
        source_id="index",
        target_id="performance",
        relationship="improves",
        provenance={
            "source": {
                "document_id": "doc_a",
                "page_number": 1,
            }
        },
        confidence=0.9,
    )
    service.add_relationship(
        source_id="index",
        target_id="performance",
        relationship="improves",
        provenance={
            "source": {
                "document_id": "doc_b",
                "page_number": 2,
            }
        },
        confidence=0.9,
    )

    service.delete_document_provenance("doc_a")

    graph = service.get_graph()

    assert graph["edge_count"] == 1
    assert graph["edges"][0]["provenance"] == [
        {
            "document_id": "doc_b",
            "page_number": 2,
        }
    ]


def test_delete_document_removes_orphaned_relationship_and_nodes(tmp_path):
    service = make_service(tmp_path)

    add_source(service, "a", "Concept A", "doc_a")
    add_source(service, "b", "Concept B", "doc_a")

    service.add_relationship(
        source_id="a",
        target_id="b",
        relationship="connects_to",
        provenance={
            "source": {
                "document_id": "doc_a",
                "page_number": 1,
            }
        },
    )

    result = service.delete_document_provenance("doc_a")

    graph = service.get_graph()

    assert result["edges_removed"] == 1
    assert result["nodes_removed"] == 2
    assert graph["node_count"] == 0
    assert graph["edge_count"] == 0


def test_delete_unknown_document_does_not_change_graph(tmp_path):
    service = make_service(tmp_path)

    add_source(service, "existing", "Existing", "doc_a")

    before = service.get_graph()
    result = service.delete_document_provenance("unknown_doc")
    after = service.get_graph()

    assert result["node_provenance_removed"] == 0
    assert result["edge_provenance_removed"] == 0
    assert result["edges_removed"] == 0
    assert result["nodes_removed"] == 0
    assert before == after


def test_provenance_cleanup_is_persisted(tmp_path):
    storage_path = tmp_path / "graph.json"
    service = KnowledgeGraphService(
        storage_path=str(storage_path)
    )

    add_source(service, "concept", "Concept", "doc_a")
    service.delete_document_provenance("doc_a")

    reloaded_service = KnowledgeGraphService(
        storage_path=str(storage_path)
    )

    assert reloaded_service.get_concept("concept") is None