import cohere
import streamlit as st
import json

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Generate AI suggestions for the partnership form using Cohere Chat API (latest SDK).
    """

    if api_key is None:
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing. Set it in Streamlit secrets.")

    co = cohere.Client(api_key)

    # Combine all context
    context = f"Company Info:\n{company_info_text}\n\nDocuments:\n{uploaded_docs_text}\n\nManual Input:\n{manual_input}"

    # Prompt for AI
    prompt = f"""
You are an expert in corporate partnerships. Your task is to fill the partnership form 
based on the context provided. Return the output strictly in JSON format matching the template placeholders.

Context:
{context}
"""

    try:
        # Correct usage with latest SDK
        response = co.chat(
            model="command-xlarge-nightly",
            message=[  # must be plural
                {"role": "system", "content": "You are an expert in corporate partnerships."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1500
        )

        # Correct way to get text
        return response.generations[0].text.strip()

    except Exception as e:
        st.error(f"Unexpected error in AI fill: {e}")
        return "{}"
