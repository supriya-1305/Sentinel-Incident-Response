import os
from typing import Any, Dict, List

try:
    from flashrank import Ranker, RerankRequest
except ImportError:  # pragma: no cover - broad fallback for package variation
    Ranker = None
    RerankRequest = None

from app.ingestion import collection

RERANKER = None
if Ranker is not None:
    try:
        RERANKER = Ranker(model_name="ms-marco-TinyBERT-L-2-v2")
    except Exception:
        RERANKER = None


def retrieve_chunks(query: str, top_k: int = 20) -> List[Dict[str, Any]]:
    results = collection.query(query_texts=[query], n_results=top_k, include=["documents", "metadatas", "distances"])
    chunks = []

    documents = results.get("documents", []) or []
    metadatas = results.get("metadatas", []) or []
    distances = results.get("distances", []) or []

    if not documents:
        return chunks

    first_documents = documents[0] or []
    first_metadatas = metadatas[0] if len(metadatas) > 0 else []
    first_distances = distances[0] if len(distances) > 0 else []

    for doc, meta, dist in zip(first_documents, first_metadatas, first_distances):
        chunks.append({"text": doc, "metadata": meta or {}, "distance": dist})
    return chunks


def rerank_chunks(query: str, chunks: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
    if not chunks:
        return []

    if RERANKER is None or RerankRequest is None:
        return [
            {**chunk, "rerank_score": 1.0 - (index / max(len(chunks), 1))}
            for index, chunk in enumerate(chunks[:top_n])
        ]

    request = RerankRequest(
        query=query,
        passages=[{"id": idx, "text": chunk["text"]} for idx, chunk in enumerate(chunks)],
    )
    scores = RERANKER.rerank(request)
    ranked = []
    for score_item in scores[:top_n]:
        idx = score_item.get("id")
        if idx is None or idx >= len(chunks):
            continue
        chunk = chunks[idx]
        ranked.append({**chunk, "rerank_score": score_item.get("score", 0.0)})
    return ranked


def clean_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for chunk in chunks:
        text = chunk.get("text", "")
        text = " ".join(text.split())
        if text:
            cleaned.append({**chunk, "text": text})
    return cleaned


def build_context(query: str) -> Dict[str, Any]:
    raw = retrieve_chunks(query, top_k=20)
    reranked = rerank_chunks(query, raw, top_n=5)
    cleaned = clean_chunks(reranked)
    return {"raw_chunks": raw, "reranked_chunks": cleaned}
