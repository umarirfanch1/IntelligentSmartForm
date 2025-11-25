import os
import json
import requests
import streamlit as st

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}):
    """
    Uses Groq Llama-3.1 with JSON mode for stable and accurate form filling.
    """
    api_key = st.secrets.get("GROQ", {}).get("api_key")
    if not api_key:
        raise ValueError("Groq API key is missing. Set it in Streamlit secrets under [GROQ].")

    # compact context
    context = f"""
Company Info:
{company_info_text}

Uploaded Documents:
{uploaded_docs_text}

Manual Input:
{manual_input}
"""

    # JSON structure expected
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
        "model": "llama-3.1-70b-versatile",  # BEST for structured extraction
        "response_format": {"type": "json_object"},   # <<< THE FIX
        "messages": [
            {
                "role": "system",
                "content": "You are an expert in corporate partnerships. Return STRICT JSON only."
            },
            {
                "role": "user",
                "content": f"""
Fill the following JSON template using the provided context.

Template:
{json.dumps(json_template, indent=4)}

Rules:
- Only fill values that can be inferred.
- Unknown fields must remain "".
- DO NOT add new keys.
- DO NOT add explanations.
- Return ONLY raw JSON.

Context:
{context}
"""
            }
        ],
        "temperature": 0,
        "max_tokens": 2000
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload
    )

    if response.status_code != 200:
        st.error(f"Groq API Error {response.status_code} — {response.text}")
        return {}

    try:
        content = response.json()["choices"][0]["message"]["content"]
        return json.loads(content)
    except Exception as e:
        st.warning(f"AI returned invalid JSON ({e}).")
        st.json(response.json())  # debugging
        return {}
