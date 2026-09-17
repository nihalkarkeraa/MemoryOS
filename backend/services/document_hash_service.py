import hashlib


class DocumentHashService:

    def calculate_hash(
        self,
        file_path: str
    ):
        """
        Calculate a SHA-256 hash for the entire file.

        Files with identical contents will produce
        the same hash, regardless of their filename.
        """

        sha256 = hashlib.sha256()

        with open(
            file_path,
            "rb"
        ) as file:

            while True:

                chunk = file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                sha256.update(
                    chunk
                )

        return sha256.hexdigest()


document_hash_service = DocumentHashService()