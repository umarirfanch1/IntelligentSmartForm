# company_parser.py
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document

def parse_website(url):
    """
    Extract readable text from a website.
    Works for most static sites. Adds a User-Agent header.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")

        # Remove scripts, styles
        for script in soup(["script", "style"]):
            script.extract()

        # Extract text
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        return "\n".join(lines)

    except Exception as e:
        print(f"[ERROR] Failed to parse URL {url}: {e}")
        return ""
