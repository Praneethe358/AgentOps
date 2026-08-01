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
