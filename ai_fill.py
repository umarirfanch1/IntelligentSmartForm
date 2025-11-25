import os
import json
import requests
import streamlit as st

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}):
    """
    Uses Groq API (OpenAI-compatible) to generate pre-filled partnership form suggestions.
    """
    # Get API key from secrets
    api_key = st.secrets.get("GROQ", {}).get("api_key")
    if not api_key:
        raise ValueError("Groq API key is missing. Set it in Streamlit secrets under [GROQ].")

    # Combine context
    context = f"Company Info:\n{company_info_text}\nDocuments:\n{uploaded_docs_text}\nManual Input:\n{manual_input}"

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

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        # FIXED: use a valid Groq model
        "model": "llama-3.1-8b-instant",
        # OR use: "llama-3.1-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are an expert in corporate partnerships."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0,
        "max_tokens": 2000
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        st.error(f"Groq API Error: {response.status_code} — {response.text}")
        return {}

    try:
        text = response.json()["choices"][0]["message"]["content"].strip()
        return json.loads(text)
    except Exception as e:
        st.warning(f"AI output is empty or invalid JSON. Please fill manually. ({e})")
        return {}
