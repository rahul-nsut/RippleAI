# Based on added & removed lines, extract the exact chunk where the change was made
from typing import List, Dict

from app.core.vectorstore import get_vectorstore


def extract_source_context(
    source_page_id: str,
    added_lines: List[str],
    removed_lines: List[str],
    include_neighbor_chunks: bool = True,
) -> List[Dict]:

    if not added_lines and not removed_lines:
        return []

    # Fetch all chunks for the source page from the vectorstore
    vectorstore = get_vectorstore()
    results = vectorstore.get(
        where={"doc_id": source_page_id},
        include=["documents", "metadatas"],
    )
    if not results.get("documents"):
        # Backward-compatibility for older chunks written with page_id only.
        results = vectorstore.get(
            where={"page_id": source_page_id},
            include=["documents", "metadatas"],
        )

    if not results.get("documents"):
        return []

    # Build list sorted by chunk_index
    chunks = []
    for doc_content, meta, doc_id in zip(
        results["documents"], results["metadatas"], results["ids"]
    ):
        chunks.append({
            "id": doc_id,
            "content": doc_content or "",
            "chunk_index": meta.get("chunk_index", 0),
        })
    chunks.sort(key=lambda c: c["chunk_index"])

    matched_indices = []
    # Find exact chunks that have added or removed lines
    for idx, chunk in enumerate(chunks):
        content = chunk["content"]

        for line in added_lines + removed_lines:
            if line and line in content:
                matched_indices.append(idx)
                break

    if not matched_indices:
        return []

    # Add neighbour indices for more context to LLM
    final_indices = set(matched_indices)
    if include_neighbor_chunks:
        for idx in matched_indices:
            if idx - 1 >= 0:
                final_indices.add(idx - 1)
            if idx + 1 < len(chunks):
                final_indices.add(idx + 1)

    contexts = []
    for idx in sorted(final_indices):
        chunk = chunks[idx]
        contexts.append({
            "page_id": source_page_id,
            "chunk_id": chunk["id"],
            "content": chunk["content"],
            "position": chunk["chunk_index"],
            "added_lines": added_lines,
            "removed_lines": removed_lines,
        })

    return contexts
