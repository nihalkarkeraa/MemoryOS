from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
import json
import os
import tempfile

from services.document_service import extract_text_from_pdf
from services.chunking_service import chunk_pages
from services.embedding_service import embedding_service
from services.chroma_service import chroma_service
from services.knowledge_graph_extraction_service import (
    KnowledgeGraphExtractionService,
)


class IngestionService:
    """PDF ingestion with persistent status for background graph extraction."""

    def __init__(
        self,
        embedding_service_instance=None,
        chroma_service_instance=None,
        graph_extraction_service_instance=None,
        max_graph_workers=1,
        status_dir="data/knowledge_graph_status",
    ):
        self.embedding_service = embedding_service_instance or embedding_service
        self.chroma_service = chroma_service_instance or chroma_service
        self.graph_extraction_service = (
            graph_extraction_service_instance
            or KnowledgeGraphExtractionService()
        )
        self.graph_executor = ThreadPoolExecutor(
            max_workers=max_graph_workers,
            thread_name_prefix="memoryos-graph",
        )
        self.status_dir = Path(status_dir)
        self.status_dir.mkdir(parents=True, exist_ok=True)
        self.graph_statuses = {}
        self.graph_status_lock = Lock()
        self._load_graph_statuses()

    def _status_path(self, document_id):
        safe_id = "".join(
            char for char in str(document_id)
            if char.isalnum() or char in ("-", "_")
        )
        if not safe_id:
            raise ValueError("Invalid document_id.")
        return self.status_dir / f"{safe_id}.json"

    def _write_status_record(self, document_id, status_data):
        path = self._status_path(document_id)
        record = {
            "document_id": document_id,
            "knowledge_graph": status_data,
        }
        fd, temp_path = tempfile.mkstemp(
            prefix=f"{path.stem}_",
            suffix=".tmp",
            dir=str(self.status_dir),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(record, handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_path, path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _load_graph_statuses(self):
        for path in self.status_dir.glob("*.json"):
            try:
                with path.open("r", encoding="utf-8") as handle:
                    record = json.load(handle)
                document_id = record.get("document_id")
                status = record.get("knowledge_graph")
                if not document_id or not isinstance(status, dict):
                    continue
                if status.get("status") in {"pending", "processing"}:
                    status = status.copy()
                    status["status"] = "interrupted"
                    status["message"] = (
                        "Backend restarted while this job was pending or "
                        "processing. The extraction was not automatically resumed."
                    )
                    self._write_status_record(document_id, status)
                self.graph_statuses[document_id] = status
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                # Keep a malformed status file from preventing API startup.
                continue

    def _set_graph_status(self, document_id, status_data):
        copied = status_data.copy()
        with self.graph_status_lock:
            self._write_status_record(document_id, copied)
            self.graph_statuses[document_id] = copied

    def get_graph_status(self, document_id):
        with self.graph_status_lock:
            status = self.graph_statuses.get(document_id)
            if status is not None:
                return status.copy()

            path = self._status_path(document_id)
            if not path.exists():
                return None
            try:
                with path.open("r", encoding="utf-8") as handle:
                    record = json.load(handle)
                status = record.get("knowledge_graph")
                if isinstance(status, dict):
                    self.graph_statuses[document_id] = status
                    return status.copy()
            except (OSError, json.JSONDecodeError, TypeError, ValueError):
                return None
        return None

    def _extract_knowledge_graph(self, pages, document_id):
        concepts = 0
        relationships = 0
        processed = 0
        errors = []
        text_pages = [
            page for page in pages
            if isinstance(page.get("text", ""), str)
            and page.get("text", "").strip()
        ]

        try:
            self._set_graph_status(document_id, {
                "status": "processing",
                "pages_processed": 0,
                "total_text_pages": len(text_pages),
                "concepts_extracted": 0,
                "relationships_extracted": 0,
                "errors": [],
            })

            for page in text_pages:
                page_number = page.get("page_number")
                try:
                    result = self.graph_extraction_service.extract_from_text(
                        text=page.get("text", ""),
                        document_id=document_id,
                        page_number=page_number,
                    ) or {}
                    concepts += int(result.get("concepts_extracted", 0) or 0)
                    relationships += int(
                        result.get("relationships_extracted", 0) or 0
                    )
                    processed += 1
                except Exception as error:
                    errors.append({
                        "page_number": page_number,
                        "error": str(error),
                    })

                self._set_graph_status(document_id, {
                    "status": "processing",
                    "pages_processed": processed,
                    "total_text_pages": len(text_pages),
                    "concepts_extracted": concepts,
                    "relationships_extracted": relationships,
                    "errors": errors.copy(),
                })

            final_status = (
                "completed" if not errors
                else "partial" if processed > 0
                else "failed"
            )
            self._set_graph_status(document_id, {
                "status": final_status,
                "pages_processed": processed,
                "total_text_pages": len(text_pages),
                "concepts_extracted": concepts,
                "relationships_extracted": relationships,
                "errors": errors,
            })
        except Exception as error:
            self._set_graph_status(document_id, {
                "status": "failed",
                "pages_processed": processed,
                "total_text_pages": len(text_pages),
                "concepts_extracted": concepts,
                "relationships_extracted": relationships,
                "errors": errors + [{"error": f"Graph worker failed: {error}"}],
            })

    def ingest_pdf(self, file_path: str, document_id: str):
        # 1. Extract PDF text
        pages = extract_text_from_pdf(file_path)

        # 2. Chunk the pages
        chunks = chunk_pages(pages=pages, document_id=document_id)

        # 3. Generate embeddings
        if chunks:
            texts = [chunk["text"] for chunk in chunks]
            embeddings = self.embedding_service.embed_texts(texts)
        else:
            embeddings = []

        # 4. Store chunks and embeddings
        if chunks:
            stored_count = self.chroma_service.add_chunks(
                chunks=chunks,
                embeddings=embeddings,
            )
        else:
            stored_count = 0

        total_text_pages = sum(
            1 for page in pages
            if isinstance(page.get("text", ""), str)
            and page.get("text", "").strip()
        )
        self._set_graph_status(document_id, {
            "status": "pending",
            "pages_processed": 0,
            "total_text_pages": total_text_pages,
            "concepts_extracted": 0,
            "relationships_extracted": 0,
            "errors": [],
        })

        try:
            self.graph_executor.submit(
                self._extract_knowledge_graph,
                pages,
                document_id,
            )
        except Exception as error:
            self._set_graph_status(document_id, {
                "status": "failed",
                "pages_processed": 0,
                "total_text_pages": total_text_pages,
                "concepts_extracted": 0,
                "relationships_extracted": 0,
                "errors": [{
                    "error": f"Could not start graph extraction: {error}"
                }],
            })

        return {
            "document_id": document_id,
            "total_pages": len(pages),
            "total_chunks": len(chunks),
            "embeddings_generated": len(embeddings),
            "chunks_stored": stored_count,
            "knowledge_graph": self.get_graph_status(document_id),
        }


ingestion_service = IngestionService()
