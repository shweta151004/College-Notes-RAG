import pdfplumber

from langchain_core.documents import Document


def extract_tables(pdf_path):

    documents = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_number, page in enumerate(pdf.pages):

            page_text = page.extract_text() or ""

            lines = page_text.split("\n")

            table_title = "Extracted Table"

            for line in lines:

                line = line.strip()

                if len(line) > 5 and len(line) < 80:

                    table_title = line

                    break


            tables = page.extract_tables()

            if not tables:
                continue

            for table in tables:

                if not table or len(table) < 2:
                    continue

                headers = [
                    str(h).strip() if h else f"Column {i+1}"
                    for i, h in enumerate(table[0])
                ]

                text = f"Table Title: {table_title}\n\n"

                for row in table[1:]:

                    row = [
                        str(cell).strip() if cell else ""
                        for cell in row
                    ]

                    text += "Table Record:\n"

                    for header, value in zip(headers, row):

                        text += f"{header}: {value}\n"

                    text += "\n"
                documents.append(

                    Document(

                        page_content=text.strip(),

                        metadata={
                            "source": pdf_path,
                            "page": page_number + 1,
                            "type": "table",
                            "table_title": table_title,
                            "rows": len(table) - 1,
                            "columns": len(headers)
                       }

                    )

                )

    return documents

if __name__ == "__main__":

    docs = extract_tables(
        "data/uploaded_pdfs/table_extraction_samples.pdf"
    )

    print(len(docs))

    if docs:

        print(docs[0].page_content)