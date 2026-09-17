from services.document_service import extract_text_from_pdf


pdf_path = "data/uploads/test.pdf"

pages = extract_text_from_pdf(pdf_path)

print(f"Total pages: {len(pages)}")

for page in pages[:3]:
    print("\n--------------------")
    print(f"Page: {page['page_number']}")
    print(page["text"][:500])