import streamlit as st
import requests
import threading
import time
import uvicorn
import asyncio
from main import app  # ✅ Import FastAPI app

# ✅ Use FastAPI on port `8500`
FASTAPI_URL = "http://127.0.0.1:8500"

# ✅ Function to run FastAPI without event loop conflicts
def run_fastapi():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    config = uvicorn.Config(app, host="0.0.0.0", port=8500, loop="asyncio")
    server = uvicorn.Server(config)
    server.run()

# ✅ Start FastAPI inside Streamlit only once
if "fastapi_started" not in st.session_state:
    st.session_state["fastapi_started"] = True
    threading.Thread(target=run_fastapi, daemon=True).start()
    time.sleep(3)  # ✅ Give FastAPI time to start

st.set_page_config(page_title="AI-Powered Document Search & Translation", layout="wide")
st.title("📄 AI-Powered Document Search & Translation (Powered by Gemini AI)")

# 📤 **File Upload Section**
st.subheader("📤 Upload a Document for Indexing")
uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

if uploaded_file:
    with st.spinner("Uploading..."):
        response = requests.post(
            f"{FASTAPI_URL}/upload-document/",
            files={"file": (uploaded_file.name, uploaded_file.getvalue())}
        )
        
        if response.status_code == 200:
            st.success(f"✅ '{uploaded_file.name}' uploaded successfully!")
        else:
            st.error("❌ Failed to upload the file.")

# 🔍 **Search & Translate Section**
st.subheader("🔍 Search & Translate a Document")
query_text = st.text_input("Enter a search query:")
target_language = st.selectbox("Select Target Language:", ["fr", "de", "es", "it", "hi", "zh"])

if st.button("🔎 Search & Translate"):
    if query_text:
        with st.spinner("Searching & Translating..."):
            response = requests.get(
                f"{FASTAPI_URL}/translate-search/",
                params={"query_text": query_text, "target_language": target_language}
            )
            
            if response.status_code == 200:
                download_url = response.json().get("download_url")

                if download_url:
                    st.success("✅ Gemini AI Translation Completed! Click below to download.")
                    st.markdown(f"[📥 Click to Download]({download_url})", unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to retrieve download link.")
            else:
                st.error("❌ No relevant document found.")
