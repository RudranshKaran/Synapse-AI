# Synapse AI System Design Decisions

## Overview

This document records the major architectural and technology decisions made during the design and development of Synapse AI.

Each decision captures:

* Problem Context
* Alternatives Considered
* Final Decision
* Rationale
* Tradeoffs

The objective is to make architectural choices explicit and explain the reasoning behind them.

---

# ADR-001

## API Framework Selection

### Status

Accepted

---

### Problem

Synapse AI requires a backend framework capable of:

* Handling multiple LLM providers
* Supporting asynchronous operations
* Exposing REST APIs
* Managing debate orchestration workflows

---

### Alternatives Considered

#### Django

Pros

* Mature ecosystem
* Built-in admin panel
* Rich feature set

Cons

* Heavier framework
* More opinionated architecture
* Less suitable for highly async workloads

---

#### Flask

Pros

* Lightweight
* Flexible

Cons

* Requires additional tooling
* Limited built-in validation

---

#### FastAPI

Pros

* High performance
* Native async support
* Automatic OpenAPI documentation
* Strong typing through Pydantic

Cons

* Smaller ecosystem than Django

---

### Decision

Use FastAPI.

---

### Rationale

Synapse AI is API-first and heavily dependent on asynchronous communication with multiple LLM providers.

FastAPI provides excellent support for these requirements while maintaining simplicity and strong developer productivity.

---

# ADR-002

## Database Selection

### Status

Accepted

---

### Problem

Synapse AI requires persistent storage for:

* Debates
* Responses
* Critiques
* Revisions
* Consensus Reports
* Evaluation Metrics

---

### Alternatives Considered

#### MongoDB

Pros

* Flexible schema
* Easy JSON storage

Cons

* Weak relational modeling
* More difficult analytical queries
* Less suitable for highly connected data

---

#### PostgreSQL

Pros

* Strong relational capabilities
* ACID compliance
* Mature ecosystem
* Excellent analytical support

Cons

* More structured schema design

---

### Decision

Use PostgreSQL.

---

### Rationale

The data model contains multiple strongly related entities.

Example:

```text id="xnns6d"
Debate
 ├── Opinions
 ├── Critiques
 ├── Revisions
 ├── Consensus
 └── Metrics
```

This structure is naturally relational.

PostgreSQL provides consistency, query flexibility, and long-term scalability.

---

# ADR-003

## Agent Orchestration Framework

### Status

Accepted

---

### Problem

Synapse AI requires a framework capable of orchestrating:

* Multi-agent workflows
* Stateful execution
* Debate lifecycles
* Conditional routing

---

### Alternatives Considered

#### CrewAI

Pros

* Easy setup
* Rapid prototyping

Cons

* Limited workflow control
* Less visibility into execution paths

---

#### AutoGen

Pros

* Agent communication features
* Multi-agent focus

Cons

* Less explicit workflow management

---

#### Custom Orchestrator

Pros

* Maximum flexibility

Cons

* Significant development effort

---

#### LangGraph

Pros

* Explicit state management
* Graph-based execution
* Conditional branching
* Production-oriented design

Cons

* Higher learning curve

---

### Decision

Use LangGraph.

---

### Rationale

Synapse AI is fundamentally a workflow-driven system.

Debates naturally map to graph-based execution:

```text id="jlwmgm"
Opinion Generation
      ↓
Critique
      ↓
Revision
      ↓
Consensus
      ↓
Evaluation
```

LangGraph provides clear visibility into this workflow while maintaining flexibility.

---

# ADR-004

## Evaluation Methodology

### Status

Accepted

---

### Problem

Synapse AI requires a method for comparing model outputs.

Metrics include:

* Agreement Score
* Opinion Drift
* Consensus Analysis

---

### Alternatives Considered

#### Keyword Matching

Pros

* Simple

Cons

* Ignores meaning
* Highly inaccurate

---

#### LLM-as-a-Judge

Pros

* Flexible
* Rich evaluations

Cons

* Expensive
* Difficult to reproduce
* Subjective

---

#### Embedding Similarity

Pros

* Efficient
* Reproducible
* Captures semantic meaning

Cons

* Imperfect representation

---

### Decision

Use embedding-based similarity.

---

### Rationale

Semantic embeddings provide a balance between accuracy, reproducibility, and computational cost.

---

# ADR-005

## Embedding Framework

### Status

Accepted

---

### Decision

Use Sentence Transformers.

---

### Rationale

Sentence Transformers provide:

* Strong semantic similarity performance
* Open-source models
* Fast inference
* Easy integration

They form the foundation of:

* Agreement Score
* Opinion Drift
* Consensus Analysis

---

# ADR-006

## Debate Storage Strategy

### Status

Accepted

---

### Problem

Debates produce multiple stages of output.

Each stage may be useful for future analysis.

---

### Decision

Store complete debate history.

---

### Rationale

Future research requires access to:

* Initial opinions
* Critiques
* Revisions
* Final consensus

Storing only final outputs would prevent behavioral analysis.

---

# ADR-007

## Frontend Framework

### Status

Accepted

---

### Decision

Use Next.js with TypeScript.

---

### Rationale

Provides:

* Strong React ecosystem
* Type safety
* Scalability
* Modern development workflow

---

# ADR-008

## Background Processing Strategy

### Status

Accepted

---

### Decision

Do not introduce Celery in MVP.

---

### Rationale

Current workloads are relatively small.

Introducing:

* Redis
* Celery
* Worker Infrastructure

would increase complexity without providing immediate value.

---

### Future Consideration

Introduce:

* Redis
* Celery

during large-scale experiment execution.

---

# ADR-009

## Infrastructure Strategy

### Status

Accepted

---

### Decision

Use Docker for development and deployment.

---

### Rationale

Docker provides:

* Consistent environments
* Reproducible builds
* Simplified onboarding

---

# ADR-010

## Research-First Architecture

### Status

Accepted

---

### Decision

Design Synapse AI as an evaluation platform rather than a chatbot.

---

### Rationale

Most multi-agent projects focus on generating answers.

Synapse AI focuses on measuring:

* Consensus
* Persuasion
* Opinion Change
* Influence Dynamics

The objective is to study model behavior rather than simply produce responses.

---

# Summary

The architectural decisions documented here prioritize clarity, reproducibility, extensibility, and research value. Every major technology and design choice has been selected to support Synapse AI's core objective: understanding how AI systems interact, influence one another, and converge toward shared conclusions.
