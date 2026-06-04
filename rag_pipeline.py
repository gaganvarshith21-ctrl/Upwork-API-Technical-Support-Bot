import os
import time
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()   # reads .env file automatically

# ── A1. Load the PDF ──────────────────────────────────────────────
def load_pdf(pdf_path: str) -> str:
    """Extract all text from the PDF and run a sanity check."""
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    # Sanity check — required by the assignment
    print(f"[Sanity Check] Total characters: {len(full_text)}")
    print(f"[Sanity Check] Sample text:\n{full_text[:300]}\n")

    return full_text

   # ── A2. Chunking ─────────────────────────────────────────────────
def chunk_text(text: str):
    """
    Split text into 500-char chunks with 50-char overlap.
    Overlap ensures that sentences/code split at a boundary
    still appear fully in at least one chunk.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,         # max chars per chunk
        chunk_overlap=50,       # chars shared between consecutive chunks
        separators=["\n\n", "\n", " ", ""]  # try to split at paragraph first
    )
    chunks = splitter.create_documents([text])
    print(f"[Chunking] Created {len(chunks)} chunks")
    return chunks

# ── A3. Embed and store in ChromaDB ──────────────────────────────
def build_vector_store(chunks, persist_dir="./chroma_db"):
    """
    Convert text chunks to embeddings and store in ChromaDB.
    Uses a local sentence-transformer model — no API calls for embedding.
    """
    # Load a local embedding model (downloads once, ~80MB)
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # Create ChromaDB vector store from chunks
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=persist_dir   # saves to disk so you don't re-embed every run
    )

    print(f"[VectorStore] Stored {vectorstore._collection.count()} vectors in ChromaDB")
    return vectorstore


def load_vector_store(persist_dir="./chroma_db"):
    """Load an existing ChromaDB store (skip re-embedding)."""
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding_model
    )

    # ── B1. Semantic Retrieval ────────────────────────────────────────
def retrieve_chunks(query: str, vectorstore, k: int = 3):
    """
    Embed the user's query and find top-k similar chunks.
    Uses cosine similarity under the hood.
    """
    results = vectorstore.similarity_search(query, k=k)
    return results   # list of Document objects with .page_content

    # ── B2. LLM Call with RAG prompt ─────────────────────────────────
def generate_answer(query: str, chunks: list) -> tuple[str, float]:
    """
    Send retrieved chunks + user question to LLM.
    Returns (answer_text, latency_seconds).
    """
    # Build context from retrieved chunks
    context = "\n\n---\n\n".join([doc.page_content for doc in chunks])

    # System prompt — forces the AI to stay in character and not hallucinate
    system_prompt = """You are a Senior Upwork API Consultant with 10 years of experience.
Your job is to answer developer questions about the Upwork API accurately.

STRICT RULES:
1. Answer ONLY using the documentation context provided below.
2. If the answer is not in the context, respond EXACTLY with:
   "I'm sorry, but the provided documentation does not contain that information."
3. Do NOT make up API endpoints, token values, or rate limits.
4. Be precise and technical. Quote exact values when they appear in the docs."""

    # User message with context injected
    user_message = f"""Context from Upwork API documentation:
{context}

Developer Question: {query}"""

    # Connect to DeepInfra using OpenAI-compatible client
    client = OpenAI(
        api_key=os.getenv("DEEPINFRA_API_KEY"),
        base_url=os.getenv("DEEPINFRA_BASE_URL")
    )

    start_time = time.time()

    response = client.chat.completions.create(
        model=os.getenv("MODEL_NAME"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_message}
        ],
        max_tokens=600,
        temperature=0.1    # low = more precise/factual, good for docs Q&A
    )

    latency = round(time.time() - start_time, 2)
    answer = response.choices[0].message.content

    return answer, latency