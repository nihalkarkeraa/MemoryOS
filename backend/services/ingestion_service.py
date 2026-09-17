
from services.document_service import extract_text_from_pdf
from services.chunking_service import chunk_pages
from services.embedding_service import embedding_service
from services.chroma_service import chroma_service
from services.knowledge_graph_extraction_service import (
    KnowledgeGraphExtractionService,
)


class IngestionService:

    def __init__(
        self,
        embedding_service_instance=None,
        chroma_service_instance=None,
        graph_extraction_service_instance=None,
    ):
        self.embedding_service = (
            embedding_service_instance
            or embedding_service
        )

        self.chroma_service = (
            chroma_service_instance
            or chroma_service
        )

        self.graph_extraction_service = (
            graph_extraction_service_instance
            or KnowledgeGraphExtractionService()
        )

    def ingest_pdf(
        self,
        file_path: str,
        document_id: str,
    ):
        """
        Complete document ingestion pipeline.

        PDF
            ↓
        Text Extraction
            ↓
        Chunking
            ↓
        Embeddings
            ↓
        ChromaDB
            ↓
        Knowledge Graph Extraction
        """

        # --------------------------------------------------
        # 1. Extract text
        # --------------------------------------------------

        pages = extract_text_from_pdf(
            file_path
        )

        # --------------------------------------------------
        # 2. Create chunks
        # --------------------------------------------------

        chunks = chunk_pages(
            pages=pages,
            document_id=document_id
        )

        # --------------------------------------------------
        # 3. Generate embeddings
        # --------------------------------------------------

        if chunks:

            texts = [
                chunk["text"]
                for chunk in chunks
            ]

            embeddings = (
                self.embedding_service.embed_texts(
                    texts
                )
            )

        else:

            embeddings = []

        # --------------------------------------------------
        # 4. Store chunks and embeddings
        # --------------------------------------------------

        if chunks:

            stored_count = (
                self.chroma_service.add_chunks(
                    chunks=chunks,
                    embeddings=embeddings
                )
            )

        else:

            stored_count = 0

        # --------------------------------------------------
        # 5. Extract Knowledge Graph information
        # --------------------------------------------------

        graph_concepts_extracted = 0
        graph_relationships_extracted = 0
        graph_pages_processed = 0
        graph_errors = []

        for page in pages:

            page_text = page.get(
                "text",
                ""
            )

            page_number = page.get(
                "page_number"
            )

            if not isinstance(page_text, str):
                continue

            if not page_text.strip():
                continue

            try:

                graph_result = (
                    self.graph_extraction_service.extract_from_text(
                        text=page_text,
                        document_id=document_id,
                        page_number=page_number,
                    )
                )

                graph_concepts_extracted += (
                    graph_result.get(
                        "concepts_extracted",
                        0
                    )
                )

                graph_relationships_extracted += (
                    graph_result.get(
                        "relationships_extracted",
                        0
                    )
                )

                graph_pages_processed += 1

            except Exception as error:

                graph_errors.append({
                    "page_number": page_number,
                    "error": str(error),
                })

        # --------------------------------------------------
        # 6. Determine graph extraction status
        # --------------------------------------------------

        if not graph_errors:

            graph_status = "completed"

        elif graph_pages_processed > 0:

            graph_status = "partial"

        else:

            graph_status = "failed"

        # --------------------------------------------------
        # 7. Return ingestion information
        # --------------------------------------------------

        return {
            "document_id": document_id,

            "total_pages": len(pages),

            "total_chunks": len(chunks),

            "embeddings_generated": len(
                embeddings
            ),

            "chunks_stored": stored_count,

            "knowledge_graph": {
                "status": graph_status,

                "pages_processed": (
                    graph_pages_processed
                ),

                "concepts_extracted": (
                    graph_concepts_extracted
                ),

                "relationships_extracted": (
                    graph_relationships_extracted
                ),

                "errors": graph_errors,
            },
        }


ingestion_service = IngestionService()