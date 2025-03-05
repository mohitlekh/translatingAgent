import os
import threading
import uvicorn
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from utils import process_file
from faiss_db import search_faiss_index, create_faiss_index, load_documents

app = FastAPI()

# Ensure required directories exist
os.makedirs("documents", exist_ok=True)
os.makedirs("public", exist_ok=True)

# Serve translated files publicly
app.mount("/public", StaticFiles(directory="public"), name="public")

# Load and store all documents into FAISS on startup
docs = load_documents("documents")
create_faiss_index(docs)

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI Translation & FAISS Search Service!"}

@app.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    file_path = os.path.join("documents", file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Rebuild FAISS index after upload
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

    # Move translated file to 'public/' for public access
    new_file_path = os.path.join("public", os.path.basename(translated_file_path))
    os.rename(translated_file_path, new_file_path)

    # Generate public download URL (Replace with your Streamlit App URL)
    base_url = "https://translateme.streamlit.app"
    download_url = f"{base_url}/public/{os.path.basename(new_file_path)}"

    return {"download_url": download_url}

# ✅ Start FastAPI in a background thread inside Streamlit
def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

fastapi_thread = threading.Thread(target=run_fastapi, daemon=True)
fastapi_thread.start()
