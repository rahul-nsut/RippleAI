from datetime import datetime
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import ConfluencePage
from confluence.client import fetch_pages_with_versions


def sync_confluence_space(space_key: str, db: Session):
    pages = fetch_pages_with_versions(space_key)
    changes = []

    for page in pages:
        db_page = db.query(ConfluencePage).filter(
            ConfluencePage.page_id == page["page_id"]
        ).first()

        if not db_page:
            #  New page
            db.add(ConfluencePage(
                page_id=page["page_id"],
                space_key=space_key,
                title=page["title"],
                last_synced_version=page["version"],
                last_synced_content=page["content"],
                last_synced_at=datetime.utcnow()
            ))

            changes.append({
                "type": "NEW",
                "page_id": page["page_id"],
                "title": page["title"]
            })

        elif page["version"] > db_page.last_synced_version:
            #  Updated page
            db_page.title = page["title"]
            db_page.last_synced_version = page["version"]
            db_page.last_synced_content = page["content"]
            db_page.last_synced_at = datetime.utcnow()

            changes.append({
                "type": "UPDATED",
                "page_id": page["page_id"],
                "title": page["title"]
            })

    db.commit()
    return changes
