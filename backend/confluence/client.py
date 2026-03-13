from dotenv import load_dotenv
from app.config import settings
import os
import requests
from typing import List, Dict
load_dotenv()

CONFLUENCE_BASE_URL = settings.CONFLUENCE_URL
CONFLUENCE_EMAIL = settings.CONFLUENCE_EMAIL
CONFLUENCE_API_TOKEN = settings.CONFLUENCE_API_TOKEN
CONFLUENCE_SPACE = settings.CONFLUENCE_SPACE
HEADERS = {
    "Accept": "application/json"
}

def fetch_pages_with_versions(space_key: str) -> List[Dict]:
    """
    Fetch all pages from a Confluence space with body + version info
    """
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content"
    params = {
        "spaceKey": space_key,
        "type": "page",
        "limit": 50,
        "expand": "body.storage,version"
    }

    auth = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    pages = []

    while True:
        response = requests.get(url, headers=HEADERS, params=params, auth=auth)
        response.raise_for_status()

        data = response.json()
        pages.extend(data.get("results", []))

        if "_links" in data and "next" in data["_links"]:
            url = CONFLUENCE_BASE_URL + data["_links"]["next"]
            params = None  
        else:
            break

    normalized_pages = []

    for p in pages:
        normalized_pages.append({
            "page_id": p["id"],
            "space_key": space_key,
            "title": p["title"],
            "version": p["version"]["number"],
            "content": p["body"]["storage"]["value"]
        })

    return normalized_pages
