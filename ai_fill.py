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
    Generate AI suggestions for the partnership form using Cohere Chat API.
    Returns a dict ready to fill the partnership form fields.
    """

    if api_key is None:
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing in Streamlit secrets.")

    co = cohere.Client(api_key)

    # Combine all context
    context = (
        f"Company Info:\n{company_info_text}\n\n"
        f"Documents:\n{uploaded_docs_text}\n\n"
        f"Manual Input:\n{manual_input}"
    )

    # Prompt with all placeholders
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

    try:
        # Correct chat call using messages
        response = co.chat(
            model="command-xlarge-nightly",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3
        )

        ai_output = response.output_text.strip()
        json_data = extract_json(ai_output)

        # Ensure all keys exist (fill missing ones with empty string)
        required_keys = [
            "company_name", "company_url", "founding_year", "num_employees", "hq_location",
            "partner_name", "partnership_type", "partnership_start_date", "partnership_goals",
            "expected_contributions", "mission_statement", "product_overview", "target_market",
            "competitive_advantage", "investment_amount", "contract_duration", "legal_clauses",
            "risk_liability", "additional_notes", "contact_person", "contact_email"
        ]

        for key in required_keys:
            if key not in json_data:
                json_data[key] = ""

        return json_data

    except Exception as e:
        st.error(f"Error generating AI suggestions: {e}")
        return {}
