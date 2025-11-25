# company_parser.py
import requests
from bs4 import BeautifulSoup

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
    """Extract text from uploaded PDF or DOCX files."""
    import io
    from PyPDF2 import PdfReader
    import docx

    all_text = []
    for uploaded_file in files:
        name = uploaded_file.name.lower()
        if name.endswith(".pdf"):
            pdf = PdfReader(io.BytesIO(uploaded_file.read()))
            text = "\n".join([page.extract_text() or "" for page in pdf.pages])
            all_text.append(text)
        elif name.endswith(".docx"):
            doc = docx.Document(io.BytesIO(uploaded_file.read()))
            text = "\n".join([p.text for p in doc.paragraphs])
            all_text.append(text)
    return "\n".join(all_text)
