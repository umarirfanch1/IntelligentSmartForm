import os
import json
import requests
import streamlit as st

def fill_form_with_ai(combined_text):
    """
    combined_text: str -> Combined parsed text from URL or uploaded files
    Returns: dict -> JSON of AI-suggested form data
    """
    api_key = st.secrets.get("GROQ", {}).get("api_key")
    if not api_key:
        raise ValueError("Groq API key missing under [GROQ] in secrets.toml")

    # Template JSON structure
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
                "content": "You are an expert in corporate partnerships. Return only valid JSON."
            },
            {
                "role": "user",
                "content": f"""
Fill this JSON with details inferred from the context below.

Template:
{json.dumps(json_template, indent=4)}

Rules:
- Only fill what is explicitly present or safely inferred.
- Unknown values must remain empty strings.
- Do NOT add keys.
- Return ONLY clean JSON.

Context:
{combined_text}
"""
            }
        ],
        "temperature": 0
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=payload
    )

    if response.status_code != 200:
        st.error(f"Groq API Error {response.status_code} — {response.text}")
        return {}

    try:
        out = response.json()["choices"][0]["message"]["content"]
        return json.loads(out)
    except Exception as e:
        st.warning(f"AI returned invalid JSON: {e}")
        st.code(response.json(), language="json")
        return {}
