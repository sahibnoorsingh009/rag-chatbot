import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)

load_dotenv()

endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
key = os.getenv("AZURE_SEARCH_API_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")


client = SearchIndexClient(endpoint, AzureKeyCredential(key))

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="source_file", type=SearchFieldDataType.String, filterable=True),
    SimpleField(name="page_start", type=SearchFieldDataType.Int32, filterable=True),
    SimpleField(name="page_end", type=SearchFieldDataType.Int32, filterable=True),
    SearchField(
        name="contentVector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,  # For text-embedding-3-small
        vector_search_profile_name="vector-profile"
    ),
]

vector_search = VectorSearch(
    algorithms=[HnswAlgorithmConfiguration(name="hnsw")],
    profiles=[VectorSearchProfile(
        name="vector-profile",
        algorithm_configuration_name="hnsw"
    )]
)

index = SearchIndex(
    name=index_name,
    fields=fields,
    vector_search=vector_search
)

client.create_or_update_index(index)

print(f"Index '{index_name}' created successfully.")
