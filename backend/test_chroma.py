from services.chroma_service import chroma_service


print("\n--------------------")
print("ChromaDB test")
print("--------------------")

print(
    f"Collection count: "
    f"{chroma_service.count()}"
)

print("\nChromaDB is working correctly.")