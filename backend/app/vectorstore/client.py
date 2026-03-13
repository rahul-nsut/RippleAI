import chromadb
from chromadb.config import Settings
from app.config import settings

# Initialize Chroma client (persistent)
client = chromadb.Client(
    Settings(
        persist_directory=settings.CHROMA_DIR,
        anonymized_telemetry=False
    )
)

# Main collection for Confluence docs
chroma_collection = client.get_or_create_collection(
    name="confluence_docs"
)
