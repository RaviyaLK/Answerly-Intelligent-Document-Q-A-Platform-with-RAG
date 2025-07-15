# main.py
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from auth.auth_utils import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_user,
    users_collection
)
from ingestion.pdf_loader import extract_text_from_pdf
from chunking.text_chunker import chunk_text
from embedding.embed_store import (
    embed_chunks,
    save_faiss_index,
    store_pdf_chunks_for_user,
    store_pdf_chunks_in_snowflake,  
    load_embeddings_from_mongodb    
)
from rag.qa_pipeline import generate_answer, retrieve_context_single, retrieve_context_multi
from db.db import create_collection_for_user,pdf_embeddings_collection
from fastapi.security import OAuth2PasswordRequestForm
from snowflake.snowflake_utils import log_query_response
import os

app = FastAPI()

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QARequest(BaseModel):
    question: str
    mode: str  # "single" or "multi"
    collection_name: Optional[str] = None
    
# Register new user 
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    if get_user(username):
        raise HTTPException(status_code=400, detail="Username already exists")
    users_collection.insert_one({
        "username": username,
        "hashed_password": get_password_hash(password)
    })
    return {"message": "User registered successfully"}

# Login the registered user
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(data={"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# Upload a single pdf and save to local
@app.post("/upload/single/")
def upload_single_pdf(file: UploadFile = File(...)):
    contents = file.file.read()
    file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)
    
    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    save_faiss_index(embeddings, chunks)
    return {"message": "PDF processed and saved for single mode."}

# Create the collection for the registered user
@app.post("/create-collection/")
def create_collection(collection_name: str = Form(...), current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    create_collection_for_user(user_id, collection_name)
    return {"message": f"Collection '{collection_name}' created for user."}

# Upload multiple pdfs and save to mongo and snowflake
@app.post("/upload/multi/")
def upload_multi_pdf(
    collection_name: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    contents = file.file.read()
    file_path = f"temp/{file.filename}"
    os.makedirs("temp", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf(file_path)
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)

    user_id = str(current_user["_id"])
    store_pdf_chunks_for_user(user_id, collection_name, chunks, embeddings)
    store_pdf_chunks_in_snowflake(user_id, collection_name, chunks, embeddings)
    return {"message": "PDF uploaded and stored in MongoDB for multi mode."}

# Ask questions from the pdfs
@app.post("/qa/")
def ask_question(data: QARequest, current_user: dict = Depends(get_current_user)):
    if data.mode == "multi":
        if not data.collection_name:
            raise HTTPException(status_code=400, detail="Collection name required for multi mode")
        user_id = str(current_user["_id"])
        collection_name = data.collection_name
        question= data.question
        context_chunks =  retrieve_context_multi(user_id, data.collection_name, data.question)
        answer = generate_answer(data.question, context_chunks)
    
        log_query_response(
        user_id=user_id,
        collection_name=collection_name,
        question=str(question),
        chunks_text=str(context_chunks),
        response=str(answer)
        )
        
    else:
     context_chunks = retrieve_context_single(data.question)
     answer = generate_answer(data.question, context_chunks)

    
    return {"answer": answer}
@app.get("/collections/")
def get_user_collections(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])

    # Get unique collection names for this user
    collections = pdf_embeddings_collection.distinct("collection_name", {"user_id": user_id})

    return [{"name": name} for name in collections]
