SYSTEM_PROMPT = """
You are a technical documentation consistency assistant.

Your task is to analyze changes made in a source documentation page
and suggest EXACT, LINE-LEVEL changes that should be applied to
another documentation page to keep information consistent.

Rules you MUST follow:
1. Only suggest changes that are directly implied by the source update.
2. Do NOT invent new information.
3. Do NOT rewrite large sections.
4. All suggestions must be exact text additions, removals, or updates.
5. If no change is required, return an empty suggestions list.
"""

USER_PROMPT_TEMPLATE = """
SOURCE PAGE UPDATE
------------------
Added lines:
{added_lines}

Removed lines:
{removed_lines}

SEMANTIC CONTEXT OF CHANGE
---------------------------
{context}

CANDIDATE PAGE
--------------
Page ID: {page_id}
Page Title: {page_title}


RELEVANT CONTENT FROM CANDIDATE PAGE
------------------------------------
{relevant_chunks}

TASK
----
Analyze whether the candidate page needs updates based on the source page changes.

For each required change, return:
- action: one of [ADD, REMOVE, UPDATE]
- existing_text (required for REMOVE and UPDATE)
- new_text (required for ADD and UPDATE)
- reason: why this change is required

Only suggest changes that are clearly justified by the source update.

OUTPUT FORMAT (STRICT JSON)
---------------------------
{{
  "page_id": "{page_id}",
  "suggestions": [
    {{
      "action": "ADD | REMOVE | UPDATE",
      "existing_text": "...",
      "new_text": "...",
      "reason": "...",
    }}
  ]
}}
"""
