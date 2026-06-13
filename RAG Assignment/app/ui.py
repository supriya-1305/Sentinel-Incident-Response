import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

from app.config import UPLOAD_DIR
from app.guardrails import build_hallucination_warning, validate_query
from app.ingestion import delete_document, ingest_pdf, list_documents, seed_demo_docs, update_document
from app.llm import generate_plan
from app.rag import build_context


st.set_page_config(page_title="Sentinel Incident Response", layout="wide")


def render_sidebar() -> None:
    with st.sidebar:
        st.title("Sentinel Incident Response")
        st.caption("RAG workflow automation for SOC incident response")
        uploaded_files = st.file_uploader("Upload playbooks / PDFs", type=["pdf"], accept_multiple_files=True)
        if uploaded_files:
            for uploaded_file in uploaded_files:
                path = UPLOAD_DIR / uploaded_file.name
                with open(path, "wb") as handle:
                    handle.write(uploaded_file.getbuffer())
                ingest_pdf(path, source_name=uploaded_file.name)
                st.success(f"Indexed {uploaded_file.name}")

        st.subheader("Document Management")
        docs = list_documents()
        if docs:
            for doc in docs:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"{doc['source']} · page {doc['page']}")
                with col2:
                    if st.button("Delete", key=f"del-{doc['source']}-{doc['page']}"):
                        delete_document(doc["source"])
                        if hasattr(st, "rerun"):
                            st.rerun()
                        else:
                            st.experimental_rerun()
        else:
            st.info("No indexed playbooks yet.")

        if st.button("Seed Demo Corpus"):
            seed_demo_docs()
            st.success("Demo corpus seeded")


def render_main() -> None:
    st.header("SOC Incident Workflow Automation")
    st.info("This workflow automates incident response over a 5,000+ page playbook corpus using retrieval-augmented generation.")
    st.write("Enter a security incident ticket and let the system retrieve playbook evidence, rerank it, and generate a structured 3-step response.")

    query = st.text_area("Incident Ticket", placeholder="e.g. Phishing alert on executive laptop")
    if st.button("Generate Incident Response Plan") and query:
        allowed, rejection = validate_query(query)
        if not allowed:
            st.error(rejection)
            return

        with st.spinner("Retrieving and reranking context..."):
            context = build_context(query)
            raw_chunks = context.get("raw_chunks", [])
            reranked_chunks = context.get("reranked_chunks", [])

        st.subheader("Retrieved Evidence")
        st.caption(f"Top {len(reranked_chunks)} reranked chunks")
        for chunk in reranked_chunks:
            st.write(f"- {chunk.get('text', '')[:500]} ...")
            st.caption(f"Source: {chunk.get('metadata', {}).get('source', 'unknown')} | Page: {chunk.get('metadata', {}).get('page', 'unknown')}")

        with st.spinner("Generating response with Gemini..."):
            result = generate_plan(query, reranked_chunks)

        st.subheader("Incident Response Plan")
        if result.get("status") == "degraded":
            st.warning(result.get("answer", "System Degradation Warning"))
            st.info("Raw retrieved chunks are shown below for analyst continuity.")
            for chunk in raw_chunks:
                st.code(f"Source: {chunk.get('metadata', {}).get('source', 'unknown')} | Page: {chunk.get('metadata', {}).get('page', 'unknown')}\n{chunk.get('text', '')[:1200]}")
        else:
            warning = build_hallucination_warning(reranked_chunks, result.get("answer", ""))
            if warning:
                st.warning(warning)
            st.success("Structured plan generated")
            st.write(result.get("answer", ""))

        st.subheader("Playbook Citations")
        citations = result.get("citations", []) or []
        if citations:
            for citation in citations:
                source = citation.get("source", "unknown")
                page = citation.get("page", "unknown")
                st.write(f"- {source} · Page {page}")
        else:
            st.info("No citations were generated for this run.")


def app() -> None:
    render_sidebar()
    render_main()


if __name__ == "__main__":
    app()
