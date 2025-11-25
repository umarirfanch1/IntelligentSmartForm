# ai_fill.py
import openai
import streamlit as st
import json

def extract_json(text):
    """Extract JSON object from AI output."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except:
                return {}
        return {}

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Fill partnership form using OpenAI GPT-3.5/4.
    Returns a dict ready for auto-filling the form.
    """
    if api_key is None:
        api_key = st.secrets.get("OpenAPI", {}).get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is missing in Streamlit secrets.")

    openai.api_key = api_key

    context = (
        f"Company Info:\n{company_info_text}\n\n"
        f"Documents:\n{uploaded_docs_text}\n\n"
        f"Manual Input:\n{manual_input}"
    )

    prompt = f"""
You are an expert in corporate partnerships. Fill all the fields for the partnership form
based on the context below. Return STRICT JSON matching the following keys exactly:

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

Do NOT add explanations. Use context to fill as much as possible.

Context:
{context}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1500
        )

        ai_text = response['choices'][0]['message']['content'].strip()
        return extract_json(ai_text)

    except Exception as e:
        st.error(f"Error generating AI suggestions: {e}")
        return {}
