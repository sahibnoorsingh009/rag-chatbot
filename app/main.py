from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.rag import answer_with_sources
from app.ingest import ingest_pdf

app = FastAPI(title="ZEISS RAG Chatbot")

@app.get("/")
def root():
    return {"message": "ZEISS RAG API is running. Go to /docs"}



@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"./{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = ingest_pdf(file_path)

    return result


@app.post("/chat")
def chat(query: str, k: int = 5):
    return answer_with_sources(query, k=k)