import cohere
import streamlit as st

def fill_form_with_ai(company_info_text, uploaded_docs_text="", manual_input={}, api_key=None):
    """
    Generate AI suggestions for the partnership form using Cohere Chat API (ClientV2).
    """

    if api_key is None:
        api_key = st.secrets.get("cohere", {}).get("api_key")
        if not api_key:
            raise ValueError("Cohere API key is missing. Set it in Streamlit secrets.")

    co = cohere.ClientV2(api_key=api_key)

    context = (
        f"Company Info:\n{company_info_text}\n\n"
        f"Documents:\n{uploaded_docs_text}\n\n"
        f"Manual Input:\n{manual_input}"
    )

    system_message = {
        "role": "system",
        "content": "You are an expert in corporate partnerships. Fill the partnership form based on the context. Return output strictly in JSON format matching the template."
    }

    user_message = {
        "role": "user",
        "content": context
    }

    try:
        response = co.chat(
            model="command-a-03-2025",  # or whichever chat model you're using
            messages=[system_message, user_message],
            max_tokens=1500
        )
        # The response.message.content is a list of objects; get the text
        return response.message.content[0].text.strip()
    except cohere.error.CohereError as e:
        st.error(f"Cohere API error: {e}")
        return "{}"
    except Exception as e:
        st.error(f"Unexpected error in AI fill: {e}")
        return "{}"
