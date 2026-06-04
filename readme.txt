# Upwork API — Technical Support Bot
### Associate AI Developer Assignment | RAG System

A Retrieval-Augmented Generation (RAG) chatbot that answers developer questions about the Upwork API accurately, using only the provided documentation — no hallucinations.

---

## What It Does

- Reads the Upwork API documentation PDF locally
- Splits it into searchable chunks and stores them in ChromaDB
- When you ask a question, it finds the 3 most relevant chunks
- Sends those chunks + your question to Meta-Llama-3.1-8B (via DeepInfra)
- Returns a precise answer with sources and response time shown in the UI
- If the answer isn't in the docs, it says so — it never makes things up

---

## Tech Stack

| Layer | Tool |
|---|---|
| Language | Python 3.10+ |
| Framework | LangChain |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (local, no API) |
| Vector DB | ChromaDB (persisted to disk) |
| LLM | Meta-Llama-3.1-8B-Instruct-Turbo via DeepInfra |
| UI | Streamlit |

---

## Project Structure

```
upwork-rag/
├── app.py                        # Streamlit UI (Part B3)
├── rag_pipeline.py               # Full RAG pipeline (Parts A1–B2)
├── requirements.txt              # All dependencies
├── .env                          # Your API key (never commit this)
├── .env.example                  # Safe template to share
├── API Documentation Partial.pdf # Source document
├── TECHNICAL_SUMMARY.md          # Assignment technical writeup
└── chroma_db/                    # Auto-created after first build
```

---

## Setup Instructions

### 1. Clone / download the project
```bash
cd upwork-rag
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables
Copy `.env.example` to `.env` and fill in your DeepInfra API key:
```bash
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
```

Your `.env` should look like:
```
DEEPINFRA_API_KEY=your_api_key_here
DEEPINFRA_BASE_URL=https://api.deepinfra.com/v1/openai
MODEL_NAME=meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
```

### 5. Make sure the PDF is in the project folder
```
API Documentation Partial.pdf
```

### 6. Run the app
```bash
streamlit run app.py
```

---

## How to Use

1. Open your browser at `http://localhost:8501`
2. Click **"Build Knowledge Base"** in the left sidebar — this reads the PDF, chunks it, embeds it locally, and saves it to ChromaDB (takes ~30 seconds on first run)
3. Once you see **"Indexed X chunks"** — start asking questions in the chat box

> You only need to click "Build Knowledge Base" **once**. The index is saved to disk and loaded automatically on every future run.

---

## Ground Truth Test Questions

Run these three questions to verify the bot is working correctly:

| # | Question | Expected Behaviour |
|---|---|---|
| Q1 | *What is the specific request-per-second rate limit for the Upwork API, and is it enforced per Key or per IP?* | Hallucination guard fires — answer not in partial docs |
| Q2 | *How long is an OAuth access token valid for?* | **24 hours** (86400 seconds) |
| Q3 | *Can I use a Client Credentials Grant to access a user's private contract details?* | **No** — Client Credentials is enterprise-only and server-to-server only |

---

## RAG Pipeline Overview

```
PDF File
   │
   ▼
load_pdf()          → Extracts text, prints sanity check (char count + sample)
   │
   ▼
chunk_text()        → 500-char chunks, 50-char overlap (RecursiveCharacterTextSplitter)
   │
   ▼
build_vector_store() → Local embeddings (all-MiniLM-L6-v2) → stored in ChromaDB
   │
   ▼  [at query time]
retrieve_chunks()   → Embeds query → cosine similarity → top 3 chunks returned
   │
   ▼
generate_answer()   → System prompt + chunks + question → DeepInfra LLM → answer + latency
```

---

## Key Design Decisions

**Why local embeddings?**
The assignment prohibits uploading source documentation to any public LLM. Using `sentence-transformers/all-MiniLM-L6-v2` means all embedding happens on your machine — the Upwork docs never leave your system.

**Why 500 chars / 50 overlap?**
API docs contain multi-line code blocks. A 50-char overlap ensures code snippets that fall on chunk boundaries still appear complete in at least one chunk.

**Why temperature 0.1?**
Low temperature makes the LLM more deterministic and factual — essential for a technical support bot where made-up values (wrong token TTLs, fake endpoints) cause real damage.

**Why top-3 retrieval?**
Enough context for the LLM to answer accurately, while keeping the prompt short and API latency low.

---

## Important Notes

- **Never commit your `.env` file** — it contains your API key
- The `chroma_db/` folder is auto-generated and can be safely deleted to rebuild from scratch
- First run downloads the embedding model (~80 MB) — subsequent runs are instant

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

*Built for the ProAnalyst AI Team — Associate AI Developer Assignment, June 2026*