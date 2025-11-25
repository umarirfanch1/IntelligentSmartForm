import cohere
import streamlit as st
import json

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Generate AI suggestions for the partnership form using Cohere Chat API.
    """

    if api_key is None:
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing. Set it in Streamlit secrets.")

    co = cohere.Client(api_key)

    # Combine all context
    context = f"Company Info:\n{company_info_text}\n\nDocuments:\n{uploaded_docs_text}\n\nManual Input:\n{json.dumps(manual_input)}"

    # Prompt for AI
    prompt = f"""
You are an expert in corporate partnerships. Your task is to fill the partnership form 
based on the context provided. Return the output strictly in JSON format matching the template placeholders.

Context:
{context}
"""

    try:
        # Using Chat API instead of Generate API
        response = co.chat(
            message=prompt,
            model="command-xlarge-nightly",  # Use the appropriate Chat model
            temperature=0.7,  # Adjust as needed
            max_tokens=1500
        )

        return response.text.strip()

    except Exception as e:
        st.error(f"Unexpected error in AI fill: {e}")
        return "{}"
