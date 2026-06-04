# Upwork API — Technical Support Bot

> Associate AI Developer Assignment · RAG System · June 2026

A Retrieval-Augmented Generation (RAG) chatbot that answers developer questions about the Upwork API accurately — using only the provided documentation. No hallucinations, no guessing.

---

## What It Does

- Reads the Upwork API documentation PDF **locally** — nothing leaves your machine
- Splits it into 500-char chunks and stores them as vectors in ChromaDB
- When you ask a question, it finds the **top 3 most relevant chunks**
- Sends those chunks + your question to **Meta-Llama-3.1-8B** via DeepInfra
- Returns a precise answer with **exact source snippets** and **response time**
- If the answer is not in the docs, it says so — it never fabricates information

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Framework | LangChain |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (runs locally, no API call) |
| Vector DB | ChromaDB (persisted to disk) |
| LLM | Meta-Llama-3.1-8B-Instruct-Turbo via DeepInfra |
| UI | Streamlit |

---

## Project Structure

```
upwork-rag/
├── app.py                         # Streamlit UI (Part B3)
├── rag_pipeline.py                # Full RAG pipeline (Parts A1 – B2)
├── requirements.txt               # All Python dependencies
├── .env                           # Your API key — never commit this
├── .env.example                   # Safe placeholder to share
├── API Documentation Partial.pdf  # Source document
├── TECHNICAL_SUMMARY.md           # Assignment writeup
└── chroma_db/                     # Auto-created after first build
```

---

## Setup

### 1 · Create a virtual environment

```bash
python -m venv venv
```

```bash
# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 2 · Install dependencies

```bash
pip install -r requirements.txt
```

### 3 · Configure environment variables

Copy the example file and add your DeepInfra API key:

```bash
copy .env.example .env        # Windows
cp   .env.example .env        # Mac / Linux
```

Your `.env` should contain:

```
DEEPINFRA_API_KEY=your_api_key_here
DEEPINFRA_BASE_URL=https://api.deepinfra.com/v1/openai
MODEL_NAME=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
```

### 4 · Place the PDF in the project folder

```
API Documentation Partial.pdf
```

### 5 · Run the app

```bash
streamlit run app.py
```

---

## How to Use

1. Open your browser at `http://localhost:8501`
2. In the **left sidebar**, click **Build Knowledge Base**
   - Reads the PDF → chunks it → embeds locally → saves to ChromaDB
   - Takes ~30 seconds on first run; instant every run after that
3. Once you see **"Indexed X chunks"** — start chatting

> **Tip:** You only need to click "Build Knowledge Base" once.
> The index is saved to disk and loaded automatically on every restart.

---

## Ground Truth Validation

Run these three questions to confirm the bot is working correctly:

| # | Question | Expected Answer |
|---|---|---|
| Q1 | What is the specific rate limit (RPS) for the Upwork API, per key or per IP? | Hallucination guard fires — not in the docs |
| Q2 | How long is an OAuth access token valid? | **24 hours** (86400 seconds) |
| Q3 | Can I use Client Credentials Grant to access a user's private contract details? | **No** — enterprise only, server-to-server only |

---

## RAG Pipeline

```
PDF File
   │
   ▼
load_pdf()            →  Extract text, print sanity check (page count + char count + sample)
   │
   ▼
chunk_text()          →  500-char chunks, 50-char overlap (RecursiveCharacterTextSplitter)
   │
   ▼
build_vector_store()  →  Local embeddings (all-MiniLM-L6-v2) → persist in ChromaDB
   │
   ▼  ── at query time ──
retrieve_chunks()     →  Embed query → cosine similarity search → top 3 chunks
   │
   ▼
generate_answer()     →  System prompt + chunks + question → DeepInfra → answer + latency
```

---

## Key Design Decisions

### Why local embeddings?
The assignment prohibits uploading source documentation to any public LLM.
`sentence-transformers/all-MiniLM-L6-v2` runs entirely on your machine — the Upwork docs never leave your system.

### Why 500 chars / 50-char overlap?
API documentation contains multi-line code blocks (curl, JSON, GraphQL). A 50-char overlap ensures code snippets split at a boundary still appear complete in at least one chunk.

### Why temperature 0.1?
Low temperature keeps the model deterministic and factual — critical for a support bot where fabricated token TTLs or fake endpoints cause real developer errors.

### Why top-3 retrieval?
Enough context for accurate answers, while keeping prompts short and API latency low.

### Why ChromaDB persistence?
Rebuilding the vector index on every run would take 30–60 seconds. Persisting to disk means the index loads instantly on every restart after the first build.

---

## Important Notes

- **Never commit `.env`** — it contains your live API key
- `chroma_db/` is auto-generated — delete it to force a full rebuild
- First run downloads the embedding model (~80 MB) — all runs after are instant

---

## Dependencies

```
streamlit
langchain
langchain-community
langchain-text-splitters
chromadb
sentence-transformers
openai
python-dotenv
PyPDF2
```

---

*Built for the ProAnalyst AI Team · Associate AI Developer Assignment · June 2026*
