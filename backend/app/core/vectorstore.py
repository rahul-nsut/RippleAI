from langchain_chroma import Chroma

from app.core.embeddings import OpenRouterEmbeddings

CHROMA_DIR = "./chroma_data"

embeddings = OpenRouterEmbeddings()


def get_vectorstore():
    return Chroma(
        collection_name="confluence_docs",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )
