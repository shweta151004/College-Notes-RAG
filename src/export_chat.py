import io
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def export_chat_pdf(chat_history):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph("<b>College Notes RAG Chat Export</b>", styles["Heading1"]))

    story.append(Paragraph("<br/>", styles["Normal"]))

    for chat in chat_history:

        story.append(
            Paragraph(
                f"<b>User:</b> {chat['question']}",
                styles["Normal"]
            )
        )

        story.append(
            Paragraph(
                f"<b>Assistant:</b> {chat['answer']}",
                styles["Normal"]
            )
        )

        if chat["sources"]:

            story.append(
                Paragraph(
                    "<b>Sources:</b>",
                    styles["Normal"]
                )
            )

            for source in chat["sources"]:

                story.append(
                    Paragraph(
                        source,
                        styles["Normal"]
                    )
                )

        story.append(
            Paragraph("<br/><br/>", styles["Normal"])
        )

    doc.build(story)

    buffer.seek(0)

    return buffer


def export_chat_markdown(chat_history):

    md = "# College Notes RAG Chat Export\n\n"

    for chat in chat_history:

        md += f"## User\n{chat['question']}\n\n"

        md += f"## Assistant\n{chat['answer']}\n\n"

        if chat["sources"]:

            md += "### Sources\n"

            for source in chat["sources"]:

                md += f"- {source}\n"

        md += "\n---\n\n"

    return md