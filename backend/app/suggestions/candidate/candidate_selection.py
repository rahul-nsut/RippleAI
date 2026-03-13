from typing import List, Dict
from collections import defaultdict

from sqlalchemy.orm import Session

from app.db.models import ConfluencePage
from app.core.vectorstore import get_vectorstore


CANDIDATE_CONFIDENCE_THRESHOLD = 0.4


def _build_query_text(
    added_lines: List[str],
    removed_lines: List[str]
) -> str:
    """
    Build a semantic query from added + removed lines.
    Used only for vector similarity search.
    """
    parts = []

    if added_lines:
        parts.append("ADDED:")
        parts.extend(added_lines)

    if removed_lines:
        parts.append("REMOVED:")
        parts.extend(removed_lines)

    return "\n".join(parts)


def select_candidate_pages(
    db: Session,
    source_page_id: str,
    added_lines: List[str],
    removed_lines: List[str],
    top_k_chunks: int = 30,
) -> List[Dict]:
    """
    Step-1: Candidate Page Selection

    Returns pages whose confidence score >= threshold.

    Output:
    [
        {
            "page_id": str,
            "title": str,
            "confidence": float
        }
    ]
    """


    print(f"Added lines: {added_lines}")
    print(f"Removed lines: {removed_lines}")
    if not added_lines and not removed_lines:
        return []

    query_text = _build_query_text(added_lines, removed_lines)
    print(f"Query text: {query_text}")

    vectorstore = get_vectorstore()
    # similarity_search_with_score returns (Document, score) where score is distance
    results = vectorstore.similarity_search_with_score(
        query_text,
        k=top_k_chunks,
    )

    page_scores = defaultdict(list)

    for doc, distance in results:
        metadata = doc.metadata or {}
        page_id = metadata.get("doc_id") or metadata.get("page_id")

        if not page_id or page_id == source_page_id:
            continue

        similarity = 1.0 / (1.0 + distance)
        page_scores[page_id].append(similarity)

    candidates = []

    for page_id, similarities in page_scores.items():
        confidence = sum(similarities) / len(similarities)
        print(f"Page ID: {page_id}, Confidence: {confidence}")

        # ✅ Embedded threshold logic
        if confidence < CANDIDATE_CONFIDENCE_THRESHOLD:
            continue

        page = db.query(ConfluencePage).filter(ConfluencePage.page_id == page_id).first()
        candidates.append({
            "page_id": page_id,
            "title": page.title if page else page_id,
            "confidence": round(confidence, 3)
        })

    candidates.sort(key=lambda x: x["confidence"], reverse=True)

    return candidates
