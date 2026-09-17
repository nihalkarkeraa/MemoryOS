from uuid import uuid4
from datetime import datetime, timezone

from services.document_hash_service import (
    document_hash_service
)

from services.document_registry_service import (
    document_registry_service
)


print("\n==============================")
print("MemoryOS Document Registry Test")
print("==============================")


# --------------------------------------------------
# 1. Calculate hash of test PDF
# --------------------------------------------------

pdf_path = (
    "data/uploads/test.pdf"
)

file_hash = (
    document_hash_service.calculate_hash(
        pdf_path
    )
)


print("\nTest PDF:")
print(pdf_path)

print("\nSHA-256:")
print(file_hash)


# --------------------------------------------------
# 2. Check whether document already exists
# --------------------------------------------------

existing_document = (
    document_registry_service.find_by_hash(
        file_hash
    )
)


print("\n==============================")
print("Initial Duplicate Check")
print("==============================")


if existing_document:

    print(
        "Document already exists in registry."
    )

    print(
        f"Existing document ID: "
        f"{existing_document['document_id']}"
    )

else:

    print(
        "Document does not exist yet."
    )


# --------------------------------------------------
# 3. Register document if new
# --------------------------------------------------

if not existing_document:

    document = {

        "document_id": str(
            uuid4()
        ),

        "filename": "test.pdf",

        "file_hash": file_hash,

        "upload_time": datetime.now(
            timezone.utc
        ).isoformat(),

        "status": "processed",

        "total_pages": 103,

        "total_chunks": 124
    }

    registered_document = (
        document_registry_service.register_document(
            document
        )
    )

    print("\n==============================")
    print("Document Registered")
    print("==============================")

    print(
        f"Document ID: "
        f"{registered_document['document_id']}"
    )

else:

    registered_document = (
        existing_document
    )


# --------------------------------------------------
# 4. Check duplicate again
# --------------------------------------------------

duplicate_check = (
    document_registry_service.find_by_hash(
        file_hash
    )
)


print("\n==============================")
print("Second Duplicate Check")
print("==============================")


if duplicate_check:

    print(
        "Duplicate detected successfully."
    )

    print(
        f"Document ID: "
        f"{duplicate_check['document_id']}"
    )

else:

    print(
        "ERROR: Duplicate was not detected."
    )


# --------------------------------------------------
# 5. Test lookup by document ID
# --------------------------------------------------

document_id = (
    registered_document["document_id"]
)

document_by_id = (
    document_registry_service.find_by_id(
        document_id
    )
)


print("\n==============================")
print("Document ID Lookup")
print("==============================")


if document_by_id:

    print(
        "Document found successfully."
    )

    print(
        f"Filename: "
        f"{document_by_id['filename']}"
    )

else:

    print(
        "ERROR: Document ID lookup failed."
    )


# --------------------------------------------------
# 6. Registry statistics
# --------------------------------------------------

print("\n==============================")
print("Registry Statistics")
print("==============================")


print(
    f"Registered documents: "
    f"{document_registry_service.count()}"
)


print("\n==============================")
print("Registry test completed")
print("==============================")