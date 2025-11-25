import os
import json
import requests
import streamlit as st

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Uses Groq API to generate pre-filled partnership form suggestions.
    """

    # Retrieve API key from Streamlit secrets if not provided
    if api_key is None:
        api_key = st.secrets.get("GROQ", {}).get("api_key")
        if not api_key:
            raise ValueError("Groq API key is missing. Set it in Streamlit secrets under [GROQ].")

    # Combine all context
    context = f"Company Info:\n{company_info_text}\nDocuments:\n{uploaded_docs_text}\nManual Input:\n{manual_input}"

    # Prompt for Groq model
    prompt = f"""
You are an expert in corporate partnerships. Fill the partnership form in JSON format exactly with these keys:

{{
    "company_name": "",
    "company_url": "",
    "founding_year": "",
    "num_employees": "",
    "hq_location": "",
    "partner_name": "",
    "partnership_type": "",
    "partnership_start_date": "",
    "partnership_goals": "",
    "expected_contributions": "",
    "mission_statement": "",
    "product_overview": "",
    "target_market": "",
    "competitive_advantage": "",
    "investment_amount": "",
    "contract_duration": "",
    "legal_clauses": "",
    "risk_liability": "",
    "additional_notes": "",
    "contact_person": "",
    "contact_email": ""
}}

Use context to infer any missing information. Return ONLY JSON, no explanations.

Context:
{context}
"""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "groq-1",               # Make sure to use the correct Groq model
        "prompt": prompt,
        "max_output_tokens": 1500,
        "temperature": 0.3
    }

    try:
        # Correct Groq endpoint
        response = requests.post("https://api.groq.com/v1/text-generation", headers=headers, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Groq API Error: {e}")
        return {}

    try:
        ai_text = response.json().get("text", "")
        return json.loads(ai_text)
    except Exception as e:
        st.warning(f"AI output is empty or invalid. Please fill manually. ({e})")
        return {}
