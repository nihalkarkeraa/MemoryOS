import json

from services.chunking_service import chunk_pages


document_id = "5f5b88a5-29b9-428b-b6c9-7c7f511a840e"

extracted_file = (
    f"data/extracted/{document_id}.json"
)


with open(extracted_file, "r", encoding="utf-8") as file:
    pages = json.load(file)


chunks = chunk_pages(
    pages,
    document_id
)


print(f"Total pages: {len(pages)}")
print(f"Total chunks: {len(chunks)}")


for chunk in chunks[:5]:
    print("\n--------------------")
    print(f"Chunk ID: {chunk['chunk_id']}")
    print(f"Document ID: {chunk['document_id']}")
    print(f"Page: {chunk['page_number']}")
    print(f"Characters: {len(chunk['text'])}")
    print(chunk["text"][:300])