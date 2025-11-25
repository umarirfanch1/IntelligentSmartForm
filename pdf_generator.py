import pdfkit
from jinja2 import Template

def generate_pdf_from_form(form_data, template_data, output_file="partnership_form.pdf"):
    """
    Generates a PDF from the filled partnership form.
    
    Parameters:
    - form_data: dict containing filled values for all placeholders
    - template_data: dict containing section titles and field labels
    - output_file: filename of the resulting PDF
    """
    
    # Build HTML content for PDF using template_data and form_data
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

    # Generate PDF using pdfkit
    try:
        pdfkit.from_string(html_content, output_file)
        return output_file
    except Exception as e:
        print(f"PDF generation failed: {e}")
        return None
