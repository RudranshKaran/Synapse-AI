# Synapse AI

> A Multi-LLM Consensus & Evaluation Platform for studying reasoning convergence, persuasion dynamics, and consensus formation across AI systems.

## Overview

Large Language Models are typically evaluated in isolation.

A model receives a prompt, generates a response, and is judged independently.

However, real-world decision making rarely happens in isolation.

People debate, challenge assumptions, revise opinions, and eventually form consensus.

**Synapse AI explores what happens when AI systems do the same.**

The platform orchestrates structured debates between multiple Large Language Models, tracks how their reasoning evolves over time, and measures behavioral dynamics such as:

* Consensus Formation
* Opinion Drift
* Persuasion
* Confidence Shifts
* Debate Efficiency

Rather than asking:

> "Which model gives the best answer?"

Synapse AI asks:

> "How do intelligent systems influence one another and converge toward shared conclusions?"

---

## The Problem

Current LLM benchmarks focus on:

* Accuracy
* Task Completion
* Benchmark Scores

These evaluations reveal how models perform individually.

They do not answer questions such as:

* How do models influence one another?
* Which models are most persuasive?
* Does debate improve reasoning quality?
* Which domains generate the greatest disagreement?
* How stable is consensus across repeated discussions?

Synapse AI was built to investigate these questions.

---

## Example Debate Flow

A user submits a question:

```text
Should AI-generated code be deployed directly to production?
```

The platform orchestrates:

```text
Question
    |
    v
Opinion Generation
    |
    v
Cross Critique
    |
    v
Opinion Revision
    |
    v
Consensus Formation
    |
    v
Evaluation Metrics
```

Result:

```json
{
  "consensus_score": 84,
  "agreements": [
    "Human review remains important",
    "Automated testing is necessary"
  ],
  "disagreements": [
    "Level of human oversight required"
  ]
}
```

---

## Core Features

### Multi-LLM Debate Engine

Supports debates between multiple language models including:

* Model-A
* Model-B
* Model-C

---

### Consensus Generation

Identifies:

* Shared conclusions
* Remaining disagreements
* Areas of uncertainty

---

### Evaluation Framework

Measures behavioral dynamics such as:

* Agreement Score
* Opinion Drift
* Persuasion Score
* Confidence Shift
* Debate Efficiency

---

### Research Experiments

Run large-scale experiments to analyze:

* Consensus trends
* Domain-specific disagreement
* Model influence patterns
* Debate effectiveness

---

### Analytics Dashboard

Visualize:

* Debate progression
* Influence networks
* Consensus evolution
* Opinion changes

---

## Prerequisites

* **Docker** & **Docker Compose** (recommended for full-stack setup)
* **Python 3.12+** (for local development without Docker)
* **PostgreSQL 16** (for local development without Docker)

---

## Quick Start (Docker)

The fastest way to get running:

```bash
git clone <repository-url>
cd synapse-ai
docker compose up --build
```

This starts:
* **Backend** (FastAPI) at `http://localhost:8000`
* **Database** (PostgreSQL 16) on port `5432`
* **API docs** at `http://localhost:8000/api/v1/docs`

### Run database migrations

```bash
docker compose exec backend alembic upgrade head
```

### Run tests

```bash
docker compose exec backend python -m pytest tests/ -v
```

---

## Local Development (Without Docker)

### 1. Backend setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env     # Windows
cp .env.example .env       # Linux/macOS
```

### 2. Start PostgreSQL

Ensure PostgreSQL 16 is running locally. The default connection string expects:
* Host: `localhost`
* Port: `5432`
* User: `synapse`
* Password: `synapse`
* Database: `synapse`

Create the database if it doesn't exist:

```bash
createdb -U synapse synapse
```

### 3. Run migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start the server

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Verify

```bash
curl http://localhost:8000/api/v1/health
# {"status": "healthy"}
```

---

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

Tests use an in-memory SQLite database -- no PostgreSQL connection required.

---

## API Reference

All endpoints are prefixed with `/api/v1`.

### Health

```http
GET /api/v1/health
```

```json
{"status": "healthy"}
```

### Create Debate

```http
POST /api/v1/debates
Content-Type: application/json

