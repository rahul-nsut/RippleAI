import json
from typing import List, Dict, Tuple

from app.suggestions.prompts.change_suggestions import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def build_suggestion_prompt(
    *,
    source_page_id: str,
    added_lines: List[str],
    removed_lines: List[str],
    target_page_id: str,
    target_page_title: str,
    target_chunks: List[Dict],
    context: str,
) -> Tuple[str, str]:
    """
    Builds the final prompt sent to the LLM.
    Returns (system_prompt, user_prompt).
    """

    user_prompt = USER_PROMPT_TEMPLATE.format(
        source_page_id=source_page_id,
        added_lines=json.dumps(added_lines, indent=2),
        removed_lines=json.dumps(removed_lines, indent=2),
        page_id=target_page_id,
        page_title=target_page_title,
        relevant_chunks=json.dumps(target_chunks, indent=2),
        context=context,
    )

    return SYSTEM_PROMPT, user_prompt
