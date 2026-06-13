import re
from typing import Tuple

BLOCKED_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"bypass",
    r"delete all",
    r"exfiltrate",
    r"steal credentials",
]


def validate_query(query: str) -> Tuple[bool, str]:
    normalized = query.lower()
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, normalized):
            return False, f"Input rejected: suspicious prompt pattern detected ({pattern})."
    if len(query.strip()) < 8:
        return False, "Input rejected: query is too short."
    if any(token in normalized for token in ["illegal", "harmful", "malware", "attack"]):
        if "incident" not in normalized and "security" not in normalized:
            return False, "Input rejected: out-of-scope or unsafe request."
    return True, ""


def build_hallucination_warning(context_chunks: list[dict], answer: str) -> str:
    if not context_chunks:
        return "Hallucination Warning: no grounded context was retrieved."
    if any(keyword in answer.lower() for keyword in ["probably", "might", "could", "assume"]):
        return "Hallucination Warning: answer contains tentative language without explicit support from the retrieved context."
    return ""
