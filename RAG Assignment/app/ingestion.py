import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
import fitz
from chromadb.config import Settings

from app.config import CHROMA_DIR, UPLOAD_DIR

client = chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
collection = client.get_or_create_collection(name="sentinel_playbooks")


def _read_pdf_pages(file_path: Path) -> List[Dict[str, Any]]:
    doc = fitz.open(file_path)
    chunks = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text().strip()
        if text:
            chunks.append({"page": page_num + 1, "text": text})
    doc.close()
    return chunks


def ingest_pdf(file_path: Path, source_name: Optional[str] = None) -> Dict[str, Any]:
    source_name = source_name or file_path.name
    pages = _read_pdf_pages(file_path)
    documents = []
    metadatas = []
    ids = []
    for page_data in pages:
        documents.append(page_data["text"])
        metadatas.append({"source": source_name, "page": page_data["page"]})
        ids.append(f"{source_name.replace('.pdf', '')}-p{page_data['page']}")
    if documents:
        collection.add(documents=documents, metadatas=metadatas, ids=ids)
    return {"source": source_name, "pages": len(pages), "chunks": len(documents)}


def _normalize_metadata(metadata: Any) -> Dict[str, Any]:
    if isinstance(metadata, dict):
        return metadata
    if isinstance(metadata, (list, tuple)):
        return metadata[0] if metadata and isinstance(metadata[0], dict) else {}
    return {}


def list_documents() -> List[Dict[str, Any]]:
    results = collection.get(include=["metadatas"])
    docs = []
    for metadata in results.get("metadatas", []) or []:
        metadata_dict = _normalize_metadata(metadata)
        if metadata_dict:
            docs.append({"source": metadata_dict.get("source"), "page": metadata_dict.get("page")})
    return docs


def delete_document(source_name: str) -> None:
    results = collection.get(include=["metadatas"])
    ids_to_delete = []
    for metadata, record_id in zip(results.get("metadatas", []) or [], results.get("ids", []) or []):
        metadata_dict = _normalize_metadata(metadata)
        if metadata_dict.get("source") == source_name:
            ids_to_delete.append(record_id)
    if ids_to_delete:
        collection.delete(ids=ids_to_delete)


def update_document(source_name: str, file_path: Path) -> Dict[str, Any]:
    delete_document(source_name)
    return ingest_pdf(file_path, source_name=source_name)


def seed_demo_docs() -> None:
    demo_dir = Path(__file__).resolve().parent.parent / "data" / "demo"
    demo_dir.mkdir(parents=True, exist_ok=True)
    if not (demo_dir / "playbook_demo.pdf").exists():
        sample_text = """
        Incident Response Playbook
        Triage: Validate the alert, identify impacted assets and correlate with identity and endpoint telemetry.
        Containment: Isolate affected systems, block malicious indicators and preserve evidence.
        Eradication: Remove persistence mechanisms, reset credentials and recover services.
        """
        from reportlab.pdfgen import canvas
        c = canvas.Canvas(str(demo_dir / "playbook_demo.pdf"))
        c.drawString(40, 780, sample_text)
        c.save()
    if not collection.count():
        ingest_pdf(demo_dir / "playbook_demo.pdf", source_name="playbook_demo.pdf")
