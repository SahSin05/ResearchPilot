# ResearchPilot AI

> **An AI-powered research paper assistant built with Retrieval-Augmented Generation (RAG), hybrid search, reranking, citations, and LLM-powered paper analysis.**

ResearchPilot AI helps users **upload, understand, search, and interact with research papers** through an evidence-grounded AI system.

Instead of sending an entire paper directly to an LLM, ResearchPilot retrieves the most relevant evidence from the paper first and uses that evidence to generate grounded responses.

---

## 🚀 What It Does

ResearchPilot is designed around two main experiences:

### 📖 Paper Intelligence

Automatically analyzes a research paper and produces a structured explanation covering:

- Research problem
- Key concepts
- Methodology
- Dataset
- Results
- Limitations
- Glossary

The system will be expanded into a more comprehensive **research-paper study guide**.

### 💬 Research Paper Chat

Users can ask questions about an uploaded paper and receive answers based on **retrieved evidence from that specific paper**, with citations pointing back to the source.

---

# 🧠 Core RAG Pipeline

The project implements a multi-stage RAG pipeline:

```text
Research Paper
      ↓
PDF Processing
      ↓
Hierarchical Chunking
      ↓
Embeddings
      ↓
┌─────────────────────────┐
│ Vector Search           │
│        +                │
│ PostgreSQL Full-Text    │
│ Search                  │
└────────────┬────────────┘
             ↓
            RRF
             ↓
         Reranking
             ↓
     Parent Context
        Expansion
             ↓
      Context Selection
             ↓
        Citations
             ↓
       LLM Generation
             ↓
   Evidence-Grounded Answer
```

This architecture allows the system to retrieve relevant evidence instead of relying entirely on the LLM's internal knowledge.

---

# 🔑 Key Concepts Implemented

### Retrieval-Augmented Generation

The LLM receives relevant retrieved evidence before generating an answer.

### Hybrid Search

Combines:

- **Semantic vector search** using embeddings
- **Lexical search** using PostgreSQL Full-Text Search

This provides both semantic understanding and exact keyword matching.

### Reciprocal Rank Fusion (RRF)

Combines the rankings from vector and lexical retrieval into a unified candidate ranking.

### Reranking

Retrieved candidates are reranked based on their relevance to the user's question before being passed to the generation layer.

### Hierarchical Chunking

Documents are divided into chunks while maintaining parent-child relationships, allowing precise retrieval while preserving surrounding context.

### Citation-Aware Generation

Retrieved evidence is converted into citation references such as:

```text
[C1] [C2] [C3]
```

allowing generated answers to be traced back to source sections/pages.

### Structured LLM Output

Paper explanations use structured JSON schemas and Pydantic validation to produce predictable, frontend-friendly responses.

---

# 🏗️ Architecture

```text
                    React Frontend
                          │
                          ▼
                    FastAPI Backend
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
     Documents        Retrieval       Generation
          │               │               │
          ▼               ▼               ▼
     PDF/Chunks       Hybrid Search   Groq / Ollama
          │               │
          ▼               ▼
      Embeddings       RRF + Rerank
          │               │
          └───────┬───────┘
                  ▼
             PostgreSQL
              + pgvector
```

---

# 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Vector Search | pgvector + HNSW |
| Lexical Search | PostgreSQL FTS + GIN |
| Embeddings | Sentence Transformers (`all-mpnet-base-v2`) |
| Generation | Groq / Ollama |
| Validation | Pydantic |
| Testing | Pytest |
| Infrastructure | Docker |

---

# 📂 Project Structure

```text
ResearchPilot-sync/
│
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── embeddings/
│   │   │   ├── retrieval/
│   │   │   └── generation/
│   │   └── database/
│   │
│   └── tests/
│
├── frontend/
│   └── src/
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

# 🧪 Testing

Testing is treated as an important part of the project rather than an afterthought.

The backend includes tests for:

- Document ingestion
- Embedding persistence
- Retrieval APIs
- Paper evidence retrieval
- Explanation generation
- Explanation APIs

The project will also include broader **end-to-end testing** covering:

```text
Upload Paper
     ↓
Process & Index
     ↓
Generate Explanation
     ↓
Ask Question
     ↓
Retrieve Evidence
     ↓
Generate Answer
     ↓
Verify Citations
```

---

# 📊 RAG Evaluation

A major planned part of the project is evaluating the RAG system itself.

Evaluation will cover:

- Retrieval quality
- Recall@K
- Precision@K
- MRR / ranking quality
- Answer correctness
- Groundedness
- Hallucination rate
- Citation accuracy
- Retrieval latency
- End-to-end response latency

The goal is to evaluate **whether the RAG pipeline actually improves answer quality**, rather than only demonstrating that the application works.

---

# ☁️ Deployment & Production

The project is being developed with a production-oriented architecture.

Planned deployment includes:

```text
React Frontend
      ↓
FastAPI Backend
      ↓
PostgreSQL + pgvector
      ↓
Groq LLM
```

Production considerations include:

- Dockerized services
- Environment-based configuration
- Secret management
- Database persistence
- API security
- Logging and monitoring
- CI/CD
- Automated testing
- Performance evaluation

---

# 🔮 Roadmap

### Current

- [x] Full-stack application foundation
- [x] Document ingestion
- [x] Hierarchical chunking
- [x] Embedding pipeline
- [x] Vector search
- [x] PostgreSQL Full-Text Search
- [x] Hybrid retrieval
- [x] RRF
- [x] Reranking
- [x] Parent context expansion
- [x] Citation generation
- [x] Groq integration
- [x] Structured paper explanation
- [x] Backend test coverage

### Next

- [ ] Enhanced Paper Intelligence / Study Guide
- [ ] Full research-paper chatbot
- [ ] Multi-turn conversational context
- [ ] Improved citation/source UI
- [ ] RAG evaluation framework
- [ ] End-to-end evaluation
- [ ] Production deployment
- [ ] CI/CD and monitoring

---

# 🎯 Why This Project?

ResearchPilot is designed to demonstrate practical understanding of modern AI application development beyond simply calling an LLM API.

The project combines:

**RAG + Information Retrieval + Vector Databases + NLP + LLMs + Backend Engineering + Frontend Engineering + Evaluation + Deployment**

The focus is on building a system where AI responses are **retrieved from evidence, traceable to sources, testable, and measurable**.

---

## Project Status

🚧 **Actively under development**

The core RAG infrastructure and structured paper explanation pipeline are operational. The next development phase focuses on completing the research-paper chatbot, improving paper intelligence, and establishing a comprehensive RAG evaluation and deployment workflow.