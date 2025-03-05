import streamlit as st
import requests

# ✅ Use localhost since FastAPI is running inside Streamlit
FASTAPI_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI-Powered Document Search & Translation", layout="wide")

st.title("📄 AI-Powered Document Search & Translation")

# 🔍 **Search & Translate Section**
query_text = st.text_input("🔍 Enter a search query:")
target_language = st.selectbox("🌍 Select Target Language:", ["fr", "de", "es", "it", "hi", "zh"])

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
                    st.success("✅ Translation Completed! Click below to download.")
                    st.markdown(f"[📥 Click to Download]({download_url})", unsafe_allow_html=True)
                else:
                    st.error("❌ Failed to retrieve download link.")
            else:
                st.error("❌ No relevant document found.")
