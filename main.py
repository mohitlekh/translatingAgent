import os
import threading
import uvicorn
import google.generativeai as genai
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from utils import process_file
from faiss_db import search_faiss_index, create_faiss_index, load_documents

# ✅ Initialize Google Gemini AI
GOOGLE_API_KEY = "AIzaSyBRbOwTCb015gqn4ii2WhB1-ah5RFrttfQ"  # Replace with your actual key
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

app = FastAPI()

# ✅ Ensure directories exist
os.makedirs("documents", exist_ok=True)
os.makedirs("public", exist_ok=True)

# ✅ Serve translated files publicly
app.mount("/public", StaticFiles(directory="public"), name="public")

# ✅ Load and store all documents into FAISS on startup
docs = load_documents("documents")
create_faiss_index(docs)

@app.get("/")
def home():
    return {"message": "Welcome to the Translation & FAISS Search Service!"}

@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join("documents", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # ✅ Rebuild FAISS index after upload
    docs = load_documents("documents")
    create_faiss_index(docs)

    return JSONResponse({"message": f"File '{file.filename}' uploaded successfully!"})

@app.get("/translate-search/")
def translate_search(query_text: str, target_language: str):
    retrieved_doc = search_faiss_index(query_text)
    
    if not retrieved_doc:
        return {"error": "No relevant document found"}

    translated_file_path, error = process_file(retrieved_doc, target_language)
    
    if error:
        return {"error": error}

    # ✅ Improve translation with Google Gemini AI
    with open(translated_file_path, "r", encoding="utf-8") as f:
        translated_text = f.read()

    gemini_prompt = f"Improve this translation in {target_language}:\n{translated_text}"
    gemini_response = model.generate_content(gemini_prompt).text

    # ✅ Save improved translation
    new_translated_file_path = os.path.join("public", f"gemini_{os.path.basename(translated_file_path)}")
    with open(new_translated_file_path, "w", encoding="utf-8") as f:
        f.write(gemini_response)

    # ✅ Generate public download URL
    base_url = "https://translateme.streamlit.app"  # Replace with your Streamlit URL
    download_url = f"{base_url}/public/{os.path.basename(new_translated_file_path)}"

    return {"download_url": download_url}

# ✅ Start FastAPI inside Streamlit (No subprocess issues!)
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8050)

fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
fastapi_thread.start()
