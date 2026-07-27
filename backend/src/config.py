import os
from dotenv import load_dotenv

load_dotenv()

# Azure OpenAI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

CHAT_MODEL = os.getenv("CHAT_MODEL")
EMBED_MODEL = os.getenv("EMBED_MODEL")

# AWS
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# S3
S3_BUCKET = os.getenv("S3_BUCKET")

# ChromaDB
# ChromaDB
CHROMA_DB_DIR = os.getenv(
    "CHROMA_DB_DIR",
    "./data/chromadb"
)

# Tenant
TENANT_ID = os.getenv(
    "TENANT_ID",
    "star-health"
)

# Tenant
TENANT_ID = os.getenv("TENANT_ID", "star-health")