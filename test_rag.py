from src.pdf_loader import load_pdf
from src.chunker import chunk_documents
from src.vector_store import create_vector_store
from src.retriever import get_retriever
from src.rag_chain import answer_question

docs = load_pdf(
    "data/uploaded_pdfs/Unit 3.pdf"
)

chunks = chunk_documents(docs)

db = create_vector_store(chunks)

retriever = get_retriever(db)

question = input("Ask a question: ")

answer, sources = answer_question(
    question,
    retriever
)

print("\nAnswer:\n")
print(answer)

print("\nSources:")
print(", ".join(sources))