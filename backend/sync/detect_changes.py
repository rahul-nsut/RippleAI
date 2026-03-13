from typing import List, Dict
from sqlalchemy.orm import Session

from confluence.client import fetch_pages_with_versions
from app.db.models import ConfluencePage
from sync.diff import compute_text_diff
from bs4 import BeautifulSoup

## Helper to condense response body
def split_diff(diff_lines: list[str]) -> dict:
    added = []
    removed = []

    for line in diff_lines:
        if line.startswith(("+++", "---", "@@")):
            continue
        if line.startswith("+ "):
            added.append(line[2:])
        elif line.startswith("- "):
            removed.append(line[2:])

    return {
        "added": added,
        "removed": removed
    }


def confluence_html_to_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    # Remove macros & metadata
    for tag in soup(["script", "style"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Normalize whitespace
    lines = [line.strip() for line in text.splitlines()]
    return "\n".join([l for l in lines if l])


def detect_confluence_changes(
    db: Session,
    space_key: str
) -> List[Dict]:
    """
    Detect NEW / UPDATED / UNCHANGED Confluence pages
    without mutating DB or Chroma
    """

    latest_pages = fetch_pages_with_versions(space_key)
    changes = []

    for page in latest_pages:
        page_id = page["page_id"]
        title = page["title"]
        version = page["version"]
        content = page["content"]

        db_page = (
            db.query(ConfluencePage)
            .filter(ConfluencePage.page_id == page_id)
            .first()
        )

        # 🆕 New page
        if not db_page:
            changes.append({
                "type": "NEW",
                "page_id": page_id,
                "title": title
            })
            continue

        # ⏸ No change
        if db_page.last_synced_version == version:
            changes.append({
                "type": "UNCHANGED",
                "page_id": page_id,
                "title": title
            })
            continue

        # 🔄 Updated page
        old_text = confluence_html_to_text(db_page.last_synced_content or "")
        new_text = confluence_html_to_text(content)
        # print("Old text:", old_text)
        # print("New text:", new_text)
        diffs = compute_text_diff(
            old_text=old_text,
            new_text=new_text
        )
        print("Diffs:", diffs)
        changes.append({
            "type": "UPDATED",
            "page_id": page_id,
            "title": title,
            "diff": diffs,
            "version_from": db_page.last_synced_version,
            "version_to": version,
        })

    return changes
