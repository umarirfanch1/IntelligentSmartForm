import streamlit as st
import openai
import json
import re

def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            return json.loads(match.group())
    except json.JSONDecodeError:
        pass
    return {}

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}):
    api_key = st.secrets["OpenAPI"]["api_key"]
    if not api_key:
        raise ValueError("OpenAI API key is missing in Streamlit secrets.")
    openai.api_key = api_key

    context = (
        f"Company Info:\n{company_info_text}\n\n"
        f"Documents:\n{uploaded_docs_text}\n\n"
        f"Manual Input:\n{manual_input}"
    )

    prompt = f"""
You are an expert in corporate partnerships. Based on the provided context,
fill the fields of the partnership form with the most relevant information.

Return the output STRICTLY in JSON format with EXACTLY the following keys:

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

Do NOT add explanations, commentary, or extra fields.
Use the context to infer any missing data.

Context:
{context}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    ai_text = response["choices"][0]["message"]["content"].strip()
    return extract_json(ai_text)
