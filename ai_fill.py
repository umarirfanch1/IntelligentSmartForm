import cohere
import streamlit as st

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Generate AI suggestions for the partnership form using Cohere Chat API.
    """

    if api_key is None:
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing. Set it in Streamlit secrets.")

    co = cohere.ClientV2(api_key)  # Use ClientV2 for newer API

    # Combine context
    context = (
        f"Company Info:\n{company_info_text}\n\n"
        f"Documents:\n{uploaded_docs_text}\n\n"
        f"Manual Input:\n{manual_input}"
    )

    # System / instruction message
    system_instruction = (
        "You are an expert in corporate partnerships. "
        "Your task is to fill the partnership form based on the context, "
        "and return output strictly in JSON format matching the form template."
    )

    # Cohere v2 chat call uses `message=` for user content
    try:
        response = co.chat(
            model="command-a-03-2025",
            message=context,
            preamble=system_instruction,
            max_tokens=1500
        )
        # `response.message.content[0].text` holds the generated text
        return response.message.content[0].text.strip()
    except cohere.error.CohereError as e:
        st.error(f"Cohere API error: {e}")
        return "{}"
    except Exception as e:
        st.error(f"Unexpected error in AI fill: {e}")
        return "{}"
