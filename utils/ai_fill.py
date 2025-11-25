import cohere

co = cohere.Client("1Kt9hhRJVYrwahPOAVwca3KLKds67nIdZOsT5jcp")

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}):
    # Combine all context into one prompt
    context = f"Company Info:\n{company_info_text}\n\nDocuments:\n{uploaded_docs_text}\n\nManual Input:\n{manual_input}"
    prompt = f"""
You are an expert in corporate partnerships. Fill the partnership form using the following context:
{context}

Return output in JSON format matching the template placeholders exactly.
"""
    response = co.generate(
        model="xlarge",
        prompt=prompt,
        max_tokens=1500
    )
    return response.generations[0].text.strip()
