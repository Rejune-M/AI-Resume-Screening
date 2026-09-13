from PyPDF2 import PdfReader
from docx import Document


def extract_pdf_text(file):
    reader = PdfReader(file)
    text = []

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_docx_text(file):
    document = Document(file)

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text)

    return "\n".join(text)


def extract_resume_text(file):
    filename = file.name.lower()

    if filename.endswith(".pdf"):
        return extract_pdf_text(file)

    if filename.endswith(".docx"):
        return extract_docx_text(file)

    return ""