import streamlit as st
import json
import os
import base64
from company_parser import parse_website, parse_uploaded_docs
from ai_fill import fill_form_with_ai
from pdf_generator import generate_pdf_from_form
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

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
    'manual_input': {},
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

steps = ["Choose Input Method", "Provide Information", "AI Pre-Fill & Review", "Edit Form", "Preview PDF"]
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
        "How would you like to provide company information?",
        ("Paste Company URL", "Upload Supporting Documents", "Manual Form Input")
    )

# ----------------------------
# Step 2: Provide Information
# ----------------------------
elif current_step == "Provide Information":
    st.header("Step 2: Provide Information")
    option = st.session_state['input_option']

    if not option:
        st.warning("Please select an input method before proceeding.")
    else:
        if option == "Paste Company URL":
            url = st.text_input("Paste Company Website URL")
            if url and not st.session_state['company_parsed']:
                with st.spinner("Parsing website..."):
                    st.session_state['company_text'] = parse_website(url)
                    st.session_state['company_parsed'] = True
                    st.success(f"Parsed {len(st.session_state['company_text'].split())} words from website.")

        elif option == "Upload Supporting Documents":
            files = st.file_uploader("Upload PDFs or Word Docs", type=["pdf", "docx"], accept_multiple_files=True)
            if files and not st.session_state['docs_parsed']:
                with st.spinner("Parsing uploaded files..."):
                    st.session_state['uploaded_text'] = parse_uploaded_docs(files)
                    st.session_state['docs_parsed'] = True
                    st.success(f"Parsed {len(st.session_state['uploaded_text'].split())} words from documents.")

        elif option == "Manual Form Input":
            st.info("Manual input selected. You will fill the form manually in the next step.")

# ----------------------------
# Step 3 & 4: AI Pre-Fill & Review
# ----------------------------
elif current_step in ["AI Pre-Fill & Review", "Edit Form"]:
    st.header("Step 3 & 4: AI Pre-Fill & Review Form")
    option = st.session_state['input_option']

    if option in ["Paste Company URL", "Upload Supporting Documents"]:
        combined_text = ""
        if option == "Paste Company URL":
            combined_text += st.session_state.get('company_text', '')
        if option == "Upload Supporting Documents":
            combined_text += "\n" + st.session_state.get('uploaded_text', '')

        if combined_text.strip() and not st.session_state['ai_filled']:
            if st.button("Auto-Fill Form with AI"):
                with st.spinner("Generating AI suggestions..."):
                    ai_output = fill_form_with_ai(combined_text)
                    if ai_output:
                        def safe(k): return ai_output.get(k, "")
                        st.session_state['form_data'] = {
                            "Company Information": {
                                "company_name": safe("company_name"),
                                "company_url": safe("company_url"),
                                "founding_year": safe("founding_year"),
                                "num_employees": safe("num_employees"),
                                "hq_location": safe("hq_location")
                            },
                            "Partnership Details": {
                                "partner_name": safe("partner_name"),
                                "partnership_type": safe("partnership_type"),
                                "partnership_start_date": safe("partnership_start_date"),
                                "partnership_goals": safe("partnership_goals"),
                                "expected_contributions": safe("expected_contributions")
                            },
                            "Product / Service Description": {
                                "mission_statement": safe("mission_statement"),
                                "product_overview": safe("product_overview"),
                                "target_market": safe("target_market"),
                                "competitive_advantage": safe("competitive_advantage")
                            },
                            "Legal & Financial Information": {
                                "investment_amount": safe("investment_amount"),
                                "contract_duration": safe("contract_duration"),
                                "legal_clauses": safe("legal_clauses"),
                                "risk_liability": safe("risk_liability")
                            },
                            "Miscellaneous / Notes": {
                                "additional_notes": safe("additional_notes"),
                                "contact_person": safe("contact_person"),
                                "contact_email": safe("contact_email")
                            }
                        }
                        st.session_state['ai_filled'] = True
                        st.success("AI has populated the form!")
                        st.experimental_rerun()
                    else:
                        st.warning("AI returned empty or invalid output.")
    elif option == "Manual Form Input":
        st.info("Manual input selected → skipping AI auto-fill.")

    # Editable form UI
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
# Step 5: PDF Preview & Send
# ----------------------------
elif current_step == "Preview PDF":
    st.header("Step 5: Preview PDF & Send")
    if st.session_state['form_data']:
        with st.spinner("Generating PDF..."):
            generate_pdf_from_form(st.session_state['form_data'], template, "partnership_form_preview.pdf")
        st.success("PDF generated!")
        st.components.v1.iframe("partnership_form_preview.pdf", height=600)

        recipient = st.text_input("Recipient Email:", "reachingjust@gmail.com")
        if st.button("Send PDF via SendGrid"):
            try:
                sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
                with open("partnership_form_preview.pdf", "rb") as f:
                    data = f.read()
                encoded = base64.b64encode(data).decode()

                attachment = Attachment(
                    file_content=FileContent(encoded),
                    file_type=FileType("application/pdf"),
                    file_name=FileName("partnership_form.pdf"),
                    disposition=Disposition("attachment")
                )
                mail = Mail(
                    from_email="reachingjust@gmail.com",
                    to_emails=recipient,
                    subject="Completed Partnership Form",
                    plain_text_content="Please find the completed partnership form attached."
                )
                mail.attachment = attachment
                resp = sg.send(mail)
                st.success(f"PDF sent! Status code: {resp.status_code}")
            except Exception as e:
                st.error(f"Failed to send email: {e}")
    else:
        st.warning("Form data is empty. Fill or generate form first.")

# ----------------------------
# Navigation Buttons
# ----------------------------
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Back") and current_step_index > 0:
        st.session_state['current_step'] -= 1
        st.experimental_rerun()

with col2:
    if st.button("Next") and current_step_index < len(steps)-1:
        if current_step == "Choose Input Method" and not st.session_state['input_option']:
            st.warning("Select an input method first.")
        elif current_step == "Provide Information":
            option = st.session_state['input_option']
            if option == "Paste Company URL" and not st.session_state['company_text']:
                st.warning("Provide a valid company URL.")
            elif option == "Upload Supporting Documents" and not st.session_state['uploaded_text']:
                st.warning("Upload at least one document.")
            else:
                st.session_state['current_step'] += 1
                st.experimental_rerun()
        else:
            st.session_state['current_step'] += 1
            st.experimental_rerun()
