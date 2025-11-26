import streamlit as st
import json
import os
import base64
from company_parser import parse_website, parse_uploaded_docs
from pdf_generator import generate_pdf_from_form
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# ----------------------------
# Local LLM Auto-Fill Function
# ----------------------------
def local_autofill(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    output = {}

    def search_keywords(keywords):
        for line in lines:
            for kw in keywords:
                if kw.lower() in line.lower():
                    return line
        return "REQUIRED"

    # Section 1: Company Info
    output['company_name'] = search_keywords(["company name", "about us"])
    output['company_url'] = search_keywords(["http://", "https://"])
    output['founding_year'] = search_keywords(["founded", "established", "incorporated"])
    output['num_employees'] = search_keywords(["employee", "team size"])
    output['hq_location'] = search_keywords(["headquarters", "located in", "office in"])

    # Section 2: Partnership Details
    output['partner_name'] = search_keywords(["partner", "collaboration"])
    output['partnership_type'] = search_keywords(["partnership type", "type of partnership"])
    output['partnership_start_date'] = search_keywords(["start date", "partnership begins"])
    output['partnership_goals'] = search_keywords(["goal", "objective", "aim"])
    output['expected_contributions'] = search_keywords(["contribution", "responsibility"])

    # Section 3: Product / Service Description
    output['mission_statement'] = search_keywords(["mission", "purpose"])
    output['product_overview'] = search_keywords(["product", "service overview"])
    output['target_market'] = search_keywords(["target market", "customer"])
    output['competitive_advantage'] = search_keywords(["competitive advantage", "USP"])

    # Section 4: Legal & Financial
    output['investment_amount'] = search_keywords(["investment", "funding"])
    output['contract_duration'] = search_keywords(["contract duration", "term"])
    output['legal_clauses'] = search_keywords(["legal", "clause"])
    output['risk_liability'] = search_keywords(["risk", "liability"])

    # Section 5: Misc / Notes
    output['additional_notes'] = search_keywords(["note", "remark"])
    output['contact_person'] = search_keywords(["contact person", "contact"])
    output['contact_email'] = search_keywords(["@", "email"])

    return output

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="Intelligent Smart Partnership Form", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4B0082;'>🤝 Intelligent Smart Partnership Form</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#666;'>A prototype by Umar™</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# Initialize Session State
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
                st.success(f"Parsed {len(st.session_state['uploaded_text'].split())} words from uploaded documents.")

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
                    # Map output to form
                    st.session_state['form_data'] = {}
                    for section_key, section in template.items():
                        st.session_state['form_data'][section_key] = {}
                        for field_key in section['fields'].keys():
                            st.session_state['form_data'][section_key][field_key] = ai_output.get(field_key, "REQUIRED")
                    st.session_state['ai_filled'] = True
                    st.success("Form auto-filled! Missing fields are marked as REQUIRED.")
            else:
                st.warning("No data available to auto-fill.")

    # Show editable form in all cases
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
# Step 4: PDF Preview & Send
# ----------------------------
elif current_step == "Preview PDF":
    st.header("Step 4: Preview PDF & Send")
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
        st.rerun()

with col2:
    if st.button("Next") and current_step_index < len(steps)-1:
        st.session_state['current_step'] += 1
        st.rerun()
