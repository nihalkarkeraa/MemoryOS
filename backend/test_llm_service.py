from services.llm_service import llm_service


print("\n==============================")
print("MemoryOS LLM Service Test")
print("==============================")


prompt = """
You are a helpful AI assistant.

Answer the following question briefly and clearly.

Question:
What is database normalization?

Answer:
"""


print("\nSending prompt to Phi-3 Mini...")

response = llm_service.generate(
    prompt=prompt
)


print("\n==============================")
print("Phi-3 Mini Response")
print("==============================")

print(response)


print("\n==============================")
print("LLM test completed")
print("==============================")