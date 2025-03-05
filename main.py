from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
import os
from utils import process_file
from faiss_db import create_faiss_index, search_faiss_index, load_documents

app = FastAPI()

# Load and store documents into FAISS on startup
docs = load_documents("documents")
create_faiss_index(docs)

@app.get("/")
def home():
    return {"message": "Welcome to the Translation App & FAISS Search Service!"}

@app.get("/translate-search/")
def translate_search(query_text: str, target_language: str):
    print(f"🔍 Searching for: {query_text}")

    retrieved_doc = search_faiss_index(query_text)

    if not retrieved_doc:
        print("❌ No relevant document found.")
        return {"error": "No relevant document found"}

    print(f"✅ Found document: {retrieved_doc}")

    translated_file_path, error = process_file(retrieved_doc, target_language)

    if error:
        print(f"⚠️ Error Processing File: {error}")
        return {"error": error}

    print(f"📥 Returning translated file: {translated_file_path}")
    return FileResponse(translated_file_path, filename=os.path.basename(translated_file_path), media_type="application/octet-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
