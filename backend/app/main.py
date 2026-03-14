from fastapi import FastAPI, HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from app.apis.confluence import router as confluence_router
from app.apis.ingest import ingest_document
from app.core.vectorstore import get_vectorstore
from app.apis.confluence import fetch_confluence_page, html_to_text
import re
from app.apis.qna_agent import answer_question
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import SessionLocal
from sync.detect_changes import detect_confluence_changes, confluence_html_to_text
from app.db.models import ConfluencePage
from pydantic import BaseModel
from sync.apply_sync import apply_sync
from app.suggestions.candidate.candidate_selection import select_candidate_pages
from app.suggestions.candidate.candidate_selection import _build_query_text
from app.suggestions.chunk_extractor import extract_relevant_chunks_from_candidate_pages
from app.suggestions.prompts.build_suggestion_prompt import build_suggestion_prompt
from app.suggestions.prompts.build_change_context_prompt import build_change_context_prompt
from app.suggestions.source_context.extractor import extract_source_context
from app.suggestions.llm.client import OpenRouterLLMClient
from app.db.models import Base
from app.db.session import engine
from app.apis.auth import router as auth_router
from app.auth.dependencies import get_current_user
from app.db.models import User


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Knowledge Base Auto Updater")
@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)
def debug_env():
    print("DATABASE_URL:", os.getenv("DATABASE_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Confluence-specific routes
app.include_router(confluence_router, prefix="/confluence")
app.include_router(auth_router, prefix="/auth")
class SyncPreviewRequest(BaseModel):
    space_key: str

class CommitSyncRequest(BaseModel):
    url: str

class GetCandidatesRequest(BaseModel):
    source_page_id: str
    added_lines: list[str]
    removed_lines: list[str]

class GetRelevantChunksRequest(BaseModel):
    source_page_id: str
    added_lines: list[str]
    removed_lines: list[str]

class SuggestionRequest(BaseModel):
    source_page_id: str
    added_lines: list[str]
    removed_lines: list[str]


def _filter_suggestions_by_candidate_content(
    raw_suggestions: list[dict],
    candidate_chunks: list[dict],
) -> list[dict]:
    """
    Guardrail to drop hallucinated updates:
    - UPDATE/DELETE must reference existing_text present in candidate chunks.
    - ADD should not duplicate text already present in candidate chunks.
    """
    candidate_text = "\n".join(chunk.get("content", "") for chunk in candidate_chunks)
    filtered = []

    for suggestion in raw_suggestions:
        action = suggestion.get("action")
        existing_text = (suggestion.get("existing_text") or "").strip()
        new_text = (suggestion.get("new_text") or "").strip()

        if action in {"UPDATE", "DELETE", "REMOVE"}:
            if not existing_text or existing_text not in candidate_text:
                continue

        if action == "ADD":
            if not new_text or new_text in candidate_text:
                continue

        if action == "UPDATE":
            if not new_text:
                continue

        filtered.append(suggestion)

    return filtered

@app.get("/")
def root():
    return {"message": "AI doc updater is running"}

@app.api_route("/health", methods=["GET", "HEAD"])
def health():
    return {"status": "ok"}

@app.post("/ingest")
def ingest(doc_id: str, url: str):
    match = re.search(r"/pages/(\d+)", url)
    if not match:
        match = re.search(r"pageId=(\d+)", url)
    page_id = match.group(1)

    html = fetch_confluence_page(url) 
    text = html_to_text(html)
    title= html["title"]

    ingest_document(doc_id, text, url, title)

    return {"message": "Ingested Successfully", "page_id": page_id}

@app.get("/search")
def search_data(q: str): 
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(q, k=3)

    return [
        {
            "text": r.page_content,
            "metadata": r.metadata
        }
        for r in results
    ]

executor = ThreadPoolExecutor(max_workers=2)

@app.post("/agentic-qna")
async def qna(question: str, current_user: User = Depends(get_current_user)):
    logger.info(f"Endpoint called with question: {question}")
    try:
        loop = asyncio.get_event_loop()
        logger.info("About to call answer_question in executor")
        answer = await loop.run_in_executor(
            executor, 
            answer_question, 
            question
        )
        logger.info("Got answer back from executor")
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Exception in qna endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/data/documents")
def get_documents(current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(ConfluencePage)
            .order_by(ConfluencePage.last_synced_at.desc())
            .all()
        )

        pages = []
        for row in rows:
            plain_text = confluence_html_to_text(row.last_synced_content or "")
            preview = plain_text[:200]
            source = (
                f"https://rahul-docs-ai-update.atlassian.net/wiki/spaces/"
                f"{row.space_key}/pages/{row.page_id}"
                if row.space_key
                else ""
            )
            pages.append({
                "doc_id": row.page_id,
                "title": row.title,
                "source": source,
                "preview": preview,
            })

        return pages
    finally:
        db.close()

@app.post("/sync-pages")
def preview_sync(request: SyncPreviewRequest, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        changes = detect_confluence_changes(
            db=db,
            space_key=request.space_key
        )


        if not changes or all(c["type"] == "UNCHANGED" for c in changes):
            print("No changes found in syncing")
            return {
                "status": "ALREADY_SYNCED",
                "changes": []
            }

        print("Done syncing")
        return {
            "status": "CHANGES_FOUND",
            "changes": changes
        }
    finally:
        db.close()

@app.post("/commit-sync-to-db")
def commit_sync_to_db(payload: CommitSyncRequest, current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    url = payload.url
    if not url:
        return {"error": "url is required"}

    apply_sync(db=db, url=url)

    return {
        "status": "SYNCED",
        "url": url
    }

@app.post("/get-candidates")
def get_candidate_pages(
    payload: GetCandidatesRequest,
    current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        candidates = select_candidate_pages(
            db=db,
            source_page_id=payload.source_page_id,
            added_lines=payload.added_lines,
            removed_lines=payload.removed_lines,
        )
        return {
            "candidates": candidates
        }
    finally:
        db.close()


@app.post("/get-relevant-chunks")
#A common API that will first get the candidate pages and then extract the relevant chunks from the candidate pages
def get_relevant_chunks(
    payload: GetRelevantChunksRequest,
    current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    candidates = select_candidate_pages(
        db=db,
        source_page_id=payload.source_page_id,
        added_lines=payload.added_lines,
        removed_lines=payload.removed_lines,
    )
    relevant_chunks = extract_relevant_chunks_from_candidate_pages(
        candidate_page_ids=[candidate["page_id"] for candidate in candidates],
        query_text=_build_query_text(payload.added_lines, payload.removed_lines),
    )
    return {
        "relevant_chunks": relevant_chunks
    }


@app.post("/get-suggestions")
def generate_suggestions(
    payload: SuggestionRequest,
    current_user: User = Depends(get_current_user)):
    db: Session = SessionLocal()
    try:
        # Step 1: Candidate selection
        candidates = select_candidate_pages(
            db=db,
            source_page_id=payload.source_page_id,
            added_lines=payload.added_lines,
            removed_lines=payload.removed_lines,
        )

        if not candidates:
            return {
                "source_page_id": payload.source_page_id,
                "suggestions": []
            }

        # Step 2: Extract source context and get semantic summary via LLM
        source_contexts = extract_source_context(
            source_page_id=payload.source_page_id,
            added_lines=payload.added_lines,
            removed_lines=payload.removed_lines,
        )

        llm_client = OpenRouterLLMClient()
        change_context = ""

        if source_contexts:
            source_chunk_content = "\n---\n".join(
                ctx["content"] for ctx in source_contexts
            )
        else:
            source_chunk_content = (
                "No exact source chunk match found for the changed lines. "
                "Infer semantic meaning from explicit added/removed lines."
            )
            logger.info(
                "[LLM Call 1] No source chunk matched exactly; falling back to explicit change lines only."
            )

        context_prompt = build_change_context_prompt(
            source_page_id=payload.source_page_id,
            added_lines=payload.added_lines,
            removed_lines=payload.removed_lines,
            source_chunk_content=source_chunk_content,
        )
        logger.info(
            "[LLM Call 1] Requesting change context summary for source page: %s",
            payload.source_page_id,
        )
        context_result = llm_client.chat(
            system_prompt="You are a technical documentation change analyst.",
            user_prompt=context_prompt,
            temperature=0.1,
            max_tokens=300,
        )
        change_context = context_result.get("summary", "")
        logger.info("[LLM Call 1] Semantic change context: %s", change_context)

        # Step 3: For each candidate → extract relevant chunks → generate suggestions
        suggestions = []
        query_text = _build_query_text(payload.added_lines, payload.removed_lines)

        for candidate in candidates:
            page_id = candidate["page_id"]
            confidence = candidate["confidence"]

            relevant_chunks = extract_relevant_chunks_from_candidate_pages(
                candidate_page_ids=[page_id],
                query_text=query_text,
            )
            chunks = relevant_chunks.get(page_id, [])

            if not chunks:
                continue

            system_prompt, user_prompt = build_suggestion_prompt(
                source_page_id=payload.source_page_id,
                added_lines=payload.added_lines,
                removed_lines=payload.removed_lines,
                target_page_id=page_id,
                target_page_title=candidate["title"],
                target_chunks=chunks,
                context=change_context,
            )

            logger.info("[LLM Call 2] Generating suggestions for candidate page: %s", page_id)
            llm_response = llm_client.chat(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=0.1,
                max_tokens=1200,
            )
            logger.info("[LLM Call 2] Got %d suggestion(s) for page: %s", len(llm_response.get("suggestions", [])), page_id)
            validated_suggestions = _filter_suggestions_by_candidate_content(
                llm_response.get("suggestions", []),
                chunks,
            )

            suggestions.append({
                "page_id": page_id,
                "title": candidate["title"],
                "confidence": confidence,
                "suggested_changes": {
                    "page_id": llm_response.get("page_id", page_id),
                    "suggestions": validated_suggestions,
                },
            })

        return {
            "source_page_id": payload.source_page_id,
            "suggestions": suggestions
        }
    finally:
        db.close()

## Need to get a API that fetches all pages for a space
