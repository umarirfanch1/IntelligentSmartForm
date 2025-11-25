import cohere
import streamlit as st
import json
import re

def extract_json(text):
    """Extract first JSON object from AI output."""
    try:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return {}

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Generate AI suggestions for the partnership form using Cohere Chat API (latest SDK).
    Returns a dict ready to fill the form.
    """

    if api_key is None:
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing. Set it in Streamlit secrets.")

    co = cohere.Client(api_key)

    # Combine all context
    context = f"Company Info:\n{company_info_text}\n\nDocuments:\n{uploaded_docs_text}\n\nManual Input:\n{manual_input}"

    # Updated Prompt for AI
    prompt = f"""
You are an expert in corporate partnerships. Your task is to fill the partnership form 
based on the context provided. Return the output strictly in JSON format matching the 
following structure (without any additional root key like "partnership_form"):

{{
    "company_name": "",
    "contact_name": "",
    "contact_email": "",
    "contact_phone": "",
    "partnership_type": "",
    "products_services": [],
    "promotions": [],
    "trade_in_program": {{
        "name": "",
        "description": "",
        "terms_conditions": ""
    }},
    "additional_notes": ""
}}

Context:
{context}
"""

    try:
        # Correct Chat API usage
        response = co.chat(
            model="command-xlarge-nightly",  # Cohere Chat model
            message=prompt,
            max_tokens=1500,
            temperature=0.7
        )

        # Extract only JSON from AI output
        output_text = response.text.strip()
        return extract_json(output_text)

    except Exception as e:
        st.error(f"Unexpected error in AI fill: {e}")
        return {}
