import streamlit as st
import subprocess
import requests
import time

# Ensure FastAPI starts inside Streamlit
FASTAPI_URL = "http://127.0.0.1:8000"

# Function to run FastAPI
def run_fastapi():
    subprocess.Popen(["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])

# Check if FastAPI is running, else start it
if "fastapi_started" not in st.session_state:
    st.session_state["fastapi_started"] = True
    run_fastapi()
    time.sleep(3)  # Wait for FastAPI to start

st.title("📄 AI-Powered Document Search & Translation")

# User enters search query
query_text = st.text_input("🔍 Enter a search query:")
target_language = st.selectbox("🌍 Select Target Language:", ["fr", "de", "es", "it"])

if st.button("🔎 Search & Translate"):
    with st.spinner("Searching & Translating..."):
        response = requests.get(f"{FASTAPI_URL}/translate-search/", params={"query_text": query_text, "target_language": target_language})
        if response.status_code == 200:
            translated_file_url = response.url
            st.success("✅ Translation Completed!")
            st.markdown(f"[📥 Download Translated File]({translated_file_url})")
        else:
            st.error("❌ No relevant document found.")
