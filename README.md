<div align="center">
  <h1>AI-Based Interview Preparation Platform</h1>
  <p><strong>Master DSA interviews with AI-powered coding practice, real-time feedback, and intelligent hints.</strong></p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi" alt="FastAPI"/>
    <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=flat&logo=mongodb" alt="MongoDB"/>
    <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat&logo=chroma" alt="ChromaDB"/>
    <img src="https://img.shields.io/badge/Anthropic-412991?style=flat&logo=anthropic" alt="Anthropic"/>
    <img src="https://img.shields.io/badge/Sentence_Transformers-FFD43B?style=flat&logo=python" alt="Sentence Transformers"/>
    <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit" alt="Streamlit"/>
  </p>
</div>

---

## Overview

An end-to-end platform that leverages **Retrieval-Augmented Generation (RAG)** and **Anthropic Claude** to help candidates prepare for Data Structures & Algorithms interviews. Users solve curated DSA questions, receive AI-generated code feedback, request contextual hints, and generate model solutions — all through a clean REST API and an upcoming Streamlit frontend.

## Key Features

| Feature | Description |
|---|---|
| **Question Bank** | 10+ curated DSA questions across arrays, trees, graphs, DP, and more |
| **RAG Retrieval** | Relevant questions & solutions retrieved via ChromaDB + Sentence Transformers |
| **AI Code Feedback** | Submit your solution and receive structured feedback with a rating out of 10 |
| **Contextual Hints** | Get subtle, progressive hints powered by Claude without spoiling the solution |
| **Solution Generator** | Generate well-documented model solutions with time/space complexity analysis |
| **REST API** | Fully documented FastAPI backend with async MongoDB (Motor) for persistence |

## Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI (Python 3.14) |
| **Database** | MongoDB via Motor (async driver) |
| **Vector Store** | ChromaDB (persistent client) |
| **LLM** | Anthropic Claude 3.5 Sonnet |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **Frontend** | Streamlit (coming soon) |

## Architecture

```
User Request
    │
    ▼
FastAPI Router ──► MongoDB (question/feedback lookup)
    │
    ├──► RAG Service ──► ChromaDB (semantic search)
    │                             │
    │                             ▼
    │                    Sentence Transformers (embeddings)
    │
    └──► LLM Service ──► Anthropic Claude API
                                │
                                ▼
                         Hint / Feedback / Solution
```

## Quick Start

### Prerequisites

- Python 3.10+
- MongoDB instance (local or Atlas)
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/interview-prep.git
cd interview-prep

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
source venv/Scripts/activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB_NAME="interview_prep"
```

### Run the Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at **http://localhost:8000**.

Interactive docs at **http://localhost:8000/docs** (Swagger UI).

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `GET` | `/questions/` | List questions (filter by `topic`, `difficulty`) |
| `GET` | `/questions/{id}` | Get a specific question |
| `POST` | `/questions/` | Create a new question |
| `POST` | `/questions/{id}/hint` | Generate an AI hint for a question |
| `POST` | `/questions/{id}/solution` | Generate a model solution |
| `POST` | `/feedback/` | Submit code for AI evaluation |
| `GET` | `/feedback/history/{id}` | Get feedback history for a question |

### Example: Get a hint

```bash
curl -X POST http://localhost:8000/questions/two-sum/hint \
  -H "Content-Type: application/json" \
  -d '{"question_id": "two-sum", "user_code": "def two_sum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]"}' 
```

## Project Structure

```
interview-prep/
├── backend/
│   ├── __init__.py
│   ├── config.py                  # Environment & app configuration
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   └── schemas.py             # Pydantic models & request/response schemas
│   ├── routes/
│   │   ├── questions.py           # Question CRUD + hint/solution endpoints
│   │   └── feedback.py            # Code feedback submission & history
│   └── services/
│       ├── db_service.py          # Async MongoDB client (Motor)
│       ├── llm_service.py         # Anthropic Claude wrapper
│       └── rag_service.py         # ChromaDB + Sentence Transformers
├── data/
│   └── question_bank.json         # 10 curated DSA questions
├── frontend/                      # Streamlit app (coming soon)
├── venv/                          # Virtual environment
└── README.md
```

## Roadmap

- [x] REST API with FastAPI
- [x] RAG-based semantic question retrieval (ChromaDB)
- [x] AI-powered hints, feedback, and solutions (Claude)
- [x] MongoDB persistence for questions and feedback
- [ ] Streamlit frontend with code editor (Monaco/CodeMirror)
- [ ] User authentication (JWT)
- [ ] Session history & progress tracking
- [ ] Custom question creation with AI assistance
- [ ] Support for multiple programming languages (Java, C++, JavaScript)
- [ ] Deployment via Docker + docker-compose
