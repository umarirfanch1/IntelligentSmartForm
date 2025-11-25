# ai_fill.py
import cohere
import os

# Use Streamlit secrets if available, else fallback to environment variable
api_key = os.getenv("COHERE_API_KEY") or st.secrets["cohere_api_key"]
co = cohere.Client(api_key)

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}):
    """
    Fills the partnership form using Cohere chat endpoint.
    Combines company info, uploaded docs, and manual input into one prompt.
    Returns JSON-formatted string.
    """
    context = f"Company Info:\n{company_info_text}\n\nDocuments:\n{uploaded_docs_text}\n\nManual Input:\n{manual_input}"

    messages = [
        {"role": "system", "content": "You are an expert in corporate partnerships, helping to fill forms accurately."},
        {"role": "user", "content": f"Fill the partnership form based on the following context in JSON matching the template:\n{context}"}
    ]

    try:
        response = co.chat(
            model="command-xlarge-nightly",
            messages=messages,
            max_tokens=1500
        )
        # Cohere chat returns response.generations[0].content
        return response.generations[0].content.strip()
    except Exception as e:
        return f"Error in AI fill: {e}"
