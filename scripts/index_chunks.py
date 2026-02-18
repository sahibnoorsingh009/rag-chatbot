import os
import uuid
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

# ---- Config ----
PDF_PATH = "microscopy.pdf"
CHUNK_SIZE = 1500
OVERLAP = 200

UPLOAD_LIMIT = None   # set 5 for testing; later change to None for all

# Azure OpenAI (Embeddings)
aoai = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)
EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

# Azure AI Search
search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)

def chunk_text(text: str, chunk_size: int, overlap: int):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        ch = text[start:end].strip()
        if ch:
            chunks.append(ch)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

def extract_and_chunk_pdf(pdf_path: str):
    reader = PdfReader(pdf_path)
    all_chunks = []
    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").replace("\n", " ").strip()
        if not text:
            continue
        page_chunks = chunk_text(text, CHUNK_SIZE, OVERLAP)
        for j, ch in enumerate(page_chunks):
            all_chunks.append({
                "page_start": i + 1,
                "page_end": i + 1,
                "chunk_id": f"p{i+1}_c{j}",
                "content": ch
            })
    return all_chunks

def embed(text: str):
    resp = aoai.embeddings.create(model=EMBED_DEPLOYMENT, input=text)
    return resp.data[0].embedding

def upload_documents(chunks, source_file):
    docs = []
    for c in chunks:
        vec = embed(c["content"])
        docs.append({
            "id": str(uuid.uuid4()),
            "content": c["content"],
            "source_file": source_file,
            "page_start": c["page_start"],
            "page_end": c["page_end"],
            "contentVector": vec
        })
    result = search_client.upload_documents(docs)
    return result

if __name__ == "__main__":
    chunks = extract_and_chunk_pdf(PDF_PATH)
    print("Total chunks found:", len(chunks))

    if UPLOAD_LIMIT is not None:
        chunks = chunks[:UPLOAD_LIMIT]
        print("Uploading only:", len(chunks))

    res = upload_documents(chunks, source_file=os.path.basename(PDF_PATH))
    print("Upload result:", res)
    print("Done ✅")
