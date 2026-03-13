from sqlalchemy.orm import Session
from urllib.parse import urlparse
from app.apis.confluence import fetch_confluence_page
from app.db.models import ConfluencePage
from sync.detect_changes import confluence_html_to_text
from app.vectorstore.chroma import upsert_page_chunks
from datetime import datetime

def extract_page_id(url: str) -> str:
    path = urlparse(url).path
    parts = path.split("/")
    if "pages" in parts:
        idx = parts.index("pages")
        return parts[idx + 1]   
    raise ValueError("Invalid Confluence URL: Could not extract page ID")

def apply_sync(db: Session, url: str):
    page = fetch_confluence_page(url)
    page_id = extract_page_id(url)

    content_html = page["content"]
    version = page["version"]
    title = page["title"]
    space_key = page["space_key"]

    text = confluence_html_to_text(content_html)

    # 1️⃣ Update DB
    db_page = (
        db.query(ConfluencePage)
        .filter(ConfluencePage.page_id == page_id)
        .first()
    )

    if not db_page:
        db_page = ConfluencePage(
            page_id=page_id,
            title=title,
            space_key=space_key
        )
        db.add(db_page)

    db_page.last_synced_version = version
    db_page.last_synced_content = content_html
    db_page.last_synced_at = datetime.utcnow()

    # 2️⃣ Vector DB refresh (delete + insert with canonical metadata).
    # Keep this before commit so failures don't leave DB ahead of vectors.
    upsert_page_chunks(
        page_id=page_id,
        title=title,
        content=text,
        space_key=space_key,
    )

    db.commit()
