# MyWikiRAG 🔍🧠

A Retrieval-Augmented Generation (RAG) pipeline built on top of Wikipedia. This project fetches and parses Wikipedia articles, builds a FAISS vector index from their content, and enables semantic question answering powered by LLMs via Groq — all from the command line.

---

## 📁 Project Structure

```
MyWikiRAG/
├── wiki.py                  # Wikipedia API wrapper (search, fetch, summarize)
├── wiki_parser.py           # Parses & chunks raw Wikipedia content into docs
├── rag_corpus_builder.py    # Builds & deduplicates the full RAG corpus → saves to JSON
├── rag_pipeline_nlp.py      # Embeds corpus, builds FAISS index, runs interactive Q&A
├── main.py                  # Demo script to test Wikipedia API functions
├── rag_corpus_nlp.json      # Pre-built corpus of Wikipedia article chunks
├── faiss_wikipedia_index/   # Saved FAISS vector index (auto-generated)
└── requirements.txt         # All Python dependencies
```

---

## ⚙️ Requirements

- **Python 3.9+**
- A **[Groq API key](https://console.groq.com/)** for LLM-powered answers

### Install dependencies

```bash
pip install -r requirements.txt
```

> ⚠️ Always activate your virtual environment before installing or running anything.

---

## 🛠️ Virtual Environment Setup

```bash
# Create the venv
python -m venv venv

# Activate — Windows (PowerShell)
venv\Scripts\activate

# Activate — Linux / macOS
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

> 📌 **Never move the `venv/` folder** after creating it. It uses absolute paths and will break if relocated. If you move the project, delete `venv/` and recreate it.

---

## 🔑 API Key Setup

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Or export it directly in your terminal:

```bash
# Windows (PowerShell)
$env:GROQ_API_KEY = "your_api_key_here"

# Windows (Command Prompt)
set GROQ_API_KEY=your_api_key_here

# Linux / macOS
export GROQ_API_KEY=your_api_key_here
```

---

## 🚀 Order of Execution

Run the files in this exact order:

---

### Step 1 — `wiki.py` *(no direct run needed)*

The Wikipedia API wrapper. Used as a module by other scripts. Provides:

| Function | Description |
|---|---|
| `search_articles(query)` | Search Wikipedia by keyword |
| `get_article_summary(title)` | Fetch a short article summary |
| `get_article_content(title)` | Fetch full or intro-only article text |
| `get_article_section(title)` | Fetch section headers of an article |
| `get_todays_featured_article()` | Fetch today's Wikipedia featured article |
| `get_random_article()` | Fetch a random article summary |

---

### Step 2 — `wiki_parser.py` *(no direct run needed)*

Parses and cleans raw Wikipedia API responses into structured document chunks. Used as a module by `rag_corpus_builder.py`.

---

### Step 3 — `main.py` *(optional — for testing)*

A demo script to verify that the Wikipedia API wrapper is working correctly.

```bash
python main.py
```

Prints search results, summaries, random articles, and section headers to the console.

---

### Step 4 — `rag_corpus_builder.py`

Loops through a predefined list of AI/ML topics, fetches Wikipedia content for each, deduplicates the chunks, and saves everything to `rag_corpus_nlp.json`.

```bash
python rag_corpus_builder.py
```

**What it does:**
- Fetches search results, article content, summaries, and sections for 20+ topics
- Deduplicates documents (removes chunks under 50 characters or seen before)
- Appends today's featured article
- Saves the final corpus to `rag_corpus_nlp.json`

> ⏭️ Skip this step if `rag_corpus_nlp.json` already exists in the repo — it's pre-built.

---

### Step 5 — `rag_pipeline_nlp.py` *(main entry point)*

The full end-to-end RAG pipeline. Loads the corpus, builds or loads the FAISS vector index, and starts an interactive Q&A assistant.

```bash
python rag_pipeline_nlp.py
```

**What it does:**
- Loads `rag_corpus_nlp.json` and converts it to LangChain `Document` objects
- Embeds documents using `sentence-transformers/all-MiniLM-L6-v2`
- Builds a FAISS index on first run (or loads from `faiss_wikipedia_index/` if it exists)
- Runs a RetrievalQA chain using Groq's LLM
- Starts an interactive terminal loop — ask any AI/ML question

**Example session:**

```
AI/ML knowledge Assistant - type 'exit' to quit

 Your question: What is a Transformer model?

 Answer: A Transformer is a deep learning architecture based on self-attention...

📚 Context Sources:
  [1] Transformer Models | wikipedia_summary
  [2] Large Language Model | wikipedia_content
```

---

## 📦 Key Dependencies

| Package | Purpose |
|---|---|
| `requests` | Wikipedia REST API calls |
| `sentence-transformers` | Text embeddings (`all-MiniLM-L6-v2`) |
| `faiss-cpu` | Vector similarity search & indexing |
| `langchain` | RAG chain orchestration |
| `langchain-groq` | Groq LLM integration |
| `langchain-huggingface` | HuggingFace embeddings in LangChain |
| `langchain-community` | FAISS vector store integration |
| `groq` | Groq API client |
| `torch` + `transformers` | Underlying model support |
| `nltk` | Text preprocessing |
| `python-dotenv` | Load API keys from `.env` file |

---

## 💡 Notes

- **First run** of `rag_pipeline_nlp.py` will embed all documents and build the FAISS index — this may take a few minutes depending on your hardware.
- **Subsequent runs** will skip embedding and load directly from `faiss_wikipedia_index/`, making startup much faster.
- The pre-built `rag_corpus_nlp.json` and `faiss_wikipedia_index/` are included in the repo, so you can **jump straight to Step 5** for a quick test.
- The assistant is specialized in **AI and ML topics** based on the corpus topics defined in `rag_corpus_builder.py`. Add more topics to that list to expand its knowledge.

---

## 📄 License

This project is open source. Feel free to fork and build on it.
