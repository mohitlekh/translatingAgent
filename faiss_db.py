import os
import faiss
import pickle
import pdfplumber
import docx
import numpy as np
from sentence_transformers import SentenceTransformer

# Define the embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Function to extract text from TXT
def extract_text_from_txt(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# Function to extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# Function to process documents
def load_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith(".txt"):
            text = extract_text_from_txt(file_path)
        elif filename.endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif filename.endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            continue
        documents.append((filename, text))
    return documents

# Function to create FAISS vector database
def create_faiss_index(documents, index_path="faiss_index/faiss.index"):
    if not documents:
        print("No documents to process.")
        return None

    # Generate embeddings for all documents
    embeddings = [embedding_model.encode(text) for _, text in documents]
    embeddings = np.array(embeddings, dtype="float32")

    # Create FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, index_path)

    # Save document metadata
    metadata = {i: filename for i, (filename, _) in enumerate(documents)}
    with open("faiss_index/metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

    print(f"FAISS index created and saved at '{index_path}'.")

# Function to search the most relevant document using FAISS
def search_faiss_index(query, index_path = "faiss_index/faiss.index", top_k=1):
    index = faiss.read_index(index_path)

    with open("metadata.pkl", "rb") as f:
        metadata = pickle.load(f)

    query_embedding = embedding_model.encode(query).reshape(1, -1).astype("float32")

    distances, indices = index.search(query_embedding, top_k)

    return metadata[indices[0][0]] if indices[0][0] in metadata else None
