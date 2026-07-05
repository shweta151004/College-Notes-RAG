import os
from dotenv import load_dotenv
import google.generativeai as genai

# -----------------------
# LOAD GEMINI API KEY
# -----------------------

load_dotenv()

genai.configure(
    api_key=os.getenv("GOOGLE_API_KEY")
)

# -----------------------
# GEMINI MODEL
# -----------------------

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# -----------------------
# ANSWER QUESTION
# -----------------------

def answer_question(
    question,
    retriever,
    chat_history=None
):

    # -----------------------
    # BUILD SEARCH QUERY
    # -----------------------

    search_query = question

    if chat_history:

        previous = chat_history[-2:]

        history = "\n".join(
            f"User: {chat['question']}"
            for chat in previous
        )

        search_query = (
            history +
            "\nCurrent Question: " +
            question
        )

    # -----------------------
    # RETRIEVE DOCUMENTS
    # -----------------------

    docs = retriever.invoke(search_query)

    # -----------------------
    # BUILD CONTEXT
    # -----------------------

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # -----------------------
    # BUILD SOURCES
    # -----------------------

    sources = []

    for doc in docs:

        filename = os.path.basename(
            doc.metadata.get(
                "source",
                "Unknown Document"
            )
        )

        page = doc.metadata.get(
            "page",
            0
        )

        source = f"{filename} - Page {page}"

        if source not in sources:
            sources.append(source)

    # -----------------------
    # CHAT HISTORY
    # -----------------------

    history_text = ""

    if chat_history:

        for chat in chat_history[-5:]:

            history_text += (
                f"User: {chat['question']}\n"
                f"Assistant: {chat['answer']}\n\n"
            )

    # -----------------------
    # PROMPT
    # -----------------------

    prompt = f"""
You are an expert College Notes AI Assistant.

Your job is to answer ONLY using the retrieved context.

Rules:

1. Use ONLY the information present in the context.

2. If the answer is not present, reply exactly:

"I could not find this information in the uploaded documents."

3. Never make up facts.

4. If multiple documents contain useful information,
combine them into one answer.

5. Answer in simple language.

6. Use bullet points whenever appropriate.

------------------------

Conversation History:

{history_text}

------------------------

Retrieved Context:

{context}

------------------------

Current Question:

{question}

------------------------

Answer:
"""

    # -----------------------
    # GENERATE RESPONSE
    # -----------------------

    response = model.generate_content(prompt)

    answer = response.text

    return answer, sources