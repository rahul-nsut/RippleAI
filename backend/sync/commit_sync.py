from datetime import datetime
from sqlalchemy.orm import Session

from app.models.confluence_page import ConfluencePage
from app.vectorstore.chroma import upsert_page_chunks
from sync.detect_changes import detect_confluence_changes


def commit_sync(space_key: str, db: Session):
    """
    Commits detected changes into both DBs
    """
    changes = detect_confluence_changes(db, space_key)

    committed = []

    for change in changes:
        if change["type"] == "UNCHANGED":
            continue

        page_id = change["page_id"]

        if change["type"] == "NEW":
            page = ConfluencePage(
                page_id=page_id,
                space_key=space_key,
                title=change["title"],
                last_synced_version=change["version"],
                last_synced_content=change["content"],
                last_synced_at=datetime.utcnow(),
            )
            db.add(page)

        elif change["type"] == "UPDATED":
            page = (
                db.query(ConfluencePage)
                .filter(ConfluencePage.page_id == page_id)
                .first()
            )

            page.title = change["title"]
            page.last_synced_version = change["version"]
            page.last_synced_content = change["content"]
            page.last_synced_at = datetime.utcnow()

        #  Update Chroma
        upsert_page_chunks(
            page_id=page_id,
            title=change["title"],
            content=change["content"],
        )

        committed.append({
            "page_id": page_id,
            "title": change["title"],
            "type": change["type"],
        })

    db.commit()
    return committed
