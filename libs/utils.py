import fitz  # PyMuPDF
from docx import Document
import os
import json


def extract_text_from_doc(doc_path):
    pypandoc.download_pandoc()

    text = ""
    try:
        text = pypandoc.convert_file(doc_path, 'plain')
    except Exception as e:
        print(f"Error reading DOC file: {e}")
    return text

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        document = fitz.open(pdf_path)
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF file: {e}")
    return text

def extract_text_from_docx(docx_path):
    text = ""
    try:
        document = Document(docx_path)
        for paragraph in document.paragraphs:
            text += paragraph.text + "\n"
        
    except Exception as e:
        print(f"Error reading DOCX file: {e}")
    return text
