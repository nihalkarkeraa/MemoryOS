from services.chroma_service import chroma_service


print()
print("==============================")
print("MemoryOS ChromaDB Filter Test")
print("==============================")
print()

print(
    "Current ChromaDB chunks:",
    chroma_service.count()
)

print()
print("Testing document-specific chunk counting...")
print()

test_document_a = "document-A"
test_document_b = "document-B"

print(
    "Document A chunks:",
    chroma_service.count_document_chunks(
        test_document_a
    )
)

print(
    "Document B chunks:",
    chroma_service.count_document_chunks(
        test_document_b
    )
)

print()
print("==============================")
print("Filter Service Test Completed")
print("==============================")