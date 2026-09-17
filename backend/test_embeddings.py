from services.embedding_service import embedding_service


text = "Database indexing improves query performance."


embedding = embedding_service.embed_text(text)


print("\n--------------------")
print("Embedding test")
print("--------------------")

print(f"Input text: {text}")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First 10 values: {embedding[:10]}")