from src.pdf_loader import load_pdf
from src.chunker import chunk_documents
from src.vector_store import create_vector_store

docs = load_pdf(
    "data/uploaded_pdfs/Unit 3.pdf"
)

chunks = chunk_documents(docs)

print(f"Chunks created: {len(chunks)}")

db = create_vector_store(chunks)

print("Vector database created successfully!")