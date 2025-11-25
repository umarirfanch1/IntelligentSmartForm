import os
import json
import requests
import streamlit as st

def fill_form_with_ai(combined_text: str) -> dict:
    """
    Send combined text to Groq API and return structured JSON for the form.
    Args:
        combined_text (str): Parsed content from URL or uploaded files.
    Returns:
        dict: AI-generated form data
    """
    api_key = st.secrets.get("GROQ", {}).get("api_key")
    if not api_key:
        raise ValueError("Groq API key missing under [GROQ] in secrets.toml")

    json_template = {
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
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in corporate partnerships. Return ONLY valid JSON."
            },
            {
                "role": "user",
                "content": f"""
Fill the following JSON template using ONLY the information explicitly present or safely inferred
from the context below. Do NOT invent data. Keep unknown values empty.

Template:
{json.dumps(json_template, indent=4)}

Context:
{combined_text}
"""
            }
        ],
        "temperature": 0
    }

    try:
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        resp.raise_for_status()

        content = resp.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        st.error(f"Groq API call failed: {e}")
        return {}
