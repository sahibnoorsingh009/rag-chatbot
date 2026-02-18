import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

load_dotenv()

# Azure OpenAI
client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

CHAT_DEPLOYMENT = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]
EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

# Azure AI Search
search = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"]),
)


def embed_query(q: str):
    r = client.embeddings.create(model=EMBED_DEPLOYMENT, input=q)
    return r.data[0].embedding


def retrieve(q: str, k: int = 5):
    qvec = embed_query(q)

    vq = VectorizedQuery(
        kind="vector",
        vector=qvec,
        k_nearest_neighbors=k,
        fields="contentVector"
    )

    results = search.search(
        search_text="",
        vector_queries=[vq],
        select=["content", "source_file", "page_start", "page_end"],
        top=k
    )

    return list(results)


def answer_with_sources(q: str, k: int = 5):
    hits = retrieve(q, k=k)

    sources = []
    for h in hits:
        sources.append({
            "source_file": h["source_file"],
            "page_start": h["page_start"],
            "page_end": h["page_end"],
            "snippet": h["content"][:250]
        })

    sources_text = "\n\n".join(
        [f"[{s['source_file']} p.{s['page_start']}] {h['content']}" for s, h in zip(sources, hits)]
    )

    system = (
        "Answer ONLY using the provided sources. "
        "If missing, say you don't have enough information. "
        "Cite like (microscopy.pdf p.3)."
    )
    user = f"Question: {q}\n\nSources:\n{sources_text}"

    resp = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    return {"answer": resp.choices[0].message.content, "sources": sources}

