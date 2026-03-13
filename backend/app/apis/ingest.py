from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.vectorstore import get_vectorstore
from app.core.embeddings import get_embedding
import uuid

# Chunking setup
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

def ingest_document(doc_id: str, text: str, source_url: str, title: str):
    chunks = text_splitter.split_text(text)
    vs = get_vectorstore()

    ids = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"{doc_id}_{i}")
        metadatas.append({
            "doc_id": doc_id,
            "chunk_index": i,
            "source": source_url,
            "title": title
        })

    vs.add_texts(
        texts=chunks,
        ids=ids,
        metadatas=metadatas
    )

    return {"chunks_ingested": len(chunks)}

