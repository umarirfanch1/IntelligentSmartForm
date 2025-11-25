import streamlit as st
import requests
import json
import os
from utils.parser import parse_website, parse_uploaded_docs
from utils.ai_fill import fill_form_with_ai
from utils.pdf_generator import generate_pdf_from_form
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64

# ----------------------------
# Streamlit Page Setup
# ----------------------------
st.set_page_config(page_title="Intelligent Smart Partnership Form", layout="wide")
st.markdown("<h1 style='text-align:center;color:#4B0082;'>🤝 Intelligent Smart Partnership Form</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#666;'>A prototype by Umar™</p>", unsafe_allow_html=True)
st.markdown("---")

# ----------------------------
# Load Template
# ----------------------------
template_path = "partnership_template.json"
with open(template_path, "r") as f:
    template = json.load(f)

# Sidebar for steps
st.sidebar.header("Steps")
steps = ["Choose Input Method", "Provide Information", "AI Pre-Fill & Review", "Edit Form", "Preview PDF"]
current_step = st.sidebar.radio("Current Step", steps)

company_text = ""
uploaded_text = ""
manual_input = {}
form_data = {}

# ----------------------------
# Step 1: Choose Input Method
# ----------------------------
if current_step == "Choose Input Method":
    st.header("Step 1: Choose Input Method")
    input_option = st.radio(
        "How would you like to provide company information?",
        ("Paste Company URL", "Upload Supporting Documents", "Manual Form Input")
    )
    st.session_state['input_option'] = input_option

# ----------------------------
# Step 2: Provide Information
# ----------------------------
elif current_step == "Provide Information":
    st.header("Step 2: Provide Information")
    input_option = st.session_state.get('input_option', "Manual Form Input")

    if input_option == "Paste Company URL":
        company_url = st.text_input("Paste Company Website URL")
        if company_url:
            st.info("Parsing website content...")
            company_text = parse_website(company_url)
            st.success(f"Website parsed! {len(company_text.split())} words extracted.")

    elif input_option == "Upload Supporting Documents":
        uploaded_files = st.file_uploader("Upload PDFs or Word Docs", type=["pdf","docx"], accept_multiple_files=True)
        if uploaded_files:
            uploaded_text = parse_uploaded_docs(uploaded_files)
            st.success(f"{len(uploaded_files)} file(s) parsed! {len(uploaded_text.split())} words extracted.")

    elif input_option == "Manual Form Input":
        st.info("You will fill the partnership form manually in the next step.")

# ----------------------------
# Step 3 & 4: AI Pre-Fill & Review Form
# ----------------------------
elif current_step in ["AI Pre-Fill & Review", "Edit Form"]:
    st.header("Step 3 & 4: AI Pre-Fill & Review Form")

    # Run AI Pre-fill
    if st.button("Auto-Fill Form with AI"):
        with st.spinner("Generating AI suggestions..."):
            form_data_str = fill_form_with_ai(
                company_info_text=company_text,
                uploaded_docs_text=uploaded_text,
                manual_input=manual_input
            )
            # Convert string output to dict
            import ast
            try:
                form_data = ast.literal_eval(form_data_str) if isinstance(form_data_str, str) else form_data_str
            except:
                st.warning("AI output could not be parsed, please check manually.")
        st.success("AI has generated initial suggestions!")

    # Show editable form
    for section_key, section in template.items():
        with st.expander(section['title'], expanded=True):
            st.markdown(section.get('description',''))
            form_data.setdefault(section_key, {})
            for field_key, field_label in section['fields'].items():
                prefill = form_data[section_key].get(field_key, "")
                form_data[section_key][field_key] = st.text_area(
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
    if form_data:
        with st.spinner("Generating PDF..."):
            pdf_file = generate_pdf_from_form(form_data, template, output_file="partnership_form_preview.pdf")
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
                attachment = Attachment()
                attachment.file_content = FileContent(encoded_file)
                attachment.file_type = FileType("application/pdf")
                attachment.file_name = FileName("partnership_form.pdf")
                attachment.disposition = Disposition("attachment")

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
