import os
import subprocess
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from utils import process_file
from faiss_db import create_faiss_index, search_faiss_index, load_documents

app = FastAPI()

# Load and store all documents into FAISS on startup
docs = load_documents("documents")
create_faiss_index(docs)

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI Translation & FAISS Search Service!"}

@app.get("/translate-search/")
def translate_search(query_text: str, target_language: str):
    retrieved_doc = search_faiss_index(query_text)
    if not retrieved_doc:
        return {"error": "No relevant document found"}

    translated_file_path, error = process_file(retrieved_doc, target_language)
    if error:
        return {"error": error}

    return FileResponse(translated_file_path, filename=os.path.basename(translated_file_path), media_type="application/octet-stream")

# Function to run FastAPI inside Streamlit
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8500)

# Start FastAPI server in a separate thread
fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
fastapi_thread.start()
