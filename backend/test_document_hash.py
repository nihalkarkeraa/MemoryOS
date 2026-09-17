from pathlib import Path

from services.document_hash_service import (
    document_hash_service
)


print("\n==============================")
print("MemoryOS Document Hash Test")
print("==============================")


pdf_path = Path(
    "data/uploads/test.pdf"
)


if not pdf_path.exists():

    print(
        f"\nERROR: File not found:"
        f"\n{pdf_path}"
    )

    raise SystemExit(1)


print("\nCalculating SHA-256 hash...")


file_hash = (
    document_hash_service.calculate_hash(
        str(pdf_path)
    )
)


print("\n==============================")
print("Hash Result")
print("==============================")


print(
    f"File: {pdf_path.name}"
)

print(
    f"SHA-256: {file_hash}"
)

print(
    f"Hash length: {len(file_hash)} characters"
)


print("\n==============================")
print("Hash test completed")
print("==============================")