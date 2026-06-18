# Synapse AI Development Guidelines

## Overview

This document defines the development guidelines for AI agents and human contributors working on Synapse AI.

The guidelines ensure consistency, maintainability, and alignment with the project's research-oriented objectives.

---

## Documentation-Driven Development

The `docs/` directory is the authoritative source of truth for this project.

Before making any implementation change, consult the following documents in order of relevance:

| Document | Purpose |
| -------- | ------- |
| `product_requirements.md` | Project goals, scope, and success metrics |
| `architecture.md` | System layers and data flow |
| `agent_design.md` | Role-based agent architecture |
| `api_specification.md` | Endpoint contracts and request/response formats |
| `database_schema.md` | Entity relationships and column definitions |
| `evaluation_framework.md` | Metrics and evaluation methodology |
| `tech_stack.md` | Technology choices and rationale |
| `system_design_decisions.md` | ADRs and architectural rationale |
| `roadmap.md` | Phased delivery plan |
| `research_hypotheses.md` | Measurable research questions |
| `experiments.md` | Experiment definitions and methodology |
| `decision_log.md` | Ongoing decision tracking |

If documentation conflicts with existing implementation, treat the documentation as authoritative and flag the inconsistency.

---

## Architecture Principles

### Clean Layer Separation

Maintain strict separation between:

- **API Layer** — Route handlers, request validation, response serialization
- **Service Layer** — Business logic and orchestration
- **Repository Layer** — Data access and persistence
- **Provider Layer** — External service abstractions (LLMs, etc.)
- **Core Layer** — Configuration, dependencies, shared utilities

### Model Independence

The system must not be coupled to any specific LLM vendor.

All model interactions go through the provider abstraction layer.

New providers should be pluggable without changing business logic.

### Reproducibility

Every debate stage must be persisted for future analysis.

Database operations should preserve complete history.

### Observability

All operations should be logged and traceable.

Use structured logging with consistent severity levels.

---

## Coding Standards

### Python

- Use Python 3.11+
- Use type hints throughout
- Follow PEP 8 conventions
- Use `async`/`await` for I/O-bound operations
- Use Pydantic for all data validation
- Use SQLAlchemy 2.x ORM style (declarative)

### Project Structure

```
backend/
├── app/
│   ├── api/           # Route handlers
│   ├── core/          # Configuration, dependencies
│   ├── database/      # Session, models
│   ├── repositories/  # Data access layer
│   ├── schemas/       # Pydantic models
│   ├── services/      # Business logic
│   └── providers/     # LLM abstractions
├── tests/
├── alembic/           # Migrations
└── Dockerfile
```

### Imports Order

1. Standard library
2. Third-party packages
3. Local application modules

### Naming Conventions

- **Classes**: PascalCase (`DebateService`, `BaseProvider`)
- **Functions/Methods**: snake_case (`create_debate`, `get_debate`)
- **Variables**: snake_case (`debate_id`, `question_text`)
- **Modules**: snake_case (`debate_service.py`, `base_provider.py`)
- **Database tables**: snake_case, plural (`debates`, `debate_rounds`)
- **API routes**: lowercase with hyphens (`/api/v1/debates/{debate_id}`)

---

## Database Guidelines

- Use UUID primary keys
- Use `created_at` and `updated_at` timestamps where appropriate
- Define foreign keys with explicit constraints
- Index foreign key columns and frequently queried fields
- Use Alembic for all schema migrations
- Never modify existing migrations — create new ones

---

## API Guidelines

- Version all APIs under `/api/v{n}`
- Use JSON for all request/response payloads
- Return standard error format:
  ```json
  {
    "error": {
      "code": "ERROR_CODE",
      "message": "Human-readable description."
    }
  }
  ```
- Use appropriate HTTP status codes
- Validate all inputs with Pydantic

---

## Testing Guidelines

- Write tests for all API endpoints
- Write tests for service layer business logic
- Write tests for provider abstraction layer
- Use pytest as the test framework
- Use pytest fixtures for test dependencies
- Mock external services in tests
- Aim for meaningful coverage of core business logic

---

## Decision Recording

All significant engineering, architectural, and product decisions must be recorded in `docs/decision_log.md`.

Each entry must include:
- Date
- Decision
- Context
- Reasoning
- Impact

---

## Workflow

1. Review relevant documentation
2. Check for inconsistencies between docs and code
3. Implement changes aligned with documentation
4. Update documentation if implementation changes requirements
5. Write tests for new functionality
6. Record significant decisions in decision log
7. Verify consistency between code and documentation
