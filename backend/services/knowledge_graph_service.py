
import json
from pathlib import Path
from typing import Any

import networkx as nx


class KnowledgeGraphService:
    """
    Local persistent knowledge graph for MemoryOS.

    Nodes represent concepts or entities.
    Edges represent relationships between them.

    Each node and relationship can retain document provenance.
    """

    def __init__(self, storage_path: str = "data/knowledge_graph/graph.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.graph = nx.MultiDiGraph()
        self.load()

    @staticmethod
    def _validate_text(value: str, field_name: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string.")

        return value.strip()

    @staticmethod
    def _validate_provenance(provenance: dict[str, Any] | None) -> dict[str, Any]:
        if provenance is None:
            return {}

        if not isinstance(provenance, dict):
            raise ValueError("Provenance must be a dictionary.")

        return provenance

    def add_concept(
        self,
        concept_id: str,
        name: str,
        concept_type: str = "concept",
        description: str = "",
        provenance: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Add a concept or update its metadata."""

        concept_id = self._validate_text(concept_id, "concept_id")
        name = self._validate_text(name, "name")
        concept_type = self._validate_text(concept_type, "concept_type")

        if not isinstance(description, str):
            raise ValueError("Description must be a string.")

        provenance = self._validate_provenance(provenance)

        if self.graph.has_node(concept_id):
            existing = self.graph.nodes[concept_id]

            existing_provenance = existing.get("provenance", [])
            if isinstance(existing_provenance, list):
                for item in provenance.values():
                    if item not in existing_provenance:
                        existing_provenance.append(item)
            else:
                existing_provenance = list(provenance.values())

            self.graph.nodes[concept_id].update({
                "name": name,
                "type": concept_type,
                "description": description or existing.get("description", ""),
                "provenance": existing_provenance,
            })

        else:
            self.graph.add_node(
                concept_id,
                name=name,
                type=concept_type,
                description=description,
                provenance=list(provenance.values()),
            )

        self.save()

        return self.get_concept(concept_id)

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        provenance: dict[str, Any] | None = None,
        confidence: float | None = None,
    ) -> dict[str, Any]:
        """Add a directed relationship between two existing concepts."""

        source_id = self._validate_text(source_id, "source_id")
        target_id = self._validate_text(target_id, "target_id")
        relationship = self._validate_text(relationship, "relationship")

        if not self.graph.has_node(source_id):
            raise ValueError(f"Source concept '{source_id}' does not exist.")

        if not self.graph.has_node(target_id):
            raise ValueError(f"Target concept '{target_id}' does not exist.")

        provenance = self._validate_provenance(provenance)

        if confidence is not None:
            if not isinstance(confidence, (int, float)):
                raise ValueError("Confidence must be a number.")

            if not 0 <= confidence <= 1:
                raise ValueError("Confidence must be between 0 and 1.")

        edge_key = self.graph.add_edge(
            source_id,
            target_id,
            relationship=relationship,
            provenance=list(provenance.values()),
            confidence=confidence,
        )

        self.save()

        return {
            "source_id": source_id,
            "target_id": target_id,
            "relationship": relationship,
            "edge_key": edge_key,
            "provenance": list(provenance.values()),
            "confidence": confidence,
        }

    def get_concept(self, concept_id: str) -> dict[str, Any] | None:
        """Return a concept and its direct relationships."""

        if not self.graph.has_node(concept_id):
            return None

        node_data = dict(self.graph.nodes[concept_id])

        relationships = []

        for _, target_id, edge_data in self.graph.out_edges(
            concept_id,
            data=True,
        ):
            relationships.append({
                "target_id": target_id,
                **edge_data,
            })

        node_data["id"] = concept_id
        node_data["relationships"] = relationships

        return node_data

    def get_graph(self) -> dict[str, Any]:
        """Return the complete graph in JSON-compatible form."""

        nodes = []

        for node_id, attributes in self.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                **attributes,
            })

        edges = []

        for source_id, target_id, edge_key, attributes in self.graph.edges(
            keys=True,
            data=True,
        ):
            edges.append({
                "source_id": source_id,
                "target_id": target_id,
                "edge_key": edge_key,
                **attributes,
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
        }

    def get_neighbors(self, concept_id: str) -> list[dict[str, Any]]:
        """Return concepts directly connected to the given concept."""

        if not self.graph.has_node(concept_id):
            return []

        neighbors = []

        for neighbor_id in self.graph.successors(concept_id):
            neighbors.append({
                "id": neighbor_id,
                **self.graph.nodes[neighbor_id],
            })

        for neighbor_id in self.graph.predecessors(concept_id):
            if neighbor_id == concept_id:
                continue

            if not any(item["id"] == neighbor_id for item in neighbors):
                neighbors.append({
                    "id": neighbor_id,
                    **self.graph.nodes[neighbor_id],
                })

        return neighbors

    def delete_concept(self, concept_id: str) -> bool:
        """Delete a concept and its connected relationships."""

        if not self.graph.has_node(concept_id):
            return False

        self.graph.remove_node(concept_id)
        self.save()

        return True

    def save(self) -> None:
        """Persist the graph to a JSON file."""

        graph_data = nx.node_link_data(
            self.graph,
            edges="edges",
        )

        with self.storage_path.open("w", encoding="utf-8") as file:
            json.dump(
                graph_data,
                file,
                ensure_ascii=False,
                indent=2,
            )

    def load(self) -> None:
        """Load the graph from disk, if a saved graph exists."""

        if not self.storage_path.exists():
            return

        with self.storage_path.open("r", encoding="utf-8") as file:
            graph_data = json.load(file)

        self.graph = nx.node_link_graph(
            graph_data,
            directed=True,
            multigraph=True,
            edges="edges",
        )


knowledge_graph_service = KnowledgeGraphService()