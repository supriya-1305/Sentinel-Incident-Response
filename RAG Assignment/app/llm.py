import os
from typing import Any, Dict, List

from google import genai

from app.config import GEMINI_API_KEY, GEMINI_MODEL

if GEMINI_API_KEY:
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    client = None


def build_system_prompt() -> str:
    return """
You are a Tier-3 SOC Incident Commander.
You must produce a 3-step Incident Response Plan grounded strictly in the retrieved playbook evidence.
Use the exact structure:
[THOUGHT PROCESS]
1. Analyze the incident and evidence.
2. Identify the three most relevant playbook steps.
3. Prepare a concise, command-ready plan.
[ACTION PLAN]
1. Triage: ...
2. Containment: ...
3. Eradication: ...
[CITATIONS]
- Source: <filename>, Page: <page>
- Source: <filename>, Page: <page>
If any claim cannot be backed by the context, explicitly state that it is unsupported by retrieved evidence and trigger a Hallucination Warning.
"""


def _append_citations(answer: str, context_chunks: List[Dict[str, Any]]) -> str:
    if not context_chunks:
        return answer

    citation_lines = []
    for chunk in context_chunks:
        metadata = chunk.get("metadata", {}) or {}
        source = metadata.get("source", "unknown")
        page = metadata.get("page", "unknown")
        citation_lines.append(f"- Source: {source}, Page: {page}")

    citation_block = "\n".join(citation_lines)
    if "[CITATIONS]" in answer:
        return answer
    return f"{answer}\n\n[CITATIONS]\n{citation_block}"


def generate_plan(query: str, context_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
    cleaned_context = []
    for chunk in context_chunks:
        cleaned_context.append({
            "source": chunk.get("metadata", {}).get("source", "unknown"),
            "page": chunk.get("metadata", {}).get("page", "unknown"),
            "text": chunk.get("text", "")
        })

    if client is None:
        answer = "Gemini API key not configured. Returning offline fallback plan."
        return {"status": "degraded", "answer": _append_citations(answer, context_chunks), "citations": cleaned_context}

    prompt = f"""
System Prompt:
{build_system_prompt()}

User Incident:
{query}

Retrieved Evidence:
{cleaned_context}

Return a concise response with explicit citations to the source and page numbers.
"""

    try:
        response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        text = response.text if hasattr(response, "text") else str(response)
        answer = _append_citations(text, context_chunks)
        return {"status": "ok", "answer": answer, "citations": cleaned_context}
    except Exception as exc:
        answer = f"System Degradation Warning: Gemini generation failed ({exc})."
        return {"status": "degraded", "answer": _append_citations(answer, context_chunks), "citations": cleaned_context}
