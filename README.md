# 📚 College Notes RAG

> An AI-powered Retrieval-Augmented Generation (RAG) application that lets students chat with their lecture notes, scanned PDFs, and study material using Google Gemini and ChromaDB.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Deployed-red)
![Gemini](https://img.shields.io/badge/Google-Gemini%202.5%20Flash-blue)
![ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-success)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🚀 Live Demo

🔗 **App:** [https://YOUR-STREAMLIT-LINK.streamlit.app](https://college-notes-rag-bxhhbyuq3zebr2jc5ryebs.streamlit.app/)

🔗 **GitHub Repository:** https://github.com/shweta151004/College-Notes-RAG

---

# 📖 Overview

College Notes RAG is an AI-powered study assistant that enables students to upload multiple PDF documents and ask natural language questions about their study material.

Instead of manually searching through hundreds of pages, the application retrieves the most relevant content using semantic search and generates accurate answers with **Google Gemini 2.5 Flash**.

---

# ✨ Features

✅ Upload multiple PDFs

✅ Persistent ChromaDB vector database

✅ Semantic search using embeddings

✅ Google Gemini 2.5 Flash integration

✅ OCR support for scanned PDFs

✅ Table extraction

✅ PDF preview

✅ Source citation

✅ Chat history

✅ Export chat

✅ Modern responsive UI

✅ Dark theme

✅ Cloud deployed using Streamlit Community Cloud

---

# 🖥️ Screenshots

## Home Page

> *(<img width="1900" height="807" alt="image" src="https://github.com/user-attachments/assets/62996c30-0d88-4de8-a4d8-76e37ae01458" />)*

---

## Upload PDFs

> *(<img width="1918" height="803" alt="image" src="https://github.com/user-attachments/assets/ee0b8987-4491-4cef-af34-5bd1e9658509" />)*

---

## Chat with Notes

> *(<img width="1902" height="807" alt="image" src="https://github.com/user-attachments/assets/c99180c7-b88e-405f-b69e-01b8eb33de8e" />)*

---

## PDF Preview

> *(<img width="1916" height="796" alt="image" src="https://github.com/user-attachments/assets/8d837378-c479-45c2-87a7-06acc4e081cb" />)*

---

# ⚙️ Tech Stack

## Frontend

- Streamlit
- HTML
- CSS

## Backend

- Python

## AI

- Google Gemini 2.5 Flash

## Embedding Model

- sentence-transformers
- all-MiniLM-L6-v2

## Vector Database

- ChromaDB

## Document Processing

- PyMuPDF
- PDFPlumber
- Tesseract OCR
- PDF2Image

---

# 🧠 Architecture

```
            PDF Upload
                 │
                 ▼
        PDF Processing
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
 Text Extraction      OCR (Optional)
       │
       ▼
 Chunking
       │
       ▼
 Embedding Generation
       │
       ▼
 ChromaDB Vector Store
       │
       ▼
 User Question
       │
       ▼
 Semantic Retrieval
       │
       ▼
 Gemini 2.5 Flash
       │
       ▼
 Final Answer + Sources
```

---

# 📂 Project Structure

```
College-Notes-RAG/
│
├── assets/
│   └── style.css
│
├── data/
│   ├── uploaded_pdfs/
│   └── manifest.json
│
├── src/
│   ├── chunker.py
│   ├── manifest.py
│   ├── ocr_loader.py
│   ├── pdf_loader.py
│   ├── rag_chain.py
│   ├── retriever.py
│   ├── table_loader.py
│   ├── vector_store.py
│   └── export_chat.py
│
├── ui/
│   └── pdf_preview.py
│
├── app.py
├── requirements.txt
└── README.md
```

---

# ⚡ Installation

Clone the repository

```bash
git clone https://github.com/shweta151004/College-Notes-RAG.git

cd College-Notes-RAG
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

Run the application

```bash
streamlit run app.py
```

---

# 🧪 How It Works

1. Upload one or more PDF files.
2. Documents are processed.
3. Text is extracted.
4. OCR is applied to scanned pages.
5. Documents are split into chunks.
6. Embeddings are generated.
7. Chunks are stored in ChromaDB.
8. User asks a question.
9. Relevant chunks are retrieved.
10. Gemini generates the final answer.
11. Source citations are displayed.

---

# 🎯 Use Cases

- College Notes
- Research Papers
- Lecture Slides
- Lab Manuals
- Study Material
- Technical Documentation
- Exam Preparation

---

# 📌 Future Improvements

- Voice interaction
- Mobile responsive layout
- Authentication
- User accounts
- Cloud vector database
- Multi-language OCR
- Image understanding
- Highlight cited text inside PDF
- Chat with DOCX and PPT files

---

# 📊 Key Features

| Feature | Status |
|----------|---------|
| Multi PDF Upload | ✅ |
| Semantic Search | ✅ |
| OCR | ✅ |
| Table Extraction | ✅ |
| PDF Preview | ✅ |
| Source Citation | ✅ |
| Export Chat | ✅ |
| Persistent ChromaDB | ✅ |
| Gemini Integration | ✅ |
| Streamlit Deployment | ✅ |

---

# 👩‍💻 Author

**Shweta Sharma**

B.Tech Electronics & Communication Engineering

Pandit Deendayal Energy University (PDEU)

GitHub:
https://github.com/shweta151004

LinkedIn:
www.linkedin.com/in/shweta-sharma-373816340

---

# ⭐ If you found this project useful

Please consider giving the repository a ⭐ on GitHub.

It helps others discover the project and supports future development.

---

# 📜 License

This project is licensed under the MIT License.
