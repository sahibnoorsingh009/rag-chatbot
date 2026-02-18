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

CHAT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "zeiss-chat")
EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

# Azure Search
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
        vector=qvec,
        k_nearest_neighbors=k,
        fields="contentVector"
    )

    results = search.search(
        search_text="",              # pure vector search
        vector_queries=[vq],
        select=["content", "source_file", "page_start", "page_end"],
        top=k
    )
    return list(results)

def answer(q: str, hits):
    sources_text = "\n\n".join(
        [f"[{h['source_file']} p.{h['page_start']}] {h['content']}" for h in hits]
    )

    system = (
        "You are a helpful assistant. Answer ONLY using the provided sources. "
        "If the answer is not in the sources, say: 'I don't have enough information in the documents.' "
        "Cite sources at the end like: (microscopy.pdf p.3)."
    )

    user = f"Question: {q}\n\nSources:\n{sources_text}"

    resp = client.chat.completions.create(
        model=CHAT_DEPLOYMENT,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return resp.choices[0].message.content

if __name__ == "__main__":
    q = input("Ask a question: ").strip()
    hits = retrieve(q, k=5)
    print("\nTop sources:")
    for h in hits:
        print(f"- {h['source_file']} p.{h['page_start']}")
    print("\nAnswer:\n")
    print(answer(q, hits))
