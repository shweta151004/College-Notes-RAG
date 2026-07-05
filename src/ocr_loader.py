import streamlit as st

import pytesseract

from pdf2image import convert_from_path

from langchain_core.documents import Document


# -----------------------------
# Tesseract Location
# -----------------------------

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

# -----------------------------
# Poppler Location
# -----------------------------

POPPLER_PATH = (
    r"C:\Users\P K SHARMA\Desktop\Release-26.02.0-0\poppler-26.02.0\Library\bin"
)


# -----------------------------
# OCR Loader
# -----------------------------

@st.cache_data(show_spinner=False)
def load_scanned_pdf(pdf_path):

    images = convert_from_path(
        pdf_path,
        dpi=200,
        poppler_path=POPPLER_PATH
    )

    documents = []

    for page_number, image in enumerate(images):

        text = pytesseract.image_to_string(image)

        doc = Document(

            page_content=text,

            metadata={

                "source": pdf_path,

                "page": page_number + 1

            }

        )

        documents.append(doc)

    return documents

if __name__ == "__main__":

    docs = load_scanned_pdf(
        "data/uploaded_pdfs/PPT_2.pdf"
    )

    print("=" * 60)

    print("Pages extracted:", len(docs))

    print("=" * 60)

    print(docs[0].page_content[:1000])