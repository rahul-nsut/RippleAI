from typing import List
from app.suggestions.prompts.change_context_prompt import CHANGE_CONTEXT_PROMPT


def build_change_context_prompt(
    *,
    source_page_id: str,
    added_lines: List[str],
    removed_lines: List[str],
    source_chunk_content: str,
) -> str:

    print("starting build_change_context_prompt")
    return CHANGE_CONTEXT_PROMPT.format(
        source_page_id=source_page_id,
        added_lines=added_lines,
        removed_lines=removed_lines,
        source_chunk_content=source_chunk_content)