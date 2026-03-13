import requests
from fastapi import APIRouter
from app.config import settings
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
CONFLUENCE_BASE_URL = settings.CONFLUENCE_URL
CONFLUENCE_EMAIL = settings.CONFLUENCE_EMAIL
CONFLUENCE_API_TOKEN = settings.CONFLUENCE_API_TOKEN
CONFLUENCE_SPACE = settings.CONFLUENCE_SPACE

@router.get("/pages")
def get_pages():
    """
    Fetch all Confluence pages from a space
    """
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content"
    
    params = {
        "spaceKey": CONFLUENCE_SPACE,
        "expand": "body.storage,version"
    }
    
    auth = (CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN)
    
    response = requests.get(url, params=params, auth=auth)
    
    return response.json()

# Get confluence page data by id

def extract_page_id(url: str) -> str:
    """
    Extract the Confluence PAGE_ID from the URL.
    Example:
    https://abc.atlassian.net/wiki/spaces/XYZ/pages/123456789/MyPage
    """
    path = urlparse(url).path
    parts = path.split("/")
    if "pages" in parts:
        idx = parts.index("pages")
        return parts[idx + 1]   
    raise ValueError("Invalid Confluence URL: Could not extract page ID")


def fetch_confluence_page(url: str) -> dict:
    """Fetch full page HTML content + metadata from Confluence REST API."""
    page_id = extract_page_id(url)

    api_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{page_id}"
    params = {"expand": "body.storage,version,space"}

    response = requests.get(
        api_url,
        params=params,
        auth=(CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN),
    )
    response.raise_for_status()

    data = response.json()

    html = data["body"]["storage"]["value"]
    version = (data.get("version") or {}).get("number")
    space_key = (data.get("space") or {}).get("key")

    return {
        "content": html,
        "html": html,
        "version": version,
        "title": data["title"],
        "space_key": space_key,
    }


#Helper func
def html_to_text(html: str) -> str:
    if isinstance(html, dict):
        html = html.get("html", "")
    if isinstance(html, bytes):
        html = html.decode('utf-8')
    
    soup = BeautifulSoup(html, "html.parser")
    return soup.get_text(separator="\n")

