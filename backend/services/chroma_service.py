import chromadb


CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "memoryos_documents"


class ChromaService:

    def __init__(self):
        print("Initializing ChromaDB...")

        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "description": "MemoryOS document chunks and embeddings"
            }
        )

        print("ChromaDB initialized successfully.")

    def add_chunks(
        self,
        chunks,
        embeddings
    ):
        """
        Store document chunks and their embeddings
        in ChromaDB.
        """

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        ids = [
            chunk["chunk_id"]
            for chunk in chunks
        ]

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            {
                "document_id": chunk["document_id"],
                "page_number": chunk["page_number"]
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return len(chunks)

    def search(
        self,
        query_embedding,
        n_results=5,
        document_ids=None
    ):
        """
        Search document chunks using vector similarity.

        Parameters
        ----------
        query_embedding:
            Embedding vector for the user's query.

        n_results:
            Maximum number of results to return.

        document_ids:
            Optional list of document IDs.

            If None:
                Search across all documents.

            If a list is provided:
                Search only within those documents.
        """

        # --------------------------------------------------
        # Build optional document filter
        # --------------------------------------------------

        where_filter = None

        if document_ids:

            where_filter = {
                "document_id": {
                    "$in": document_ids
                }
            }

        # --------------------------------------------------
        # Perform vector search
        # --------------------------------------------------

        if where_filter:

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )

        else:

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )

        return results

    def delete_document(
        self,
        document_id
    ):
        """
        Delete all chunks belonging to a document.
        """

        results = self.collection.get(
            where={
                "document_id": document_id
            },
            include=[
                "metadatas"
            ]
        )

        ids = results.get(
            "ids",
            []
        )

        if not ids:
            return 0

        self.collection.delete(
            ids=ids
        )

        return len(ids)

    def count(self):
        """
        Return the total number of stored chunks.
        """

        return self.collection.count()

    def count_document_chunks(
        self,
        document_id
    ):
        """
        Return the number of chunks belonging
        to a specific document.
        """

        results = self.collection.get(
            where={
                "document_id": document_id
            },
            include=[
                "metadatas"
            ]
        )

        return len(
            results.get(
                "ids",
                []
            )
        )


chroma_service = ChromaService()