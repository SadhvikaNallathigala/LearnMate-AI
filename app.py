import streamlit as st
import os
import requests

HF_API_KEY = os.getenv("HF_API_KEY")

if not HF_API_KEY:
    st.error("Hugging Face API key missing in environment variables.")
    st.stop()
# ===============================
# CONFIGURATION
# ===============================

# Get API key from Streamlit secrets (for deployment)

API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# ===============================
# HUGGING FACE QUERY FUNCTION
# ===============================

@st.cache_data(show_spinner=False)
def query_huggingface(prompt_instruction):
    try:
        formatted_prompt = f"<s>[INST] {prompt_instruction} [/INST]"

        payload = {
            "inputs": formatted_prompt,
            "parameters": {
                "max_new_tokens": 512,
                "temperature": 0.7,
                "top_p": 0.95
            }
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            generated_text = result[0]["generated_text"]

            if "[/INST]" in generated_text:
                return generated_text.split("[/INST]")[-1].strip()
            return generated_text.strip()

        return "Unexpected API response."

    except Exception as e:
        return f"Error: {str(e)}"

# ===============================
# STREAMLIT UI
# ===============================

st.set_page_config(
    page_title="AI Student Learning Assistant",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 AI Student Learning Assistant")
st.markdown("AI-powered tool for summarization, explanations, and quizzes.")

st.sidebar.header("Features")

option = st.sidebar.selectbox(
    "Choose feature",
    [
        "Summarize Text",
        "Explain Concept",
        "Generate Model Questions",
        "Generate Quiz"
    ]
)

user_input = st.text_area("Enter topic or text:", height=200)

if st.button("Generate"):
    if not user_input.strip():
        st.warning("Please enter some text.")
    else:
        with st.spinner("Processing..."):

            if option == "Summarize Text":
                prompt = f"Summarize this clearly:\n{user_input}"

            elif option == "Explain Concept":
                prompt = f"Explain this in simple terms:\n{user_input}"

            elif option == "Generate Model Questions":
                prompt = f"Create 5 exam questions on:\n{user_input}"

            elif option == "Generate Quiz":
                prompt = f"Create 3 MCQs and 2 True/False on:\n{user_input}"

            result = query_huggingface(prompt)

            st.subheader("Result")
            st.write(result)

st.markdown("---")

st.caption("Built with Streamlit + HuggingFace Transformers")
