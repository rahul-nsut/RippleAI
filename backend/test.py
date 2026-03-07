from app.suggestions.candidate_selector import select_candidate_pages
from app.db.session import SessionLocal
from app.vectorstore.chroma import get_chroma_collection

db = SessionLocal()
chroma_collection = get_chroma_collection()

candidates = select_candidate_pages(
    db=db,
    chroma_collection=chroma_collection,
    changed_page_id="7503873",
    changed_title="Netflix System Design Document",
    diff={
        "added": ["CDN improves latency"],
        "removed": []
    }
)
print(candidates)
