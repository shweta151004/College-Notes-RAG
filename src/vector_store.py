import os
import streamlit as st

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# -----------------------
# CONFIG
# -----------------------

DB_DIRECTORY = "chroma_db"

COLLECTION_NAME = "college_notes"

# -----------------------
# EMBEDDING MODEL
# -----------------------

@st.cache_resource
def get_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# -----------------------
# CREATE / ADD DOCUMENTS
# -----------------------

def create_vector_store(chunks):

    embedding_model = get_embedding_model()

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIRECTORY,
        embedding_function=embedding_model
    )

    db.add_documents(chunks)

    return db


# -----------------------
# LOAD EXISTING DATABASE
# -----------------------

def load_vector_store():

    embedding_model = get_embedding_model()

    db = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=DB_DIRECTORY,
        embedding_function=embedding_model
    )

    return db


# -----------------------
# CHECK DATABASE
# -----------------------

def vector_store_exists():

    return os.path.exists(DB_DIRECTORY)


# -----------------------
# VECTOR COUNT
# -----------------------

def get_vector_count():

    if not vector_store_exists():

        return 0

    db = load_vector_store()

    try:

        return db._collection.count()

    except:

        return 0