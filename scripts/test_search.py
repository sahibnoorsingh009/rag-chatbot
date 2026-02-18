import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

load_dotenv()

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_API_KEY"])
)

results = client.search(search_text="Hoyle state", top=3)

for r in results:
    print("SOURCE:", r["source_file"], "pages:", r["page_start"], "-", r["page_end"])
    print(r["content"][:300])
    print("-" * 50)
