import difflib
from typing import Dict, List


def compute_text_diff(old_text: str, new_text: str) -> Dict[str, List[str]]:
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    print("Old lines:", old_lines)
    print("New lines:", new_lines)

    matcher = difflib.SequenceMatcher(
        a=old_lines,
        b=new_lines,
        autojunk=False  
    )

    added = []
    removed = []

    print("Op codes:", matcher.get_opcodes())
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "insert":
            added.extend(new_lines[j1:j2])
        elif tag == "delete":
            removed.extend(old_lines[i1:i2])
        elif tag == "replace":
            removed.extend(old_lines[i1:i2])
            added.extend(new_lines[j1:j2])

    return {
        "added": added,
        "removed": removed
    }
