import streamlit as st
import os
from rag_pipeline import (
    load_pdf, chunk_text, build_vector_store,
    load_vector_store, retrieve_chunks, generate_answer
)

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Upwork API Support Bot",
    page_icon="🤖",
    layout="centered"
)

st.title("Upwork API — Technical Support Bot")
st.caption("Powered by RAG | LLM: Meta-Llama-3.1-8B | Docs: Upwork API Reference")

# ── Sidebar: load & index docs ────────────────────────────────────
with st.sidebar:
    st.header("Setup")
    pdf_path = st.text_input("PDF path", value="API Documentation Partial.pdf")
    build_btn = st.button("Build Knowledge Base")

    if build_btn:
        with st.spinner("Loading and indexing documentation..."):
            text = load_pdf(pdf_path)
            chunks = chunk_text(text)
            build_vector_store(chunks)
        st.success(f"Done! Indexed {len(chunks)} chunks.")

# ── Load vector store into session ───────────────────────────────
if "vectorstore" not in st.session_state:
    if os.path.exists("./chroma_db"):
        st.session_state.vectorstore = load_vector_store()
    else:
        st.warning("Click 'Build Knowledge Base' in the sidebar first.")
        st.stop()

# ── Chat history ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ── User input ────────────────────────────────────────────────────
query = st.chat_input("Ask a question about the Upwork API...")

if query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    # Retrieve + Generate
    with st.chat_message("assistant"):
        with st.spinner("Searching documentation..."):
            chunks = retrieve_chunks(query, st.session_state.vectorstore)
            answer, latency = generate_answer(query, chunks)

        # 1. Show the answer
        st.write(answer)

        # 2. Show latency
        st.metric("Response time", f"{latency}s")

        # 3. Show sources
        with st.expander("Sources used"):
            for i, chunk in enumerate(chunks, 1):
                st.markdown(f"**Chunk {i}:**")
                st.code(chunk.page_content, language=None)

    st.session_state.messages.append({"role": "assistant", "content": answer})
