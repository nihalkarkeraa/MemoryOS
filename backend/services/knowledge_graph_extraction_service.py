
import json
import re
from typing import Any

import requests

from services.knowledge_graph_service import KnowledgeGraphService


class KnowledgeGraphExtractionService:
    """
    Extract concepts and relationships from text using Ollama,
    validate the result, and store it in the MemoryOS graph.
    """

    def __init__(
        self,
        graph_service: KnowledgeGraphService | None = None,
        ollama_url: str = "http://127.0.0.1:11434/api/generate",
        model: str = "phi3:mini",
        timeout: int = 300,
    ):
        self.graph_service = (
            graph_service
            if graph_service is not None
            else KnowledgeGraphService()
        )

        self.ollama_url = ollama_url
        self.model = model
        self.timeout = timeout

    @staticmethod
    def _clean_json_response(response: str) -> str:
        """Remove optional Markdown code fences from model output."""

        response = response.strip()

        response = re.sub(
            r"^```(?:json)?\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        response = re.sub(r"\s*```$", "", response)

        return response.strip()

    @staticmethod
    def _validate_extraction(data: Any) -> dict[str, list]:
        """Validate the expected concepts and relationships structure."""

        if not isinstance(data, dict):
            raise ValueError("Model output must be a JSON object.")

        concepts = data.get("concepts", [])
        relationships = data.get("relationships", [])

        if not isinstance(concepts, list):
            raise ValueError("'concepts' must be a list.")

        if not isinstance(relationships, list):
            raise ValueError("'relationships' must be a list.")

        validated_concepts = []
        concept_ids = set()

        for concept in concepts:
            if not isinstance(concept, dict):
                raise ValueError("Each concept must be an object.")

            concept_id = concept.get("id")
            name = concept.get("name")
            concept_type = concept.get("type", "concept")
            description = concept.get("description", "")

            if not isinstance(concept_id, str) or not concept_id.strip():
                raise ValueError("Each concept needs a non-empty id.")

            if not isinstance(name, str) or not name.strip():
                raise ValueError("Each concept needs a non-empty name.")

            if not isinstance(concept_type, str):
                raise ValueError("Concept type must be a string.")

            if not isinstance(description, str):
                raise ValueError("Concept description must be a string.")

            concept_id = concept_id.strip()

            if concept_id in concept_ids:
                continue

            concept_ids.add(concept_id)

            validated_concepts.append({
                "id": concept_id,
                "name": name.strip(),
                "type": concept_type.strip() or "concept",
                "description": description.strip(),
            })

        validated_relationships = []

        for relationship in relationships:
            if not isinstance(relationship, dict):
                raise ValueError("Each relationship must be an object.")

            source_id = relationship.get("source_id")
            target_id = relationship.get("target_id")
            relation_type = relationship.get("relationship")

            if not isinstance(source_id, str) or not source_id.strip():
                raise ValueError(
                    "Each relationship needs a source_id."
                )

            if not isinstance(target_id, str) or not target_id.strip():
                raise ValueError(
                    "Each relationship needs a target_id."
                )

            if (
                not isinstance(relation_type, str)
                or not relation_type.strip()
            ):
                raise ValueError(
                    "Each relationship needs a relationship label."
                )

            source_id = source_id.strip()
            target_id = target_id.strip()

            if source_id not in concept_ids:
                raise ValueError(
                    f"Unknown relationship source: {source_id}"
                )

            if target_id not in concept_ids:
                raise ValueError(
                    f"Unknown relationship target: {target_id}"
                )

            confidence = relationship.get("confidence")

            if confidence is not None:
                if isinstance(confidence, bool) or not isinstance(
                    confidence, (int, float)
                ):
                    raise ValueError(
                        "Relationship confidence must be numeric."
                    )

                if not 0 <= confidence <= 1:
                    raise ValueError(
                        "Relationship confidence must be between 0 and 1."
                    )

            validated_relationships.append({
                "source_id": source_id,
                "target_id": target_id,
                "relationship": relation_type.strip(),
                "confidence": confidence,
            })

        return {
            "concepts": validated_concepts,
            "relationships": validated_relationships,
        }

    def _build_prompt(self, text: str) -> str:
        """Create a constrained extraction prompt."""

        return f"""
You are a knowledge graph extraction system.

Extract important concepts and explicit relationships from
the supplied text.

Rules:
1. Use only information supported by the text.
2. Do not invent concepts or relationships.
3. Keep concept names concise.
4. Use lowercase snake_case IDs, such as relational_database.
5. Use descriptive relationship labels, such as uses,
   contains, improves, or depends_on.
6. Only create relationships between extracted concepts.
7. Confidence must be a number between 0 and 1.
8. Return valid JSON only. Do not include Markdown fences.

Required JSON format:
{{
  "concepts": [
    {{
      "id": "concept_id",
      "name": "Concept Name",
      "type": "concept",
      "description": "Short text-supported description"
    }}
  ],
  "relationships": [
    {{
      "source_id": "concept_id",
      "target_id": "another_concept_id",
      "relationship": "relationship_label",
      "confidence": 0.9
    }}
  ]
}}

If no useful concepts or relationships are found, return:
{{
  "concepts": [],
  "relationships": []
}}

TEXT TO ANALYZE:
{text}
""".strip()

    def extract_from_text(
        self,
        text: str,
        document_id: str,
        page_number: int | None = None,
    ) -> dict[str, Any]:
        """
        Extract concepts from text and save them to the graph.

        Each saved concept and relationship retains document
        and page provenance.
        """

        if not isinstance(text, str) or not text.strip():
            raise ValueError("Text must be a non-empty string.")

        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("document_id must be a non-empty string.")

        if page_number is not None:
            if isinstance(page_number, bool) or not isinstance(
                page_number, int
            ):
                raise ValueError("page_number must be an integer.")

            if page_number < 1:
                raise ValueError("page_number must be at least 1.")

        prompt = self._build_prompt(text)

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
            },
        }

        try:
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

        except requests.RequestException as exc:
            raise RuntimeError(
                f"Could not connect to Ollama: {exc}"
            ) from exc

        try:
            response_data = response.json()
            model_output = response_data["response"]
        except (ValueError, KeyError, TypeError) as exc:
            raise RuntimeError(
                "Ollama returned an invalid response."
            ) from exc

        if not isinstance(model_output, str):
            raise RuntimeError("Ollama response content must be text.")

        cleaned_output = self._clean_json_response(model_output)

        try:
            parsed_output = json.loads(cleaned_output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "The model did not return valid JSON."
            ) from exc

        extracted = self._validate_extraction(parsed_output)

        provenance = {
            "document_id": document_id.strip(),
            "page_number": page_number,
        }

        saved_concepts = 0
        saved_relationships = 0

        # Save all concepts first so relationship endpoints exist.
        for concept in extracted["concepts"]:
            self.graph_service.add_concept(
                concept_id=concept["id"],
                name=concept["name"],
                concept_type=concept["type"],
                description=concept["description"],
                provenance={
                    "source": provenance,
                },
            )

            saved_concepts += 1

        # Save relationships only after concepts are created.
        for relationship in extracted["relationships"]:
            self.graph_service.add_relationship(
                source_id=relationship["source_id"],
                target_id=relationship["target_id"],
                relationship=relationship["relationship"],
                confidence=relationship["confidence"],
                provenance={
                    "source": provenance,
                },
            )

            saved_relationships += 1

        return {
            "document_id": document_id.strip(),
            "page_number": page_number,
            "concepts_extracted": len(extracted["concepts"]),
            "relationships_extracted": len(
                extracted["relationships"]
            ),
            "concepts_saved": saved_concepts,
            "relationships_saved": saved_relationships,
            "graph": self.graph_service.get_graph(),
        }