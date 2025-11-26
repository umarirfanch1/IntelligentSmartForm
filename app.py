import streamlit as st
import json
import os
import base64
from company_parser import parse_website, parse_uploaded_docs
from pdf_generator import generate_pdf_from_form

# ----------------------------
# Local "LLM" Auto-fill Logic
# ----------------------------
import re

def local_autofill(text):
    """
    Simple regex-based local autofill. Fills fields if present in text, else marks as REQUIRED.
    """
    def find(patterns):
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return "REQUIRED"

    output = {
        "company_name": find([r"Company Name[:\-]\s*(.+)"]),
        "company_url": find([r"(https?://[^\s]+)"]),
        "founding_year": find([r"Founded[:\-]\s*(\d{4})", r"Establish(ed|ment)[:\-]\s*(\d{4})"]),
        "num_employees": find([r"Employees[:\-]\s*(\d+)"]),
        "hq_location": find([r"(Headquarters|HQ)[:\-]\s*(.+)"]),

        "partner_name": find([r"Partner Name[:\-]\s*(.+)"]),
        "partnership_type": find([r"Partnership Type[:\-]\s*(.+)"]),
        "partnership_start_date": find([r"Start Date[:\-]\s*(.+)"]),
        "partnership_goals": find([r"Goals[:\-]\s*(.+)"]),
        "expected_contributions": find([r"Contribution[:\-]\s*(.+)"]),

        "mission_statement": find([r"Mission[:\-]\s*(.+)"]),
        "product_overview": find([r"Product[:\-]\s*(.+)"]),
        "target_market": find([r"Market[:\-]\s*(.+)"]),
        "competitive_advantage": find([r"(Competitive Advantage|USP)[:\-]\s*(.+)"]),

        "investment_amount": find([r"Investment[:\-]\s*(.+)"]),
        "contract_duration": find([r"Contract Duration[:\-]\s*(.+)"]),
        "legal_clauses": find([r"Legal[:\-]\s*(.+)"]),
        "risk_liability": find([r"Risk[:\-]\s*(.+)"]),

        "additional_notes": find([r"Notes[:\-]\s*(.+)"]),
        "contact_person": find([r"Contact Person[:\-]\s*(.+)"]),
        "contact_email": find([r"([\w\.-]+@[\w\.-]+)"])
    }
    return output

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="Intelligent Smart Partnership Form", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4B0082;'>🤝 Intelligent Smart Partnership Form</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#666;'>A prototype by Umar™</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# Initialize session state
# ----------------------------
defaults = {
    'current_step': 0,
    'input_option': None,
    'company_text': "",
    'uploaded_text': "",
    'form_data': {},
    'ai_filled': False,
    'company_parsed': False,
    'docs_parsed': False
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ----------------------------
# Load Template
# ----------------------------
with open("partnership_template.json", "r") as f:
    template = json.load(f)

steps = ["Choose Input Method", "Provide Information", "Auto-Fill & Review", "Preview PDF"]
current_step_index = st.session_state['current_step']
current_step = steps[current_step_index]

# ----------------------------
# Sidebar Step Tracker
# ----------------------------
st.sidebar.header("Steps")
for i, step_name in enumerate(steps):
    st.sidebar.markdown(f"{'✅' if i < current_step_index else '➡️' if i == current_step_index else '❌'} {step_name}")

# ----------------------------
# Step 1: Choose Input Method
# ----------------------------
if current_step == "Choose Input Method":
    st.header("Step 1: Choose Input Method")
    st.session_state['input_option'] = st.radio(
        "Choose how to fill the form:",
        ("Manual Form Input", "AI Auto-Fill (URL and/or PDF)")
    )

# ----------------------------
# Step 2: Provide Information
# ----------------------------
elif current_step == "Provide Information":
    st.header("Step 2: Provide Information")
    option = st.session_state['input_option']

    if option == "AI Auto-Fill (URL and/or PDF)":
        url = st.text_input("Paste Company Website URL (optional)")
        files = st.file_uploader("Upload PDFs or Word Docs (optional)", type=["pdf", "docx"], accept_multiple_files=True)

        if url and not st.session_state['company_parsed']:
            with st.spinner("Parsing website..."):
                st.session_state['company_text'] = parse_website(url)
                st.session_state['company_parsed'] = True
                st.success(f"Parsed {len(st.session_state['company_text'].split())} words from website.")

        if files and not st.session_state['docs_parsed']:
            with st.spinner("Parsing uploaded files..."):
                st.session_state['uploaded_text'] = parse_uploaded_docs(files)
                st.session_state['docs_parsed'] = True
                st.success(f"Parsed {len(st.session_state['uploaded_text'].split())} words from documents.")

    elif option == "Manual Form Input":
        st.info("You will fill the form manually in the next step.")

# ----------------------------
# Step 3: Auto-Fill & Review Form
# ----------------------------
elif current_step == "Auto-Fill & Review":
    st.header("Step 3: Auto-Fill & Review Form")
    option = st.session_state['input_option']

    combined_text = ""
    if st.session_state.get('company_text'):
        combined_text += st.session_state['company_text'].strip()
    if st.session_state.get('uploaded_text'):
        if combined_text:
            combined_text += "\n\n"
        combined_text += st.session_state['uploaded_text'].strip()

    if option == "AI Auto-Fill (URL and/or PDF)":
        if st.button("Auto-Fill Form") and not st.session_state['ai_filled']:
            if combined_text:
                with st.spinner("Auto-filling form..."):
                    ai_output = local_autofill(combined_text)
                    # Map output to template
                    st.session_state['form_data'] = {}
                    for section_key, section in template.items():
                        st.session_state['form_data'][section_key] = {}
                        for field_key in section['fields']:
                            st.session_state['form_data'][section_key][field_key] = ai_output.get(field_key, "REQUIRED")
                    st.session_state['ai_filled'] = True
                    st.success("Form auto-filled! Missing fields are marked as REQUIRED.")
            else:
                st.warning("No data available to auto-fill.")

    # Show editable form
    for section_key, section in template.items():
        with st.expander(section['title'], expanded=True):
            st.markdown(section.get('description', ''))
            st.session_state['form_data'].setdefault(section_key, {})
            for field_key, field_label in section['fields'].items():
                prefill = st.session_state['form_data'][section_key].get(field_key, "")
                st.session_state['form_data'][section_key][field_key] = st.text_area(
                    field_label, value=prefill, height=60, key=f"{section_key}_{field_key}"
                )

# ----------------------------
# Step 4: Preview PDF & Download
# ----------------------------
elif current_step == "Preview PDF":
    st.header("Step 4: Preview PDF & Download")
    if st.session_state['form_data']:
        pdf_path = "partnership_form_preview.pdf"
        with st.spinner("Generating PDF..."):
            success = generate_pdf_from_form(st.session_state['form_data'], template, pdf_path)

        if success and os.path.exists(pdf_path):
            st.success("PDF generated successfully!")
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()
            st.download_button(
                label="Download PDF",
                data=pdf_bytes,
                file_name="partnership_form.pdf",
                mime="application/pdf"
            )
        else:
            st.error("Failed to generate PDF. Check logs for details.")
    else:
        st.warning("Form data is empty. Fill or auto-fill form first.")

# ----------------------------
# Navigation Buttons
# ----------------------------
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Back") and current_step_index > 0:
        st.session_state['current_step'] -= 1
        st.rerun()

with col2:
    if st.button("Next") and current_step_index < len(steps)-1:
        st.session_state['current_step'] += 1
        st.rerun()
