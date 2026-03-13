from typing import List, Dict
from collections import defaultdict

from app.core.vectorstore import get_vectorstore

def extract_relevant_chunks_from_candidate_pages(
    *,
    candidate_page_ids: List[str],
    query_text: str,
    chunks_per_page: int = 12,
    context_window: int = 1, 
) -> Dict[str, List[Dict]]:
    if not candidate_page_ids:
        return {}

    print("Starting chunk extraction..")
    print(f"Candidate page IDs: {candidate_page_ids}")

    vectorstore = get_vectorstore()
    
    # Query each page separately to guarantee chunks_per_page per page
    page_chunks: Dict[str, List[Dict]] = defaultdict(list)
    
    for page_id in candidate_page_ids:
        results = vectorstore.similarity_search_with_score(
            query_text,
            k=chunks_per_page,
            filter={"doc_id": page_id},
        )
        if not results:
            # Backward-compatibility for older chunks written with page_id only.
            results = vectorstore.similarity_search_with_score(
                query_text,
                k=chunks_per_page,
                filter={"page_id": page_id},
            )
        
        print(f"Page {page_id}: found {len(results)} chunks")
        
        for doc, score in results:
            meta = doc.metadata or {}
            page_chunks[page_id].append({
                "chunk_id": doc.id,
                "content": doc.page_content,
                "position": meta.get("chunk_index", 0),
            })

    print(f"Page chunks: {page_chunks}")

    results: Dict[str, List[Dict]] = {}
    for page_id, chunks in page_chunks.items():
        chunks.sort(key=lambda x: x["position"])
        results[page_id] = chunks

    return results