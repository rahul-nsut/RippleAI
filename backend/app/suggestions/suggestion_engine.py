from typing import Dict, List, Any
import json

from app.suggestions.llm.client import OpenRouterLLMClient
from app.suggestions.prompts.build_suggestion_prompt import build_suggestion_prompt


class LLMResponseError(Exception):
    pass


def generate_page_suggestions(
    *,
    source_page_id: str,
    added_lines: List[str],
    removed_lines: List[str],
    candidate_pages: List[Dict],
    relevant_chunks: Dict[str, List[Dict]],
    context: str,
) -> List[Dict]:
    """
    Step-3:
    Generate exact ADD / REMOVE / UPDATE suggestions per candidate page
    using LLM reasoning over relevant chunks only.

    Returns:
    [
      {
        page_id,
        confidence,
        suggestions: [
          {
            action: ADD | REMOVE | UPDATE,
            old,
            new,
            reason
          }
        ]
      }
    ]
    """

    results = []
    llm_client = OpenRouterLLMClient()

    for candidate in candidate_pages:
        page_id = candidate["page_id"]

        chunks = relevant_chunks.get(page_id)
        if not chunks:
            results.append({
                "page_id": page_id,
                "confidence": 0.0,
                "suggestions": []
            })
            continue

        system_prompt, user_prompt = build_suggestion_prompt(
            source_page_id=source_page_id,
            added_lines=added_lines,
            removed_lines=removed_lines,
            target_page_id=page_id,
            target_page_title=candidate["title"],
            target_chunks=chunks,
            context=context,
        )

        parsed = llm_client.chat(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=0.1,
            max_tokens=1200,
        )

        if (
            not isinstance(parsed, dict)
            or "page_id" not in parsed
            or "suggestions" not in parsed
        ):
            raise LLMResponseError(
                f"Invalid LLM response structure for page {page_id}"
            )

        results.append(parsed)

    return results
