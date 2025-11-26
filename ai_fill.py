def fill_form_with_ai(combined_text: str) -> dict:
    """
    Mock AI function for prototyping.
    Fills form with dummy data or simple parsing of text.
    """
    words = combined_text.split()
    return {
        "company_name": words[0] if words else "Demo Corp",
        "company_url": "https://example.com",
        "founding_year": "2020",
        "num_employees": "50",
        "hq_location": "New York",
        "partner_name": "Partner Inc",
        "partnership_type": "Strategic",
        "partnership_start_date": "2025-01-01",
        "partnership_goals": "Expand market share",
        "expected_contributions": "Funding and expertise",
        "mission_statement": "Deliver best-in-class products",
        "product_overview": "Software solutions",
        "target_market": "Global",
        "competitive_advantage": "AI-driven",
        "investment_amount": "$1,000,000",
        "contract_duration": "3 years",
        "legal_clauses": "Standard terms apply",
        "risk_liability": "Limited liability",
        "additional_notes": "",
        "contact_person": "John Doe",
        "contact_email": "john@example.com"
    }
