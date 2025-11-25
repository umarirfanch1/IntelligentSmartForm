import cohere
import streamlit as st

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Generate AI suggestions for the partnership form using Cohere.
    Inputs:
        - company_info_text: str from company website
        - uploaded_docs_text: str from uploaded files
        - manual_input: dict of any manual inputs
        - api_key: Cohere API key (recommended to pass from Streamlit secrets)
    Returns:
        - JSON string matching the template placeholders
    """

    if api_key is None:
        # Fallback: try to read from Streamlit secrets
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing. Set it in Streamlit secrets.")

    co = cohere.Client(api_key)

    # Combine all context
    context = f"Company Info:\n{company_info_text}\n\nDocuments:\n{uploaded_docs_text}\n\nManual Input:\n{manual_input}"

    prompt = f"""
You are an expert in corporate partnerships. Fill the partnership form using the following context:
{context}

Return output in JSON format matching the template placeholders exactly.
"""

    try:
        response = co.generate(
            model="xlarge",
            prompt=prompt,
            max_tokens=1500
        )
        return response.generations[0].text.strip()
    except cohere.error.CohereError as e:
        st.error(f"Cohere API error: {e}")
        return "{}"
    except Exception as e:
        st.error(f"Unexpected error in AI fill: {e}")
        return "{}"
