# AgentOps | Autonomous Multi-Agent Orchestration Studio

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0-blue?style=flat-square)](https://langchain-ai.github.io/langgraph/)
[![Docker](https://img.shields.io/badge/Docker-Ephemeral_Sandbox-2496ED?style=flat-square&logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Persistence-4169E1?style=flat-square&logo=postgresql)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit)](https://streamlit.io/)
[![CI/CD](https://img.shields.io/badge/GitHub_Actions-CI-2088FF?style=flat-square&logo=github-actions)](https://github.com/features/actions)

**AgentOps** is an enterprise-grade autonomous multi-agent task orchestrator built with **LangGraph**, **FastAPI**, **Docker**, and **Streamlit**. It plans code modifications, generates executable Python solutions, verifies code inside isolated ephemeral Docker containers, and uses native state checkpointing with Human-in-the-Loop (HITL) approval gates before final deployment.

---

## 🏗️ Architecture & Workflow

```mermaid
graph TD
    User([Client / Streamlit Dashboard]) -->|1. Submit Task Prompt| API[FastAPI Backend Server]
    API -->|2. Initialize Thread State| Postgres[(PostgreSQL Checkpointer)]
    
    subgraph LangGraph State Machine
        Analyst[Analyst Agent Node] -->|Generate Plan| Developer[Developer Agent Node]
        Developer -->|Generate Fix Code| Sandbox[Docker Sandbox Node]
        Sandbox -->|Execute Isolated Container| InterruptGate[Human Review Gate]
    end

    API -->|3. Dispatch Workflow| Analyst
    Sandbox -->|4. Launch Container| EphemeralDocker[Ephemeral Docker Container]
    EphemeralDocker -->|Stream stdout/stderr| Sandbox
    InterruptGate -->|5. Pause Graph & Fire SSE Event| Stream[Server-Sent Events Stream]
    
    User -->|6. Approval Signal| ApproveEndpoint[POST /api/v1/tasks/{thread_id}/approve]
    ApproveEndpoint -->|7. Command resume| InterruptGate
    InterruptGate -->|Approved| END([Workflow Complete])
    InterruptGate -->|Rejected| ABORT([Workflow Aborted])
```

---

## ✨ Key Features

- **Multi-Agent Collaborative Topology**: Separates high-level requirement analysis (Analyst Agent) from code generation (Developer Agent) and isolated runtime testing (Sandbox Node).
- **Ephemeral Docker Sandbox**: Executes LLM-generated code inside resource-constrained, isolated Docker containers (`python:3.11-slim`) to prevent host environment pollution.
- **Stateful Human-in-the-Loop (HITL) Gate**: Integrates native LangGraph `interrupt()` calls backed by PostgreSQL checkpointing to pause execution mid-workflow and await human verification (`Approve` or `Reject`).
- **Real-Time SSE Event Streaming**: Pushes live state transitions and container output logs to connected clients via Server-Sent Events without polling.
- **Enterprise Web Control Center**: Clean Streamlit dashboard for real-time task dispatching, system health monitoring, code diff inspection, and review approvals.

---

## 📁 Repository Structure

```
AgentOps/
├── app/
│   ├── agents/            # LangGraph State Machine & Agent Nodes
│   │   ├── graph.py       # Compiled Graph Topology & Routing Logic
│   │   └── nodes.py       # Analyst, Developer, Sandbox & HITL Nodes
│   ├── api/               # FastAPI Application Layer
│   │   ├── routes.py      # Endpoints, SSE generators & Serializers
│   │   └── schemas.py     # Pydantic Request/Response DTO Models
│   ├── core/              # Global Settings & Pydantic Configuration
│   ├── db/                # PostgreSQL Connection & Async Checkpointer
│   ├── services/          # OpenRouter LLM & Docker Sandbox Execution Services
│   └── main.py            # FastAPI Application Instance & Lifespan
├── .github/
│   └── workflows/
│       └── ci.yml         # GitHub Actions CI Workflow Matrix
├── Dockerfile             # Multi-stage Docker Build (Builder -> Runner)
├── docker-compose.yml     # Multi-container Production Orchestration
├── requirements.txt       # Project Dependencies
├── streamlit_app.py       # Enterprise Web Control Dashboard
└── test_phase1.py .. 5.py # Automated Validation Test Suite
```

---

## ⚙️ Prerequisites & Environment Configuration

### Prerequisites
- **Python 3.11+**
- **Docker & Docker Compose**
- **PostgreSQL 16+**
- **OpenRouter API Key** (for LLM model inference)

### Environment Setup (`.env`)
Create a `.env` file in the root directory:

```env
PROJECT_NAME="AgentOps Orchestrator"
POSTGRES_URI="postgresql://postgres:postgrespassword@localhost:5433/agentops_db?sslmode=disable"
OPENROUTER_API_KEY="sk-or-v1-your-openrouter-api-key"
```

---

## 🚀 Quick Start Guide

### Option 1: Multi-Service Container Stack (Recommended)
Launch the entire stack (PostgreSQL, FastAPI Backend, and Streamlit Web UI):

```bash
docker-compose up --build -d
```

- **FastAPI OpenAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Streamlit Web Control Center**: [http://localhost:8501](http://localhost:8501)
- **PostgreSQL Checkpointer Database**: `localhost:5433`

### Option 2: Local Python Virtual Environment Setup

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Start PostgreSQL Checkpointer Service**:
   ```bash
   docker-compose up agentops_postgres -d
   ```

3. **Launch FastAPI Backend**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

4. **Launch Streamlit Control Dashboard** (in another terminal):
   ```bash
   streamlit run streamlit_app.py --server.port 8501
   ```

---

## 📡 REST API Reference

### 1. Health Check
`GET /health`
```json
{
  "status": "healthy",
  "service": "AgentOps API"
}
```

### 2. Submit Coding Task
`POST /api/v1/tasks/submit`
**Request Body**:
```json
{
  "task_description": "Write a python function is_palindrome(s) that checks if a string is a palindrome.",
  "code_context": "# Optional existing context"
}
```
**Response**:
```json
{
  "task_id": "task-926f8b2e",
  "thread_id": "thread-e6387f21",
  "message": "Task initialized successfully. Connect to /stream endpoint to execute."
}
```

### 3. Real-Time SSE Stream
`GET /api/v1/tasks/{thread_id}/stream`  
Serves a Server-Sent Events (`text/event-stream`) stream pushing node progress:
- `event: node_update` — Fired when a node (`analyst`, `developer`, `sandbox`) completes.
- `event: human_approval_required` — Fired when execution suspends at the approval gate.
- `event: complete` — Fired when the task reaches completion.

### 4. Submit Human Approval Decision
`POST /api/v1/tasks/{thread_id}/approve`  
**Request Body**:
```json
{
  "approved": true
}
```
**Response**:
```json
{
  "status": "RESUMED",
  "message": "Graph resumed with approval state: True"
}
```

---

## 🧪 Running Validation Tests

Execute the phase-by-phase automated verification test suite:

```bash
# Test 1: Checkpointer & Postgres State Database Connection
python3 test_phase1.py

# Test 2: Analyst & Developer LLM Agent Graph Topology
python3 test_phase2.py

# Test 3: Ephemeral Docker Sandbox Container Execution
python3 test_phase3.py

# Test 4: LangGraph Native Interrupt & Human Resume Gate
python3 test_phase4.py

# Test 5: End-to-End FastAPI REST & SSE Streaming Suite
python3 test_phase5.py
```

---

## 🛠️ CI/CD Pipeline

Automated integration checks run on every push to `main` via GitHub Actions (`.github/workflows/ci.yml`):
1. Provisions a live PostgreSQL 16 service container.
2. Installs Python dependencies and verifies checkpointer persistence logic.
3. Builds and tags the multi-stage Docker image to ensure deployment readiness.

---

## 📄 License
Distributed under the MIT License.
