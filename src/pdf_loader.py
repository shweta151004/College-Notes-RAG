from chromadb import Documents
from langchain_community.document_loaders import PyPDFLoader
from src.ocr_loader import load_scanned_pdf
from src.table_loader import extract_tables
#from src.image_loader import extract_images

def load_pdf(filepath):

    loader = PyPDFLoader(filepath)
    docs = loader.load()

    extracted_text = ""

    for doc in docs:
        extracted_text += doc.page_content.strip()

    # if enough text exists → normal PDF
    if len(extracted_text) > 300:

        print("✅ Digital PDF detected.")

        # ---------------------------------
        # Extract Tables
        # ---------------------------------

        table_docs = extract_tables(filepath)
        docs.extend(table_docs)
        # -----------------------------
        # Image Understanding
        # -----------------------------

       # image_docs = extract_images(filepath)

        #docs.extend(image_docs)
        return docs

    # otherwise OCR

    print("📷 Scanned PDF detected. Running OCR...")

    return load_scanned_pdf(filepath)