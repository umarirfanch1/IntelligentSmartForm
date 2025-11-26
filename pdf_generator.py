from fpdf import FPDF

def generate_pdf_from_form(form_data, template, output_path="partnership_form_preview.pdf"):
    """
    Generate a simple PDF from form data.
    Returns True if successful, else False.
    """
    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "Partnership Form", ln=True, align="C")
        pdf.ln(10)

        pdf.set_font("Arial", "", 12)
        for section_key, section in form_data.items():
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 8, section_key, ln=True)
            pdf.set_font("Arial", "", 12)
            for field_key, value in section.items():
                pdf.multi_cell(0, 6, f"{field_key}: {value}")
            pdf.ln(5)

        pdf.output(output_path)
        return True
    except Exception as e:
        print(f"[ERROR] PDF generation failed: {e}")
        return False
