# Synapse AI Technology Stack

## Overview

This document defines the technology stack for Synapse AI and explains the rationale behind each technology choice.

The stack prioritizes:

* Simplicity
* Scalability
* Developer Productivity
* AI Workflow Support
* Rapid Experimentation

The goal is to build a research-oriented multi-agent AI platform without introducing unnecessary complexity during the MVP stage.

---

# Technology Stack Overview

| Layer               | Technology                |
| ------------------- | ------------------------- |
| Frontend            | Next.js                   |
| UI Components       | React                     |
| Styling             | Tailwind CSS              |
| Backend             | FastAPI                   |
| API Validation      | Pydantic                  |
| ORM                 | SQLAlchemy                |
| Database            | PostgreSQL                |
| Agent Orchestration | LangGraph                 |
| LLM Providers       | Generic LLM Provider, Generic LLM Provider, Generic LLM Provider |
| Evaluation Engine   | Sentence Transformers     |
| Data Analysis       | Pandas                    |
| Numerical Computing | NumPy                     |
| Containerization    | Docker                    |
| Local Development   | Docker Compose            |
| Version Control     | Git & GitHub              |

---

# Frontend Layer

## Next.js

### Purpose

Frontend application and user interface.

### Why Next.js?

* Production-ready React framework
* Excellent TypeScript support
* Fast development workflow
* Easy deployment
* Supports future scalability

### Responsibilities

* Question submission
* Debate visualization
* Analytics dashboard
* Consensus reports

---

## React

### Purpose

Component-based UI architecture.

### Responsibilities

* Reusable components
* State management
* Interactive dashboards

---

## Tailwind CSS

### Purpose

Styling framework.

### Why Tailwind?

* Rapid UI development
* Consistent design system
* Minimal custom CSS

---

# Backend Layer

## FastAPI

### Purpose

Core API framework.

### Why FastAPI?

* High performance
* Native async support
* Excellent developer experience
* Automatic OpenAPI documentation
* Strong integration with AI workflows

### Responsibilities

* Debate management
* Agent orchestration endpoints
* Evaluation APIs
* Experiment APIs

---

## Pydantic

### Purpose

Data validation and serialization.

### Responsibilities

* Request validation
* Response validation
* Structured schemas

---

## SQLAlchemy

### Purpose

Database abstraction layer.

### Responsibilities

* Database models
* Query generation
* Transaction management

---

# Database Layer

## PostgreSQL

### Purpose

Primary persistent storage.

### Why PostgreSQL?

* Strong relational capabilities
* ACID compliance
* Mature ecosystem
* Excellent support for analytical queries

### Stored Data

* Debates
* Opinions
* Critiques
* Revisions
* Consensus reports
* Evaluation metrics

---

# Agent Orchestration Layer

## LangGraph

### Purpose

Multi-agent workflow orchestration.

### Why LangGraph?

Traditional agent frameworks focus on simple agent communication.

Synapse AI requires:

* Stateful workflows
* Multi-step reasoning
* Branching execution paths
* Debate lifecycle management

LangGraph provides explicit control over agent interactions and workflow execution.

### Responsibilities

* Opinion generation
* Critique routing
* Revision cycles
* Consensus formation

---

# AI Layer

## Generic LLM Provider Models

### Initial Usage

Model-A

### Role

Opinion generation and debate participation.

---

## Generic LLM Provider Models

### Initial Usage

Model-B

### Role

Opinion generation and debate participation.

---

## Generic LLM Provider Models

### Initial Usage

Model-C

### Role

Opinion generation and debate participation.

---

# Evaluation Layer

## Sentence Transformers

### Purpose

Semantic similarity evaluation.

### Why Sentence Transformers?

The evaluation framework relies heavily on comparing meaning rather than exact wording.

### Responsibilities

* Agreement Score
* Opinion Drift
* Semantic Similarity
* Consensus Analysis

### Example Usage

Compare:

Initial Position

vs

Final Position

to calculate opinion drift.

---

## NumPy

### Purpose

Numerical calculations.

### Responsibilities

* Similarity computations
* Statistical calculations
* Metric aggregation

---

## Pandas

### Purpose

Data analysis and experimentation.

### Responsibilities

* Experiment analysis
* Research datasets
* Metric aggregation
* Reporting

---

# Infrastructure Layer

## Docker

### Purpose

Containerization.

### Why Docker?

* Consistent development environment
* Simplified deployment
* Reproducible builds

### Responsibilities

* Backend container
* Frontend container
* Database container

---

## Docker Compose

### Purpose

Local development orchestration.

### Responsibilities

Run the complete development environment using:

```bash
docker-compose up
```

---

# Version Control

## Git

### Purpose

Source control.

---

## GitHub

### Purpose

Repository hosting and collaboration.

### Responsibilities

* Code management
* Documentation
* Issue tracking
* Release management

---

# Excluded Technologies

The following technologies are intentionally excluded from the MVP.

---

## Celery

Reason:

Not required until large-scale experiment execution is introduced.

Potential Future Usage:

* Batch experiments
* Background processing

---

## Redis

Reason:

Current MVP does not require caching or distributed task queues.

Potential Future Usage:

* Celery broker
* Debate state caching
* Rate limiting

---

## Apache Spark

Reason:

Current data volumes do not justify distributed processing.

Potential Future Usage:

* Large-scale experiment analytics

---

## TensorFlow

Reason:

Synapse AI consumes foundation models rather than training them.

Potential Future Usage:

* Custom evaluation models

---

# Future Technology Roadmap

## Phase 2

* Redis
* Celery

Purpose:

Large-scale experiment execution.

---

## Phase 3

* AWS ECS
* AWS RDS
* AWS S3

Purpose:

Production deployment.

---

## Phase 4

* OpenTelemetry
* Prometheus
* Grafana

Purpose:

Observability and monitoring.

---

# Architecture Summary

The Synapse AI technology stack is intentionally designed to balance engineering simplicity with research flexibility. The chosen technologies provide a strong foundation for multi-agent orchestration, debate evaluation, and behavioral analysis while keeping the MVP focused and achievable.
