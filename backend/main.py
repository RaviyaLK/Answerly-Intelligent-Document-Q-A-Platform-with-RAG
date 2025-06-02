# main.py
from fastapi import FastAPI, UploadFile, File
from ingestion.pdf_loader import extract_text_from_pdf
from chunking.text_chunker import chunk_text
from embedding.embed_store import embed_chunks, save_faiss_index
from rag.qa_pipeline import retrieve_context, generate_answer

app = FastAPI()

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    with open("temp.pdf", "wb") as f:
        f.write(contents)

    text = extract_text_from_pdf("temp.pdf")
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    save_faiss_index(embeddings, chunks)
    return {"message": "PDF processed and indexed."}

@app.post("/ask/")
async def ask_question(question: str):
    context = retrieve_context(question)
    answer = generate_answer(question, context)
    return {"answer": answer}
