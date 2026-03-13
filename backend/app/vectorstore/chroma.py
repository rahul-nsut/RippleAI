from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.core.vectorstore import get_vectorstore


def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_text(text)


def upsert_page_chunks(page_id: str, title: str, content: str, space_key: str | None = None):
    """
    Deletes old vectors for a page and inserts fresh chunks
    """

    # 1) Remove existing chunks from both metadata shapes.
    # This keeps old data compatible while standardizing on doc_id.
    vectorstore = get_vectorstore()
    vectorstore.delete(where={"doc_id": page_id})
    vectorstore.delete(where={"page_id": page_id})

    # 2️⃣ Chunk content
    chunks = chunk_text(content)

    # 3) Insert chunks with stable metadata expected by suggestions pipeline.
    metadatas = []
    for idx, _ in enumerate(chunks):
        metadata = {
            "doc_id": page_id,
            "page_id": page_id,
            "title": title,
            "chunk_index": idx,
        }
        if space_key:
            metadata["space_key"] = space_key
        metadatas.append(metadata)

    vectorstore.add_texts(
        texts=chunks,
        metadatas=metadatas,
        ids=[f"{page_id}_{i}" for i in range(len(chunks))],
    )
