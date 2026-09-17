from pathlib import Path
import json


REGISTRY_PATH = Path(
    "data/documents/registry.json"
)


class DocumentRegistryService:

    def __init__(
        self,
        registry_path=REGISTRY_PATH
    ):
        self.registry_path = Path(
            registry_path
        )

        self.registry_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._initialize_registry()

    def _initialize_registry(self):
        """
        Create the registry file if it
        does not already exist.
        """

        if not self.registry_path.exists():

            with open(
                self.registry_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    [],
                    file,
                    indent=4
                )

    def _load_documents(self):
        """
        Load all registered documents.
        """

        try:

            with open(
                self.registry_path,
                "r",
                encoding="utf-8"
            ) as file:

                documents = json.load(
                    file
                )

        except (
            json.JSONDecodeError,
            FileNotFoundError
        ):

            documents = []

        return documents

    def _save_documents(
        self,
        documents
    ):
        """
        Save all registered documents.
        """

        with open(
            self.registry_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                documents,
                file,
                indent=4,
                ensure_ascii=False
            )

    def find_by_hash(
        self,
        file_hash: str
    ):
        """
        Find a document using its SHA-256 hash.

        Returns the document if found,
        otherwise None.
        """

        documents = self._load_documents()

        for document in documents:

            if document.get(
                "file_hash"
            ) == file_hash:

                return document

        return None

    def find_by_id(
        self,
        document_id: str
    ):
        """
        Find a document using its document ID.
        """

        documents = self._load_documents()

        for document in documents:

            if document.get(
                "document_id"
            ) == document_id:

                return document

        return None

    def register_document(
        self,
        document
    ):
        """
        Register a new document.

        Duplicate file hashes are rejected.
        """

        existing_document = (
            self.find_by_hash(
                document["file_hash"]
            )
        )

        if existing_document:

            raise ValueError(
                "A document with the same "
                "file hash already exists."
            )

        documents = self._load_documents()

        documents.append(
            document
        )

        self._save_documents(
            documents
        )

        return document

    def delete_document(
        self,
        document_id: str
    ):
        """
        Delete a document from the registry.

        Returns the deleted document if found.
        Returns None if the document does not exist.
        """

        documents = self._load_documents()

        remaining_documents = []

        deleted_document = None

        for document in documents:

            if document.get(
                "document_id"
            ) == document_id:

                deleted_document = document

            else:

                remaining_documents.append(
                    document
                )

        if deleted_document is None:
            return None

        self._save_documents(
            remaining_documents
        )

        return deleted_document

    def list_documents(self):
        """
        Return all registered documents.
        """

        return self._load_documents()

    def count(self):
        """
        Return the number of registered documents.
        """

        return len(
            self._load_documents()
        )


document_registry_service = (
    DocumentRegistryService()
)