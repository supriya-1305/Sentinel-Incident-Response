# Sentinel-Incident-Response
AI-powered cybersecurity application built using Retrieval-Augmented Generation (RAG).

## Overview

Sentinel Incident Response is an AI-powered cybersecurity application that automates Security Operations Center (SOC) incident response workflows using Retrieval-Augmented Generation (RAG).

The system analyzes security incident tickets, retrieves relevant evidence from indexed cybersecurity playbooks and compliance documents, reranks the retrieved content, and generates structured incident response plans with supporting citations.

The application is built using Streamlit, Google Gemini, ChromaDB, and a RAG pipeline that combines semantic retrieval with large language model reasoning.

---

## Features

* Upload and index cybersecurity playbooks in PDF format
* Automatic PDF ingestion and page-level chunking
* Vector storage and semantic search using ChromaDB
* Retrieval-Augmented Generation (RAG)
* Gemini-powered incident analysis and response generation
* Evidence-based response plans with source citations
* Interactive Streamlit user interface
* Demo corpus seeding for testing and evaluation

---

## System Architecture

### Document Processing Pipeline

1. PDF Upload
2. Text Extraction
3. Page-Level Chunking
4. Embedding Generation
5. ChromaDB Vector Indexing

### Query Processing Pipeline

1. Security Incident Ticket Submission
2. Semantic Retrieval of Relevant Chunks
3. LLM-Based Reranking
4. Evidence Collection
5. Incident Response Plan Generation
6. Citation Generation

---

## Application Workflow

### Step 1: Upload Playbooks

Users upload cybersecurity playbooks, security standards, and incident response documentation through the Streamlit interface.

### Step 2: Document Indexing

The system processes uploaded PDFs and creates page-level chunks that are indexed in ChromaDB for efficient semantic retrieval.

### Step 3: Incident Submission

Users enter a security incident ticket describing the observed issue.

Example:

> Authenticator management failure — 14 user accounts found with passwords not rotated in over 180 days, violating IA-5 authenticator management policy.

### Step 4: Evidence Retrieval

The RAG engine retrieves the most relevant playbook sections from the indexed corpus and reranks the results.

### Step 5: Response Generation

Gemini generates a structured Incident Response Plan consisting of:

* Thought Process
* Action Plan
* Supporting Citations

---

## Example Output

### Thought Process

* Analyze the incident and available evidence
* Map findings to relevant security controls
* Identify appropriate response actions

### Action Plan

#### Triage

* Identify affected accounts
* Determine incident scope

#### Containment

* Force password resets
* Enable MFA enrollment

#### Eradication

* Restore compliance with security policies
* Validate authentication controls

### Citations

Generated responses include references to the retrieved source documents and page numbers.

---

## Technology Stack

* Python
* Streamlit
* Google Gemini API
* ChromaDB
* Retrieval-Augmented Generation (RAG)
* Vector Embeddings
* PDF Processing Libraries

---

## Project Structure

```text
RAG Assignment/
│
├── app/
│   ├── config.py
│   ├── guardrails.py
│   ├── ingestion.py
│   ├── llm.py
│   ├── rag.py
│   └── ui.py
│
├── data/
│   ├── chroma/
│   ├── demo/
│   └── uploads/
│
├── tests/
│
├── app.py
├── requirements.txt
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/supriya-1305/Sentinel-Incident-Response.git
cd Sentinel-Incident-Response
```

### Create Virtual Environment

```bash
python -m venv .venv
```

### Activate Environment

#### Windows

```bash
.venv\Scripts\activate
```

#### macOS/Linux

```bash
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=YOUR_API_KEY
```

### Run Application

```bash
streamlit run app.py
```

---

## Use Cases

* Security Operations Centers (SOC)
* Incident Response Automation
* Security Playbook Search
* Compliance and Audit Support
* Cybersecurity Knowledge Management
* AI-Assisted Security Investigations

---

## Key Capabilities Demonstrated

* PDF Ingestion
* Page-Level Chunking
* Vector Indexing with ChromaDB
* Semantic Retrieval
* LLM Reranking
* Evidence-Based Response Generation
* Citation-Aware Outputs
* Streamlit-Based User Experience

---

## Future Enhancements

* Multi-document incident correlation
* Automated threat intelligence integration
* SIEM integration
* User authentication and RBAC
* Incident severity scoring
* Advanced analytics dashboard

---

## Author

**R Supriya**

Sentinel Incident Response – RAG Workflow Automation for SOC Incident Response.
