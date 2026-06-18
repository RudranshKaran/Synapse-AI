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
    │
    ▼
Opinion Generation
    │
    ▼
Cross Critique
    │
    ▼
Opinion Revision
    │
    ▼
Consensus Formation
    │
    ▼
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

## Architecture

```text
┌──────────────────────┐
│       User UI        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Debate Orchestrator  │
└──────────┬───────────┘
           │
 ┌─────────┼─────────┐
 ▼         ▼         ▼
Model-A      Model-B    Model-C
 │         │         │
 └────┬────┴────┬────┘
      ▼         ▼
┌──────────────────────┐
│  Consensus Engine    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Evaluation Engine    │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Analytics Dashboard  │
└──────────────────────┘
```

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* Pydantic

### Database

* PostgreSQL

### Agent Orchestration

* LangGraph

### AI Models

* Generic LLM Provider
* Generic LLM Provider
* Generic LLM Provider

### Evaluation

* Sentence Transformers
* NumPy
* Pandas

### Frontend

* Next.js
* TypeScript
* Tailwind CSS

### Infrastructure

* Docker
* Docker Compose

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

## Project Structure

```text
synapse/

├── backend/
│   ├── api/
│   ├── agents/
│   ├── orchestrator/
│   ├── services/
│   ├── models/
│   └── core/
│
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── services/
│   └── charts/
│
├── docs/
│
├── experiments/
│
└── README.md
```

---

## Current Status

### Phase

MVP Development

### Completed

* Product Requirements
* System Architecture
* Agent Design
* Evaluation Framework
* Database Design
* API Specification

### In Progress

* Debate Orchestration Engine
* Consensus Engine
* Evaluation Layer

---

## Roadmap

### MVP

* Multi-model debates
* Consensus generation
* Agreement scoring
* Analytics dashboard

### Future

* Evidence agents
* Judge agents
* Large-scale experimentation
* Domain-specific expert agents
* Behavioral profiling

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
