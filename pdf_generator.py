import pdfkit
from jinja2 import Template

def generate_pdf_from_form(form_data, template_data, output_file="partnership_form.pdf"):
    """
    Generates a PDF from the filled partnership form.
    Returns True if successful, False otherwise.
    """
    html_content = "<html><head><meta charset='utf-8'><style>"
    html_content += """
    body { font-family: Arial, sans-serif; margin: 30px; }
    h1 { text-align: center; color: #2F4F4F; }
    h2 { color: #4B0082; border-bottom: 1px solid #ccc; padding-bottom: 5px; }
    p { margin: 5px 0; }
    .field-label { font-weight: bold; }
    .field-value { margin-left: 10px; }
    """
    html_content += "</style></head><body>"
    html_content += "<h1>Partnership Form</h1>"

    for section_key, section in template_data.items():
        html_content += f"<h2>{section['title']}</h2>"
        html_content += f"<p>{section.get('description','')}</p>"
        for field_key, field_label in section['fields'].items():
            value = form_data.get(section_key, {}).get(field_key, "")
            html_content += f"<p><span class='field-label'>{field_label}</span>: <span class='field-value'>{value}</span></p>"

    html_content += "</body></html>"

    try:
        pdfkit.from_string(html_content, output_file)
        return True
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        return False
2️⃣ Check if PDF was generated before opening
Update Step 4 in app.py:

python
Copy code
pdf_path = "partnership_form_preview.pdf"
with st.spinner("Generating PDF..."):
    success = generate_pdf_from_form(st.session_state['form_data'], template, pdf_path)

if success and os.path.exists(pdf_path):
    st.success("PDF generated!")
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