{
  "question": "Should AI-generated code be deployed directly to production?",
  "models": ["model-a", "model-b", "model-c"]
}
```

```json
{
  "debate_id": "a1b2c3d4-...",
  "question": "Should AI-generated code be deployed directly to production?",
  "status": "created",
  "created_at": "2026-06-18T12:00:00Z",
  "completed_at": null
}
```

### Get Debate

```http
GET /api/v1/debates/{debate_id}
```

```json
{
  "debate_id": "a1b2c3d4-...",
  "question": "...",
  "status": "created",
  "created_at": "...",
  "completed_at": null
}
```

Interactive API documentation is available at `/api/v1/docs` when the server is running.

---

## Architecture

```text
+----------------------------+
|         User UI            |
+-------------+--------------+
              |
              v
+----------------------------+
|    Debate Orchestrator     |
+-------------+--------------+
              |
    +---------+---------+
    v         v         v
  Model-A   Model-B   Model-C
    |         |         |
    +----+----+----+---+
         v         v
+----------------------------+
|     Consensus Engine       |
+-------------+--------------+
              v
+----------------------------+
|    Evaluation Engine       |
+-------------+--------------+
              v
+----------------------------+
|  Analytics Dashboard       |
+----------------------------+
```

### Architecture Layers

```
+----------------------------------------+
|           API Layer (routes)           |
+----------------------------------------+
|         Service Layer (logic)          |
+----------------------------------------+
|       Repository Layer (data access)   |
+----------------------------------------+
|    +------------------------------+    |
|    |  Provider Layer (LLM abst.)  |    |
|    +------------------------------+    |
+----------------------------------------+
|       Core Layer (config, deps)        |
+----------------------------------------+
```

Each layer has a single responsibility and can be tested independently. The provider layer is fully decoupled -- new LLM providers can be added by subclassing `BaseModelProvider` and registering without changing business logic.

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy 2.x
* Pydantic v2

### Database

* PostgreSQL 16

### Agent Orchestration

* LangGraph (planned)

### AI Models

* Provider-agnostic abstraction layer
* Mock providers (Model-A, Model-B, Model-C)
* Real providers (OpenAI, Anthropic, Google -- planned)

### Evaluation

* Sentence Transformers (planned)
* NumPy (planned)
* Pandas (planned)

### Frontend

* Next.js (planned)
* TypeScript (planned)
* Tailwind CSS (planned)

### Infrastructure

* Docker
* Docker Compose

---

## Project Structure

```text
synapse-ai/
|
+-- backend/
|   +-- app/
|   |   +-- api/v1/              # Route handlers (health, debates)
|   |   +-- core/                # Config (Pydantic Settings), logging, deps
|   |   +-- database/models/     # SQLAlchemy ORM models (6 MVP entities)
|   |   +-- providers/           # LLM abstraction layer
|   |   |   +-- base.py          # Abstract provider interface
|   |   |   +-- registry.py      # Provider registration
|   |   |   +-- factory.py       # Model to provider instantiation
|   |   |   +-- config.py        # Model configuration
|   |   |   +-- mocks/           # Mock providers (Model-A/B/C)
|   |   +-- repositories/        # Data access layer
|   |   +-- schemas/             # Pydantic v2 request/response models
|   |   +-- services/            # Business logic layer
|   |   +-- main.py              # FastAPI app factory
|   +-- alembic/                 # Database migrations
|   +-- tests/                   # 35+ pytest tests
|   +-- Dockerfile
|   +-- .env.example
|   +-- requirements.txt
|
+-- docker-compose.yml           # Backend + PostgreSQL
|
+-- docs/                        # Project documentation (source of truth)
|   +-- product_requirements.md
|   +-- architecture.md
|   +-- agent_design.md
|   +-- api_specification.md
|   +-- database_schema.md
|   +-- evaluation_framework.md
|   +-- tech_stack.md
|   +-- system_design_decisions.md
|   +-- roadmap.md
|   +-- decision_log.md
|   +-- ai_development_guidelines.md
|   +-- research_hypotheses.md
|   +-- experiments.md
|
+-- frontend/                    # Next.js (coming soon)
|   +-- src/
|
+-- README.md
```

---

## Evaluation Metrics

### Agreement Score

Measures semantic similarity between model conclusions.

---

### Opinion Drift

Measures how much a model changes its position during debate.

---

### Persuasion Score

Measures influence exerted by one model over another.

---

### Confidence Shift

Tracks confidence evolution throughout discussion.

---

### Debate Efficiency

Measures how quickly consensus is achieved.

---

## Research Questions

Synapse AI is designed to explore questions such as:

* Do debates improve answer quality?
* Which models are most persuasive?
* Which domains produce the highest disagreement?
* Are some models more resistant to persuasion?
* How stable is consensus across repeated runs?

---

## Current Status

### Phase

Backend Foundation (Phase 1) -- Complete

### Completed

* FastAPI application with config, logging, dependency injection
* PostgreSQL database models (6 MVP entities)
* Alembic migrations
* Debate management API (create, get)
* Provider abstraction layer with mock providers
* Docker development environment
* 35+ passing tests
* All documentation synchronized

### Next Phases

* **Phase 2:** Multi-model opinion generation and debate orchestration
* **Phase 3:** Consensus engine and evaluation metrics
* **Phase 4:** Analytics dashboard (frontend)
* **Phase 5:** Research mode and large-scale experiments

---

## Roadmap

### Phase 1 -- Backend Foundation (current)

* FastAPI backend with clean architecture
* PostgreSQL database with migrations
* Provider-agnostic LLM abstraction layer
* Mock providers for development
* Docker development environment

### Phase 2 -- Multi-Model Opinion Generation

* Real LLM provider integrations
* Opinion generation workflow
* Response storage

### Phase 3 -- Debate Engine

* Cross-critique
* Opinion revision
* Transcript tracking

### Phase 4 -- Consensus and Evaluation

* Consensus engine
* Agreement scoring
* Evaluation metrics (opinion drift, persuasion, confidence shift)

### Phase 5 -- Analytics Dashboard

* Frontend (Next.js)
* Consensus gauges, influence graphs, debate timelines

### Future

* Evidence agents, judge agents, domain experts
* Large-scale experimentation
* Research publication tools

---

## Documentation

The `docs/` directory is the primary source of truth for this project. Before making changes, consult the relevant documentation files. Key documents:

* `product_requirements.md` -- Project goals, scope, success metrics
* `architecture.md` -- System layers and data flow
* `agent_design.md` -- Role-based agent architecture
* `api_specification.md` -- Endpoint contracts and request/response formats
* `database_schema.md` -- Entity relationships and column definitions
* `evaluation_framework.md` -- Metrics and evaluation methodology
* `tech_stack.md` -- Technology choices and rationale
* `system_design_decisions.md` -- ADRs and architectural rationale
* `roadmap.md` -- Phased delivery plan
* `decision_log.md` -- Ongoing decision tracking
* `ai_development_guidelines.md` -- Development protocols
* `research_hypotheses.md` -- Measurable research questions
* `experiments.md` -- Experiment definitions and methodology

---

## Why Synapse AI?

Most multi-agent projects focus on generating answers.

Synapse AI focuses on understanding how AI systems interact.

The goal is not simply to produce responses.

The goal is to study:

* Reasoning
* Influence
* Consensus
* Collective Intelligence

and better understand how future AI systems may collaborate, disagree, and make decisions together.

---

## License

MIT License
