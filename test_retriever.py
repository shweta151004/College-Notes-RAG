from src.pdf_loader import load_pdf
from src.chunker import chunk_documents
from src.vector_store import create_vector_store
from src.retriever import get_retriever

docs = load_pdf(
    "data/uploaded_pdfs/Unit 3.pdf"
)

chunks = chunk_documents(docs)

db = create_vector_store(chunks)

retriever = get_retriever(db)

query = "What is a cleanroom?"

results = retriever.invoke(query)

print(f"\nQuestion: {query}")

for i, doc in enumerate(results):

    print(f"\n--- Result {i+1} ---")

    print(doc.page_content[:500])

    print("\nMetadata:")
    print(doc.metadata)