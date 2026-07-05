from src.pdf_loader import load_pdf

docs = load_pdf(
    "data/uploaded_pdfs/Unit 3.pdf"
)

print(f"Pages loaded: {len(docs)}")

print("\nFirst page:\n")
print(docs[0].page_content[:1000])