import streamlit as st
import json
import os
import base64
from company_parser import parse_website, parse_uploaded_docs
from ai_fill import fill_form_with_ai  # Make sure ai_fill.py uses Groq API
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
for key, default in {
    'current_step': 0,
    'input_option': None,
    'company_text': "",
    'uploaded_text': "",
    'form_data': {},
    'manual_input': {},
    'ai_filled': False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ----------------------------
# Load Template
# ----------------------------
template_path = "partnership_template.json"
with open(template_path, "r") as f:
    template = json.load(f)

steps = ["Choose Input Method", "Provide Information", "AI Pre-Fill & Review", "Edit Form", "Preview PDF"]
current_step_index = st.session_state['current_step']
current_step = steps[current_step_index]

# ----------------------------
# Sidebar Step Tracker
# ----------------------------
st.sidebar.header("Steps")
for i, step_name in enumerate(steps):
    st.sidebar.markdown(
        f"{'✅' if i < current_step_index else '➡️' if i == current_step_index else '❌'} {step_name}"
    )

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
    input_option = st.session_state.get('input_option')

    if not input_option:
        st.warning("Please select an input method before proceeding.")
    else:
        if input_option == "Paste Company URL":
            company_url = st.text_input("Paste Company Website URL", key="company_url_input")
            if company_url:
                if 'company_parsed' not in st.session_state or not st.session_state['company_parsed']:
                    with st.spinner("Parsing website content..."):
                        st.session_state['company_text'] = parse_website(company_url)
                        st.session_state['company_parsed'] = True
                        st.success(f"Website parsed! {len(st.session_state['company_text'].split())} words extracted.")

        elif input_option == "Upload Supporting Documents":
            uploaded_files = st.file_uploader(
                "Upload PDFs or Word Docs", type=["pdf", "docx"], accept_multiple_files=True, key="uploaded_files_input"
            )
            if uploaded_files:
                if 'docs_parsed' not in st.session_state or not st.session_state['docs_parsed']:
                    with st.spinner("Parsing uploaded files..."):
                        st.session_state['uploaded_text'] = parse_uploaded_docs(uploaded_files)
                        st.session_state['docs_parsed'] = True
                        st.success(f"{len(uploaded_files)} file(s) parsed! {len(st.session_state['uploaded_text'].split())} words extracted.")
        elif input_option == "Manual Form Input":
            st.info("You will fill the partnership form manually in the next step.")

# ----------------------------
# Step 3 & 4: AI Pre-Fill & Review Form
# ----------------------------
elif current_step in ["AI Pre-Fill & Review", "Edit Form"]:
    st.header("Step 3 & 4: AI Pre-Fill & Review Form")

    if not st.session_state['ai_filled']:
        if st.button("Auto-Fill Form with AI"):
            with st.spinner("Generating AI suggestions with Groq API..."):
                ai_output = fill_form_with_ai(
                    company_info_text=st.session_state['company_text'],
                    uploaded_docs_text=st.session_state['uploaded_text'],
                    manual_input=st.session_state['manual_input']
                )

                if isinstance(ai_output, dict) and ai_output:
                    def safe(key):
                        return ai_output.get(key, "")

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
                    st.success("AI has generated initial suggestions!")
                    st.experimental_rerun()
                else:
                    st.warning("AI output is empty or invalid. Please fill manually.")

    # Editable Form UI
    for section_key, section in template.items():
        with st.expander(section['title'], expanded=True):
            st.markdown(section.get('description', ''))
            st.session_state['form_data'].setdefault(section_key, {})
            for field_key, field_label in section['fields'].items():
                prefill = st.session_state['form_data'][section_key].get(field_key, "")
                st.session_state['form_data'][section_key][field_key] = st.text_area(
                    field_label,
                    value=prefill,
                    height=60,
                    key=f"{section_key}_{field_key}"
                )

# ----------------------------
# Step 5: Preview PDF & Send
# ----------------------------
elif current_step == "Preview PDF":
    st.header("Step 5: Preview PDF & Send")
    if st.session_state['form_data']:
        with st.spinner("Generating PDF..."):
            pdf_file = generate_pdf_from_form(
                st.session_state['form_data'],
                template,
                output_file="partnership_form_preview.pdf"
            )
        st.success("PDF generated!")
        st.markdown("### PDF Preview")
        st.components.v1.iframe("partnership_form_preview.pdf", height=600)

        recipient_email = st.text_input("Recipient Email:", "reachingjust@gmail.com")

        if st.button("Send PDF via SendGrid"):
            try:
                sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
                with open("partnership_form_preview.pdf", "rb") as f:
                    data = f.read()
                encoded_file = base64.b64encode(data).decode()
                attachment = Attachment(
                    file_content=FileContent(encoded_file),
                    file_type=FileType("application/pdf"),
                    file_name=FileName("partnership_form.pdf"),
                    disposition=Disposition("attachment")
                )
                message = Mail(
                    from_email="reachingjust@gmail.com",
                    to_emails=recipient_email,
                    subject="Completed Partnership Form",
                    plain_text_content="Please find the completed partnership form attached."
                )
                message.attachment = attachment
                response = sg.send(message)
                st.success(f"PDF sent to {recipient_email}! Status code: {response.status_code}")
            except Exception as e:
                st.error(f"Failed to send email: {e}")
    else:
        st.warning("Form data is empty. Please fill or auto-generate the form first.")

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
            st.warning("Please select an input method before proceeding.")
        elif current_step == "Provide Information":
            input_option = st.session_state['input_option']
            if input_option == "Paste Company URL" and not st.session_state['company_text']:
                st.warning("Please provide a valid company URL and parse it.")
            elif input_option == "Upload Supporting Documents" and not st.session_state['uploaded_text']:
                st.warning("Please upload and parse at least one document.")
            else:
                st.session_state['current_step'] += 1
                st.experimental_rerun()
        else:
            st.session_state['current_step'] += 1
            st.experimental_rerun()
