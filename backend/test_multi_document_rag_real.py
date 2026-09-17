import services.rag_service as rag_module
import services.document_registry_service as registry_module


print()
print("=" * 70)
print("MemoryOS — MULTI-DOCUMENT RAG TEST")
print("=" * 70)


# --------------------------------------------------
# Show currently registered documents
# --------------------------------------------------

documents = registry_module.document_registry_service.list_documents()

print()
print("Registered documents:")
print()

for index, document in enumerate(documents, start=1):

    print(f"Document {index}")

    print(
        "ID:",
        document.get("document_id")
    )

    print(
        "Name:",
        document.get("filename")
    )

    print(
        "Pages:",
        document.get("page_count")
    )

    print()


# --------------------------------------------------
# Validation
# --------------------------------------------------

if len(documents) < 2:

    print("=" * 70)
    print("TEST CANNOT CONTINUE")
    print("=" * 70)

    print()
    print(
        "At least 2 registered documents are required."
    )

    print(
        "Upload another PDF through Swagger first."
    )

    raise SystemExit


# --------------------------------------------------
# Select first two documents
# --------------------------------------------------

document_a = documents[0]
document_b = documents[1]

document_a_id = document_a["document_id"]
document_b_id = document_b["document_id"]

document_a_name = document_a.get(
    "filename",
    "Document A"
)

document_b_name = document_b.get(
    "filename",
    "Document B"
)


print("=" * 70)
print("TEST DOCUMENTS")
print("=" * 70)

print()
print(
    "Document A:",
    document_a_name
)

print(
    "Document A ID:",
    document_a_id
)

print()

print(
    "Document B:",
    document_b_name
)

print(
    "Document B ID:",
    document_b_id
)


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def run_test(
    title,
    question,
    document_ids
):

    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    print()
    print("Question:")
    print(question)

    print()
    print("Document filter:")
    print(document_ids)

    print()
    print("Running RAG...")

    result = rag_module.rag_service.answer(
        question=question,
        n_results=5,
        document_ids=document_ids
    )

    print()
    print("Answer:")
    print(
        result["answer"]
    )

    print()
    print("Sources:")

    source_documents = []

    for index, source in enumerate(
        result.get("sources", []),
        start=1
    ):

        source_document_id = source.get(
            "document_id"
        )

        source_page = source.get(
            "page_number"
        )

        source_documents.append(
            source_document_id
        )

        print(
            f"Source {index}: "
            f"Document={source_document_id}, "
            f"Page={source_page}"
        )

    return result, source_documents


# --------------------------------------------------
# TEST 1 — Document A only
# --------------------------------------------------

result_a, sources_a = run_test(
    "TEST 1 — DOCUMENT A ONLY",
    "What is database indexing?",
    [document_a_id]
)


print()
print("Validation:")

if all(
    document_id == document_a_id
    for document_id in sources_a
):

    print(
        "PASS: All sources came from Document A."
    )

else:

    print(
        "FAIL: A source from another document "
        "was returned."
    )


# --------------------------------------------------
# TEST 2 — Document B only
# --------------------------------------------------

result_b, sources_b = run_test(
    "TEST 2 — DOCUMENT B ONLY",
    "What is database indexing?",
    [document_b_id]
)


print()
print("Validation:")

if all(
    document_id == document_b_id
    for document_id in sources_b
):

    print(
        "PASS: All sources came from Document B."
    )

else:

    print(
        "FAIL: A source from another document "
        "was returned."
    )


# --------------------------------------------------
# TEST 3 — Both documents
# --------------------------------------------------

result_both, sources_both = run_test(
    "TEST 3 — BOTH DOCUMENTS",
    "What is database indexing?",
    [
        document_a_id,
        document_b_id
    ]
)


print()
print("Validation:")

allowed_documents = {
    document_a_id,
    document_b_id
}

if all(
    document_id in allowed_documents
    for document_id in sources_both
):

    print(
        "PASS: All sources belong to "
        "the selected documents."
    )

else:

    print(
        "FAIL: An unexpected document "
        "appeared in the results."
    )


# --------------------------------------------------
# TEST 4 — No document filter
# --------------------------------------------------

result_all, sources_all = run_test(
    "TEST 4 — ALL DOCUMENTS",
    "What is database indexing?",
    None
)


print()
print("Validation:")

print(
    "Documents returned:",
    set(sources_all)
)

print(
    "PASS: Unrestricted multi-document "
    "RAG executed successfully."
)


# --------------------------------------------------
# Final summary
# --------------------------------------------------

print()
print("=" * 70)
print("MULTI-DOCUMENT RAG TEST SUMMARY")
print("=" * 70)

print()

print(
    "Document A only sources:",
    sources_a
)

print(
    "Document B only sources:",
    sources_b
)

print(
    "Both documents sources:",
    sources_both
)

print(
    "All documents sources:",
    sources_all
)

print()
print("=" * 70)
print("MULTI-DOCUMENT RAG TEST COMPLETE")
print("=" * 70)