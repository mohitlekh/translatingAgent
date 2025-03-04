import streamlit as st
import requests
import subprocess
import threading
import os

# Ensure FastAPI starts inside Streamlit
FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI-Powered Document Search & Translation", layout="wide")

st.title("📄 AI-Powered Document Search & Translation")

# User enters search query
query_text = st.text_input("🔍 Enter a search query:")

# User selects target language
target_language = st.selectbox("🌍 Select Target Language:", ["fr", "de", "es", "it", "hi", "zh"])

if st.button("🔎 Search & Translate"):
    if query_text:
        with st.spinner("Searching & Translating..."):
            response = requests.get(
                f"{FASTAPI_URL}/translate-search/",
                params={"query_text": query_text, "target_language": target_language}
            )
            
            if response.status_code == 200:
                translated_file_url = response.url
                st.success("✅ Translation Completed!")
                st.markdown(f"[📥 Download Translated File]({translated_file_url})")
            else:
                st.error("❌ No relevant document found.")

# File upload option
st.subheader("📤 Upload a Document for Future Searches")
uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

if uploaded_file:
    file_path = f"documents/{uploaded_file.name}"
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"✅ {uploaded_file.name} uploaded successfully!")

# Function to run FastAPI inside Streamlit
def run_fastapi():
    subprocess.Popen(["python", "main.py"])

# Start FastAPI server in a separate thread
if "fastapi_started" not in st.session_state:
    st.session_state["fastapi_started"] = True
    fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
    fastapi_thread.start()
