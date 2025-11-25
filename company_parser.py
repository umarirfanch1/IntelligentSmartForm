# company_parser.py
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document


def parse_website(url):
    """
    Extract readable text from any company website.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove JS + CSS
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
    Parse uploaded PDFs and DOCX files into raw text.

    Args:
        files: list of StreamlitUploadedFile objects
    Returns:
        str: combined extracted text
    """

    combined_text = []

    for uploaded_file in files:
        filename = uploaded_file.name.lower()

        try:
            # -------------------------
            # Parse PDF Files
            # -------------------------
            if filename.endswith(".pdf"):
                reader = PdfReader(uploaded_file)
                text = ""

                for page in reader.pages:
                    extracted = page.extract_text() or ""
                    text += extracted

                combined_text.append(text)

            # -------------------------
            # Parse DOCX Files
            # -------------------------
            elif filename.endswith(".docx"):
                doc = Document(uploaded_file)
                text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
                combined_text.append(text)

            # -------------------------
            # Unsupported Formats
            # -------------------------
            else:
                print(f"Unsupported file type: {filename}")

        except Exception as e:
            print(f"Failed to parse file {filename}: {e}")

    return "\n\n".join(combined_text)
