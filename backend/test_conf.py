# from app.db.session import SessionLocal
# from sync.service import sync_confluence_space

# db = SessionLocal()
# changes = sync_confluence_space("~712020d82452f0cb5c492a8b6f69865eb21a08", db)

# print(changes)

from app.db.session import SessionLocal
from sync.detect_changes import detect_confluence_changes

db = SessionLocal()

changes = detect_confluence_changes(
    db=db,
    space_key="~712020d82452f0cb5c492a8b6f69865eb21a08"
)

print(changes)
