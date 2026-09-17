import json


DOCUMENT_ID = "5f5b88a5-29b9-428b-b6c9-7c7f511a840e"

EXTRACTED_FILE = (
    f"data/extracted/{DOCUMENT_ID}.json"
)


SEARCH_TERMS = [
    "indexing",
    "normalization",
    "MongoDB",
    "NoSQL",
    "Entity-Relationship"
]


# ---------------------------------
# Load extracted pages
# ---------------------------------

with open(
    EXTRACTED_FILE,
    "r",
    encoding="utf-8"
) as file:

    pages = json.load(file)


print("\n==============================")
print("MemoryOS Keyword Diagnostic")
print("==============================")


# ---------------------------------
# Search each term
# ---------------------------------

for term in SEARCH_TERMS:

    print("\n================================")
    print(f"SEARCH TERM: {term}")
    print("================================")

    found = False

    for page in pages:

        text = page["text"]

        if term.lower() in text.lower():

            found = True

            print(
                f"\nPage {page['page_number']}"
            )

            # Find first occurrence
            position = text.lower().find(
                term.lower()
            )

            start = max(
                0,
                position - 200
            )

            end = min(
                len(text),
                position + len(term) + 300
            )

            print(
                text[start:end]
                .replace("\n", " ")
            )

    if not found:

        print(
            f"\nNo occurrence found for "
            f"'{term}'."
        )


print("\n==============================")
print("Keyword diagnostic completed")
print("==============================")