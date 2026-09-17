def chunk_pages(
    pages,
    document_id,
    chunk_size=1000,
    overlap=150
):
    chunks = []

    for page in pages:
        page_number = page["page_number"]
        text = page["text"].strip()

        if not text:
            continue

        start = 0
        chunk_number = 1

        while start < len(text):
            end = start + chunk_size

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": f"{document_id}_page_{page_number}_chunk_{chunk_number}",
                        "document_id": document_id,
                        "page_number": page_number,
                        "text": chunk_text,
                    }
                )

            if end >= len(text):
                break

            start = end - overlap
            chunk_number += 1

    return chunks