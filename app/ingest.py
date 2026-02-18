import os
import uuid
from dotenv import load_dotenv
from pypdf import PdfReader
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

CHUNK_SIZE = 1500
OVERLAP = 200

# Azure OpenAI
aoai = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

# Azure Search
search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)


def chunk_text(text: str):
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        ch = text[start:end].strip()
        if ch:
            chunks.append(ch)
        start = end - OVERLAP
        if start < 0:
            start = 0
    return chunks

def delete_by_source_file(source_file: str):
    # Find all docs with this source_file and delete them
    results = search_client.search(
        search_text="",
        filter=f"source_file eq '{source_file}'",
        select=["id"],
        top=1000
    )

    ids = [{"id": r["id"]} for r in results]

    if ids:
        search_client.delete_documents(ids)


def ingest_pdf(file_path: str):
    reader = PdfReader(file_path)
    source_file = os.path.basename(file_path)
    delete_by_source_file(source_file)
    docs = []

    for i, page in enumerate(reader.pages):
        text = (page.extract_text() or "").replace("\n", " ").strip()
        if not text:
            continue

        chunks = chunk_text(text)

        for ch in chunks:
            resp = aoai.embeddings.create(
                model=EMBED_DEPLOYMENT,
                input=ch
            )

            vec = resp.data[0].embedding

            docs.append({
                "id": str(uuid.uuid4()),
                "content": ch,
                "source_file": source_file,
                "page_start": i + 1,
                "page_end": i + 1,
                "contentVector": vec
            })

    search_client.upload_documents(docs)

    return {"status": "success", "chunks_indexed": len(docs)}
