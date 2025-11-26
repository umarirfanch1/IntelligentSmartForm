# company_parser.py
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document
import re

def parse_website(url: str) -> str:
    """
    Extract readable text from a website.
    Works for most static sites. Adds a User-Agent header.
    
    Args:
        url (str): website URL
    Returns:
        str: extracted plain text
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove scripts, styles, and hidden elements
        for element in soup(["script", "style", "noscript", "iframe"]):
            element.extract()

        # Grab meta description if available
        meta_desc = ""
        if soup.find("meta", attrs={"name": "description"}):
            meta_desc = soup.find("meta", attrs={"name": "description"}).get("content", "")
        elif soup.find("meta", attrs={"property": "og:description"}):
            meta_desc = soup.find("meta", attrs={"property": "og:description"}).get("content", "")

        # Extract main visible text
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Combine meta description and page text
        full_text = meta_desc + "\n" + "\n".join(lines)
        
        # Clean multiple blank lines
        full_text = re.sub(r'\n+', '\n', full_text)
        
        return full_text.strip()

    except Exception as e:
        print(f"[ERROR] Failed to parse URL {url}: {e}")
        return ""


def parse_uploaded_docs(files) -> str:
    """
    Parse uploaded PDF and DOCX files into clean text.
    
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
                for i, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    page_text = re.sub(r'\s+', ' ', page_text).strip()
                    text += page_text + "\n"
                combined_text.append(text)

            # -------------------------
            # Parse DOCX Files
            # -------------------------
            elif filename.endswith(".docx"):
                doc = Document(uploaded_file)
                text = "\n".join(p.text.strip() for p in doc.paragraphs if p.text.strip())
                combined_text.append(text)

            else:
                print(f"[WARNING] Unsupported file type: {filename}")

        except Exception as e:
            print(f"[ERROR] Failed to parse file {filename}: {e}")

    # Combine all documents
    all_text = "\n\n".join(combined_text)
    all_text = re.sub(r'\n+', '\n', all_text).strip()  # clean extra blank lines

    return all_text
