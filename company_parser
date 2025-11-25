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
        # Clean extra whitespace
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
    except Exception as e:
        print(f"Failed to parse URL: {e}")
        return ""
