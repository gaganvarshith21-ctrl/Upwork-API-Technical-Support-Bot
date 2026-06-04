#Upwork API — Technical Support Bot

A Retrieval-Augmented Generation (RAG) chatbot built to answer developer questions using the Upwork API documentation. The assistant retrieves relevant documentation sections from a local ChromaDB vector store and uses Meta-Llama-3.1-8B via DeepInfra to generate grounded, accurate responses — strictly from the docs, never from assumptions.

---

## Live Demo

- **Application:** https://upwork-technical-support-assistant.streamlit.app/
- **GitHub:** https://github.com/chowdary-15/Upwork-Technical-Support-Assistant

---

## Project Overview

This project was developed as a technical support assistant for developers working with the Upwork API.

Rather than relying on a language model's internal knowledge, the application retrieves relevant content from the official documentation and uses that context to answer questions accurately. If the answer is not in the documentation, the bot says so — it never fabricates information.

The system supports questions related to:

- OAuth 2.0 authentication flows
- Access tokens and refresh tokens
- Authorization Code, Implicit, and Client Credentials grants
- GraphQL APIs and error handling
- Upwork Enterprise API documentation

---

## How It Works

1. **PDF → chunks** (500 chars, 50 overlap)
2. **Chunks embedded locally** — no upload to any LLM
3. **Question → find top 3 similar chunks** via cosine similarity
4. **Chunks + question → LLaMA generates answer**
5. **Answer grounded strictly in the docs**

---

## Features

### Document Processing
- Loads Upwork API documentation from a PDF file using PyPDF2
- Extracts text page by page with a sanity check (character count + sample)
- Splits content using `RecursiveCharacterTextSplitter` (500 chars, 50 overlap)

### Retrieval-Augmented Generation (RAG)
- Converts document chunks into vector embeddings using a local Sentence Transformer model
- Stores and retrieves embeddings using ChromaDB (persisted to disk)
- Retrieves top-3 most relevant chunks per query using cosine similarity

### Hallucination Reduction
- Retrieved documentation is the only source of truth
- System prompt enforces strict guardrails — model cannot answer outside the docs
- Returns a fixed fallback response when the answer is not found in context

### Streamlit Interface
- Clean, centered chat interface
- Sidebar shows pipeline explanation and Build / Rebuild button
- Displays answer, response latency, and exact source chunks per query

### Local Vector Store
- ChromaDB index persisted to disk — no rebuild needed on restart
- Embedding model runs fully locally — source docs never leave your machine
- One-click rebuild via sidebar when documentation changes

---

## System Architecture

```
PDF File
   │
   ▼
load_pdf()             →  Extract text · sanity check (pages, chars, sample)
   │
   ▼
chunk_text()           →  500-char chunks · 50-char overlap · RecursiveCharacterTextSplitter
   │
   ▼
build_vector_store()   →  Local embeddings (all-MiniLM-L6-v2) · persist to ChromaDB
   │
   ▼  ── at query time ──
retrieve_chunks()      →  Embed query · cosine similarity · return top-3 chunks
   │
   ▼
generate_answer()      →  System prompt + chunks + question → DeepInfra LLM → answer + latency
```

---

## Technology Stack

### Frontend
- Streamlit

### Backend
- Python 3.10+

### RAG Components
- LangChain
- ChromaDB
- Sentence Transformers — `all-MiniLM-L6-v2` (local, ~80 MB)

### LLM Integration
- DeepInfra API (OpenAI-compatible interface)
- Model: `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo`

### Document Processing
- PyPDF2

---

## Project Structure

```
Upwork-Technical-Support-Assistant/
│
├── app.py                         # Streamlit UI
├── rag_pipeline.py                # Full RAG pipeline (ingest → retrieve → generate)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variable template
├── API Documentation Partial.pdf  # Source documentation
├── TECHNICAL_SUMMARY.md           # Assignment writeup
└── chroma_db/                     # Auto-generated vector index (not committed)
```

---

## Installation

### 1 · Clone the repository

```bash
git clone https://github.com/chowdary-15/Upwork-Technical-Support-Assistant.git
cd Upwork-Technical-Support-Assistant
```

### 2 · Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3 · Install dependencies

```bash
pip install -r requirements.txt
```

### 4 · Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template:

```
DEEPINFRA_API_KEY=your_api_key_here
DEEPINFRA_BASE_URL=https://api.deepinfra.com/v1/openai
MODEL_NAME=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
```

### 5 · Run the application

```bash
streamlit run app.py
```

On first run:
- Click **Build / Rebuild Knowledge Base** in the sidebar
- The app reads the PDF, chunks it, embeds locally, and saves to ChromaDB
- Once indexed, the chatbot is ready — index auto-loads on every restart after that

---

## Ground Truth Validation

| # | Question | Expected Answer |
|---|---|---|
| Q1 | What is the rate limit (RPS) for the Upwork API per key or IP? | Not in docs — hallucination guard fires |
| Q2 | How long is an OAuth access token valid? | **24 hours** (86400 seconds) |
| Q3 | Can Client Credentials Grant access a user's private contract details? | **No** — enterprise only, server-to-server only |

---

## Challenges Solved

### Context Preservation Across Chunks
API documentation contains multi-line code blocks — curl commands, JSON responses, GraphQL queries. Splitting at exactly 500 characters could cut a code block mid-statement. A 50-character overlap ensures that content split at a boundary still appears complete in at least one chunk.

### Hallucination Control
The partial documentation provided does not cover every topic. Without guardrails, the LLM fabricates plausible but incorrect values. A strict system prompt forces the model to respond with a fixed fallback phrase when retrieved chunks do not contain the answer.

### Data Privacy Compliance
All embeddings are generated locally using `sentence-transformers/all-MiniLM-L6-v2`. The Upwork API documentation is never uploaded to any external embedding API — only the user's question and retrieved snippets are sent to DeepInfra.

### API Latency Transparency
DeepInfra response times vary between 2–8 seconds depending on load. Rather than letting the UI freeze silently, response latency is measured with `time.time()` and displayed as a metric after every answer.

---

## Important Notes

- **Never commit your `.env` file** — it contains your live API key
- `chroma_db/` is auto-generated — add it to `.gitignore`
- The embedding model (~80 MB) downloads automatically on first run — all subsequent runs are instant

---

*Built for the ProAnalyst AI Team · Associate AI Developer Assignment · June 2026*
HEREDOC
echo "Done"
