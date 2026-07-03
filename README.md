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
    <img src="https://img.shields.io/badge/JWT-000000?style=flat&logo=json-web-tokens" alt="JWT"/>
    <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker" alt="Docker"/>
  </p>
</div>

---

## Overview

An end-to-end platform that leverages **Retrieval-Augmented Generation (RAG)** and **Anthropic Claude** to help candidates prepare for Data Structures & Algorithms interviews. Users solve curated DSA questions, receive AI-generated code feedback, request contextual hints, generate model solutions, take mock interviews, and track their progress.

## Key Features

| Feature | Description |
|---|---|
| **Question Bank** | 10+ curated DSA questions across arrays, trees, graphs, DP, and more |
| **RAG Retrieval** | Relevant questions & solutions retrieved via ChromaDB + Sentence Transformers |
| **AI Code Feedback** | Submit your solution and receive structured feedback with a rating out of 10 |
| **Contextual Hints** | Get subtle, progressive hints powered by Claude without spoiling the solution |
| **Solution Generator** | Generate well-documented model solutions with complexity analysis |
| **Multi-Language** | Python, Java, C++, and JavaScript support with code templates |
| **AI Mock Interview** | Timed mock interviews with Claude-powered answer evaluation |
| **AI Question Generation** | Auto-generate DSA questions by topic and difficulty |
| **User Auth (JWT)** | Signup/login with secure token-based authentication |
| **Progress Tracking** | Session history persisted to MongoDB, viewable in dashboards |
| **Two Frontends** | Static Vanilla JS SPA + Streamlit dashboard |
| **Deployment Ready** | Docker Compose, Render config, Netlify config |

## Tech Stack

| Layer | Technology |
|---|---|
| **API Framework** | FastAPI (Python 3.14) |
| **Database** | MongoDB via Motor (async driver) |
| **Vector Store** | ChromaDB (persistent client) |
| **LLM** | Anthropic Claude 3.5 Sonnet |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **Frontend** | Vanilla JS SPA + Streamlit |
| **Auth** | JWT (PyJWT) |
| **Linting** | Ruff |
| **Containerization** | Docker + Docker Compose |

## Architecture

```
User Request
    │
    ▼
FastAPI Router ──► MongoDB (questions, feedback, users, sessions)
    │
    ├──► Auth Service (JWT validation)
    │
    ├──► RAG Service ──► ChromaDB (semantic search)
    │                             │
    │                             ▼
    │                    Sentence Transformers (embeddings)
    │
    └──► LLM Service ──► Anthropic Claude API
                                │
                                ▼
                         Hint / Feedback / Solution / Mock Eval
```

## Quick Start

### Prerequisites

- Python 3.10+
- MongoDB instance (local or Atlas)
- Anthropic API key

### Installation

```bash
# Clone the repository
git clone https://github.com/harshit-seth/AI-Based-Interview-Preparation-Platform-.git
cd AI-Based-Interview-Preparation-Platform-

# Create virtual environment
python -m venv venv

# Activate it (Windows)
source venv/Scripts/activate
# (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB_NAME="interview_prep"
export JWT_SECRET_KEY="your-secret-key"
```

### Run the Server

```bash
uvicorn backend.main:app --reload
```

The API will be available at **http://localhost:8000**.

Interactive docs at **http://localhost:8000/docs** (Swagger UI).

### Seed the Database

```bash
python backend/seed_db.py
```

### Run the Website Frontend

Open `website/index.html` in your browser, or serve it:

```bash
python -m http.server 8080 -d website
```

### Run the Streamlit Frontend

```bash
streamlit run frontend/app.py
```

### Run with Docker

```bash
docker compose up --build -d
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/health` | No | Health check |
| `GET` | `/db-test` | No | MongoDB connection test |
| `POST` | `/auth/signup` | No | Create account |
| `POST` | `/auth/login` | No | Login, returns JWT token |
| `GET` | `/auth/me` | Yes | Get current user profile |
| `GET` | `/questions/` | No | List questions (filter by `topic`, `difficulty`) |
| `GET` | `/questions/{id}` | No | Get a specific question |
| `POST` | `/questions/` | No | Create a new question |
| `POST` | `/questions/{id}/hint` | No | Generate an AI hint |
| `POST` | `/questions/{id}/solution` | No | Generate a model solution |
| `POST` | `/questions/generate` | No | AI-generate questions by topic/difficulty |
| `POST` | `/feedback/` | No | Submit code for AI evaluation |
| `GET` | `/feedback/history/{id}` | No | Get feedback history |
| `POST` | `/feedback/batch-eval` | No | Batch evaluate mock interview answers |
| `GET` | `/history/` | Yes | Get session history for authenticated user |
| `POST` | `/history/` | Yes | Save a practice session |

## Project Structure

```
interview-prep/
├── backend/
│   ├── __init__.py
│   ├── config.py                  # Environment & app configuration
│   ├── code_templates.py          # Multi-language code templates
│   ├── main.py                    # FastAPI app entry point
│   ├── models/
│   │   └── schemas.py             # Pydantic models & request/response schemas
│   ├── routes/
│   │   ├── auth.py                # JWT signup/login/me endpoints
│   │   ├── questions.py           # Question CRUD + hint/solution/generate
│   │   ├── feedback.py            # Code feedback + batch eval
│   │   └── history.py             # Session history (auth-protected)
│   └── services/
│       ├── auth_service.py        # JWT + password hashing utilities
│       ├── db_service.py          # Async MongoDB client (Motor)
│       ├── llm_service.py         # Anthropic Claude wrapper
│       └── rag_service.py         # ChromaDB + Sentence Transformers
├── data/
│   ├── question_bank.json         # 10 curated DSA questions
│   └── chroma_db/                 # ChromaDB persistent storage (gitignored)
├── frontend/
│   └── app.py                     # Streamlit frontend
├── website/
│   ├── index.html                 # Vanilla JS SPA frontend
│   ├── app.js                     # Frontend logic & API integration
│   └── style.css                  # Dark theme styles
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── test_health.py             # Health & questions tests
│   └── test_auth.py               # Auth endpoint tests
├── Dockerfile                     # Backend container
├── Dockerfile.streamlit           # Streamlit container
├── docker-compose.yml             # Full stack (MongoDB + backend + frontend)
├── Makefile                       # Common task runner
├── Procfile                       # Heroku/Render deployment
├── render.yaml                    # Render deployment config
├── netlify.toml                   # Netlify deployment config
├── pyproject.toml                 # Ruff linting config + pytest settings
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
└── README.md
```

## Roadmap

- [x] REST API with FastAPI
- [x] RAG-based semantic question retrieval (ChromaDB)
- [x] AI-powered hints, feedback, and solutions (Claude)
- [x] MongoDB persistence for questions, feedback, users, sessions
- [x] JWT authentication (signup/login/profile)
- [x] Multi-language support (Python, Java, C++, JavaScript)
- [x] AI-assisted question generation
- [x] Mock interview with AI evaluation
- [x] Session history & progress tracking
- [x] Static website frontend (Vanilla JS SPA)
- [x] Streamlit frontend with practice, dashboard, mock interview
- [x] Backend tests (pytest, async)
- [x] Linting with Ruff
- [x] Docker + Docker Compose deployment
- [x] Render + Netlify deployment configs
