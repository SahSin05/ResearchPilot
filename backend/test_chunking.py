from app.services.chunking import chunk_text


text = """
ResearchPilot is an AI research assistant.

It helps researchers discover papers,
upload documents, understand research,
and ask questions grounded in their sources.

The system will eventually use retrieval
augmented generation to retrieve relevant
sections of documents before generating answers.
"""


chunks = chunk_text(
    text,
    chunk_size=120,
    overlap=20,
)


print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks):
    print("\n--- Chunk", index, "---")
    print(chunk)

    