# 🔍 MERN Codebase RAG Assistant

A **Retrieval-Augmented Generation (RAG)** tool that lets you chat with your MERN stack codebase using natural language. Point it at any MERN project, ingest the code once, and ask questions like *"How does user authentication work?"* or *"Which routes handle file uploads?"* — it retrieves the relevant code chunks and answers using an LLM.

---

## ✨ Features

- **Semantic code search** — finds relevant functions, routes, and schemas using vector similarity, not keyword matching
- **MERN-aware chunking** — splits JS files into logical blocks (route handlers, Mongoose schemas, React components, middleware, etc.)
- **Conversation memory** — maintains the last 10 turns of chat history for follow-up questions
- **Streaming responses** — answers stream token-by-token for a fast, interactive feel
- **Source attribution** — every answer cites the file and chunk type it drew from
- **Persistent vector store** — embeddings are saved to disk via ChromaDB; no re-indexing on every run

---

## 🏗️ Architecture

```
MERN Codebase (.js files)
        │
        ▼
  CodebaseParser          ← scans & classifies files, splits into semantic blocks
        │
        ▼
  QueryEmbedder           ← encodes chunks with all-MiniLM-L6-v2 (384-dim vectors)
        │
        ▼
  VectorDatabase          ← stores embeddings + metadata in ChromaDB (cosine similarity)
        │
   [ingestion done]
        │
        ▼
  User asks a question
        │
        ▼
  CodeRetriever           ← embeds query, retrieves top-k similar chunks
        │
        ▼
  Generator               ← builds prompt (system + history + context + question)
        │                    streams response from Llama 3.3 70B via Groq
        ▼
  Answer printed to terminal with source citations
```

### Module Breakdown

| File | Responsibility |
|---|---|
| `src/chunker.py` | Scans `.js` files, classifies them (model/route/component/etc.), splits into semantic blocks using regex patterns |
| `src/embedder.py` | Wraps `sentence-transformers` to embed single queries and batches |
| `src/database.py` | Manages ChromaDB collection — inserts documents with embeddings and metadata |
| `src/retriever.py` | Embeds a query and performs cosine similarity search against the stored vectors |
| `src/generator.py` | Builds the RAG prompt and streams LLM responses via the Groq API |
| `src/schemas.py` | `CustomDocument` and `RetrivedChunk` dataclasses used throughout the pipeline |
| `main.py` | Ingestion entry point — parse codebase → embed → store |
| `chat.py` | Interactive chat loop with history, `/clear`, `/help`, `/quit` commands |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/) (free tier available)

### Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/rag-codebase-assistant.git
cd rag-codebase-assistant

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Usage

**Step 1 — Ingest your codebase**

Open `main.py` and set `target_directory` to your MERN project path:

```python
target_directory = r"C:\path\to\your\mern-project"
```

Then run:

```bash
python main.py
```

This scans all `.js` files, splits them into semantic chunks, embeds them, and saves everything to `data/vector_store/`. You only need to do this once (or again when the codebase changes significantly).

**Step 2 — Start chatting**

```bash
python chat.py
```

```
MERN Codebase Assistant — type your question or /help

> How does user authentication work?

Answer:
User authentication is handled in authController.js using the login function ...

Sources:
  [1] controllers/authController.js — route_handler
  [2] middleware/authMiddleware.js — middleware
  [3] models/User.js — schema_def
```

**Chat commands:**

| Command | Description |
|---|---|
| `/clear` | Clear conversation history |
| `/help` | Show available commands |
| `/quit` | Exit the assistant |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Embedding model | `all-MiniLM-L6-v2` via `sentence-transformers` |
| Vector store | ChromaDB (persistent, cosine similarity) |
| LLM | Llama 3.3 70B Versatile via Groq API |
| Language | Python 3.10+ |
| Config | `python-dotenv` |

---

## 📁 Project Structure

```
RAG/
├── src/
│   ├── chunker.py       # Codebase parsing & semantic splitting
│   ├── database.py      # ChromaDB insert logic
│   ├── embedder.py      # Sentence-transformer wrapper
│   ├── generator.py     # Groq LLM + prompt builder
│   ├── retriever.py     # Vector similarity search
│   ├── schemas.py       # Shared dataclasses
│   └── __init__.py
├── data/
│   └── vector_store/    # Persisted ChromaDB embeddings (git-ignored)
├── main.py              # Ingestion script
├── chat.py              # Interactive chat interface
├── requirements.txt
├── .env                 # API keys (git-ignored)
└── README.md
```

---

## 🔮 Potential Improvements

- [ ] Add support for TypeScript (`.ts`, `.tsx`) files
- [ ] Build a web UI (FastAPI + React frontend)
- [ ] Re-index only changed files using file hashing
- [ ] Support additional LLM providers (OpenAI, Anthropic)
- [ ] Add metadata filters in retrieval (e.g., search only in `controllers/`)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
