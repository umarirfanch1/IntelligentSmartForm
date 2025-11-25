# company_parser.py
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document

def parse_website(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        # Remove scripts, styles, and get visible text
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        print(f"Failed to parse URL: {e}")
        return ""

def parse_uploaded_docs(files):
    """
    files: list of uploaded files from Streamlit uploader
    returns: combined text from PDFs and Word documents
    """
    combined_text = []

    for uploaded_file in files:
        filename = uploaded_file.name.lower()
        try:
            if filename.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                combined_text.append(text)
            elif filename.endswith(".docx"):
                doc = Document(uploaded_file)
                text = "\n".join([p.text for p in doc.paragraphs])
                combined_text.append(text)
            else:
                print(f"Unsupported file type: {filename}")
        except Exception as e:
            print(f"Failed to parse {filename}: {e}")

    return "\n\n".join(combined_text)
