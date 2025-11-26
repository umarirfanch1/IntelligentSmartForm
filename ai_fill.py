import re

def fill_form_with_ai(combined_text: str) -> dict:
    """
    Local 'LLM' for auto-filling partnership form fields.
    Fills fields if info is present in combined_text from URL + PDFs.
    Marks missing fields as empty.
    """
    text = combined_text.lower()  # normalize text
    
    def find(patterns):
        """Try multiple patterns, return first match or empty"""
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
        return ""

    # Section 1: Company Information
    company_name = find([r"company name[:\s]+([a-zA-Z0-9 &]+)"])
    company_url = find([r"(https?://[^\s]+)"])
    founding_year = find([r"founded[:\s]+(\d{4})", r"established[:\s]+(\d{4})"])
    num_employees = find([r"(\d{1,5}) employees"])
    hq_location = find([r"headquarters[:\s]+([a-zA-Z ,]+)"])

    # Section 2: Partnership Details
    partner_name = find([r"partner[:\s]+([a-zA-Z0-9 &]+)"])
    partnership_type = find([r"(strategic|financial|operational|other)"])
    partnership_start_date = find([r"(?:start|begin) date[:\s]+(\d{4}-\d{2}-\d{2})"])
    partnership_goals = find([r"goals[:\s]+(.{5,100})"])
    expected_contributions = find([r"expected contribution[:\s]+(.{5,100})"])

    # Section 3: Product / Service Description
    mission_statement = find([r"mission[:\s]+(.{5,100})"])
    product_overview = find([r"product[:\s]+(.{5,100})", r"service[:\s]+(.{5,100})"])
    target_market = find([r"target market[:\s]+(.{2,50})"])
    competitive_advantage = find([r"competitive advantage[:\s]+(.{2,50})"])

    # Section 4: Legal & Financial Information
    investment_amount = find([r"(?:investment|funding)[:\s]+([$\d,]+)"])
    contract_duration = find([r"(?:contract duration|terms)[:\s]+(.{2,50})"])
    legal_clauses = find([r"(?:legal clauses|obligations)[:\s]+(.{2,100})"])
    risk_liability = find([r"(?:risk|liability)[:\s]+(.{2,100})"])

    # Section 5: Misc / Notes
    additional_notes = find([r"notes[:\s]+(.{2,100})"])
    contact_person = find([r"contact[:\s]+([a-zA-Z ]+)"])
    contact_email = find([r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"])

    return {
        "company_name": company_name,
        "company_url": company_url,
        "founding_year": founding_year,
        "num_employees": num_employees,
        "hq_location": hq_location,
        "partner_name": partner_name,
        "partnership_type": partnership_type,
        "partnership_start_date": partnership_start_date,
        "partnership_goals": partnership_goals,
        "expected_contributions": expected_contributions,
        "mission_statement": mission_statement,
        "product_overview": product_overview,
        "target_market": target_market,
        "competitive_advantage": competitive_advantage,
        "investment_amount": investment_amount,
        "contract_duration": contract_duration,
        "legal_clauses": legal_clauses,
        "risk_liability": risk_liability,
        "additional_notes": additional_notes,
        "contact_person": contact_person,
        "contact_email": contact_email
    }
