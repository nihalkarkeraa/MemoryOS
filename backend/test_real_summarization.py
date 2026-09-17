from pathlib import Path

from services.document_service import extract_text_from_pdf
from services.summarization_service import summarization_service


PDF_PATH = "data/uploads/test.pdf"


def main():

    print("=" * 70)
    print("MemoryOS - Real Document Summarization Test")
    print("=" * 70)

    # ------------------------------------------------------
    # Locate document
    # ------------------------------------------------------

    pdf_path = Path(PDF_PATH)

    print("\n[1] Checking document...")

    if not pdf_path.exists():

        raise FileNotFoundError(
            f"PDF not found: {pdf_path.resolve()}"
        )

    print(
        f"PDF found: {pdf_path.resolve()}"
    )

    # ------------------------------------------------------
    # Extract document
    # ------------------------------------------------------

    print("\n[2] Extracting document...")

    pages = extract_text_from_pdf(
        str(pdf_path)
    )

    print(
        f"Pages extracted: {len(pages)}"
    )

    if not pages:

        raise RuntimeError(
            "No text was extracted from the document."
        )

    # ------------------------------------------------------
    # Combine extracted pages
    # ------------------------------------------------------

    print("\n[3] Preparing document content...")

    document_text_parts = []

    for page in pages:

        page_number = page.get(
            "page_number",
            "Unknown"
        )

        text = page.get(
            "text",
            ""
        )

        if text.strip():

            document_text_parts.append(
                f"""
[PAGE {page_number}]

{text}
"""
            )

    document_text = "\n".join(
        document_text_parts
    )

    print(
        f"Document text length: "
        f"{len(document_text)} characters"
    )

    if not document_text.strip():

        raise RuntimeError(
            "Document contains no usable text."
        )

    # ------------------------------------------------------
    # Generate real summary
    # ------------------------------------------------------

    print("\n[4] Sending document to Ollama...")
    print("This may take some time on CPU.\n")

    result = summarization_service.summarize(
        document_text
    )

    # ------------------------------------------------------
    # Display result
    # ------------------------------------------------------

    print("=" * 70)
    print("REAL DOCUMENT SUMMARY")
    print("=" * 70)

    print(
        result["summary"]
    )

    print("=" * 70)

    if result["summary"].strip():

        print(
            "\nRESULT: Real document summarization succeeded."
        )

    else:

        print(
            "\nRESULT: Ollama returned an empty summary."
        )


if __name__ == "__main__":
    main()