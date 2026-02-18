import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_version=os.environ["AZURE_OPENAI_API_VERSION"],
)

EMBED_DEPLOYMENT = os.environ["AZURE_OPENAI_EMBEDDING_DEPLOYMENT"]

text = "This is a test sentence for embeddings."

resp = client.embeddings.create(
    model=EMBED_DEPLOYMENT,
    input=text
)

vec = resp.data[0].embedding
print("Embedding length:", len(vec))
print("First 5 numbers:", vec[:5])
