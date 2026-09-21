import os
import streamlit as st
from google import genai

def get_gemini_client() -> genai.Client:
    api_key = None
    if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured. Set it in Streamlit secrets or environment.")

    return genai.Client(api_key=api_key)
