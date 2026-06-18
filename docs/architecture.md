# Synapse Architecture Document

## Overview

Synapse is a Multi-LLM Consensus and Evaluation Platform designed to orchestrate structured debates between multiple Large Language Models and analyze how consensus emerges through interaction.

The platform consists of five primary layers:

1. User Interaction Layer
2. Debate Orchestration Layer
3. Agent Layer
4. Evaluation Layer
5. Analytics Layer

Together, these layers enable multi-model discussions, consensus generation, and behavioral analysis.

---

# High-Level Architecture

```text
┌─────────────────────────────┐
│          User UI            │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Debate Orchestrator    │
└──────────────┬──────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌───────┐
│ GPT-4 │  │Claude │  │Gemini │
└───┬───┘  └───┬───┘  └───┬───┘
    │           │          │
    └─────┬─────┴────┬─────┘
          ▼          ▼
┌─────────────────────────────┐
│      Consensus Engine       │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Evaluation Engine      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Analytics Dashboard    │
└─────────────────────────────┘
```

---

# Architectural Principles

The architecture is designed around the following principles:

### Model Independence

Models should not be tightly coupled to the orchestration system.

Adding or removing a model should require minimal changes.

---

### Reproducibility

Debates should be reproducible and stored for future analysis.

---

### Observability

Every debate round, response, critique, and metric should be traceable.

---

### Extensibility

New models, evaluation metrics, and debate strategies should be easy to integrate.

---

# Layer 1: User Interaction Layer

## Purpose

Provides the interface through which users initiate debates and review results.

---

## Responsibilities

* Accept user questions.
* Configure participating models.
* Display debate progression.
* Display analytics and consensus reports.

---

## Technology

Frontend:

* Next.js
* TypeScript
* Tailwind CSS

Visualization:

* Recharts
* D3.js

---

# Layer 2: Debate Orchestrator

## Purpose

Acts as the central coordinator of the system.

The orchestrator manages debate flow and ensures each agent receives the correct context.

---

## Responsibilities

### Question Distribution

Sends the user question to all participating models.

---

### Debate Scheduling

Controls:

* Initial opinion generation
* Critique rounds
* Response refinement
* Consensus generation

---

### State Management

Tracks:

* Debate status
* Debate rounds
* Model responses
* Evaluation results

---

## Technology

* FastAPI
* LangGraph

---

# Layer 3: Agent Layer

## Purpose

Represents the participating AI systems.

Each agent corresponds to a specific LLM.

---

## Supported Models (MVP)

### GPT Agent

Provider:

OpenAI

Responsibilities:

* Generate opinion
* Critique peers
* Participate in consensus

---

### Claude Agent

Provider:

Anthropic

Responsibilities:

* Generate opinion
* Critique peers
* Participate in consensus

---

### Gemini Agent

Provider:

Google

Responsibilities:

* Generate opinion
* Critique peers
* Participate in consensus

---

## Future Models

* Llama
* DeepSeek
* Qwen
* Mistral

---

# Debate Lifecycle

## Phase 1: Initial Opinion Generation

Each model receives the same question.

Example:

Question:

"Should autonomous AI agents execute financial trades without human approval?"

Output:

* Position
* Reasoning
* Confidence Score

---

## Phase 2: Cross Critique

Each model reviews responses from peers.

Models identify:

* Weak assumptions
* Missing evidence
* Logical inconsistencies

---

## Phase 3: Opinion Revision

Models may revise their stance after reviewing critiques.

This stage is used to measure opinion drift.

---

## Phase 4: Consensus Formation

Models attempt to identify:

* Shared conclusions
* Remaining disagreements
* Areas of uncertainty

---

# Layer 4: Consensus Engine

## Purpose

Transforms debate outputs into a structured consensus report.

---

## Responsibilities

### Agreement Extraction

Identify statements accepted by multiple models.

---

### Disagreement Extraction

Identify unresolved conflicts.

---

### Consensus Summary

Generate a final synthesized conclusion.

---

## Output Example

```json
{
  "consensus_score": 82,
  "agreements": [
    "...",
    "..."
  ],
  "disagreements": [
    "...",
    "..."
  ],
  "final_conclusion": "..."
}
```

---

# Layer 5: Evaluation Engine

## Purpose

Measure behavioral characteristics of participating models.

---

## Metrics

### Agreement Score

Measures semantic similarity between conclusions.

---

### Opinion Drift

Measures how much a model changed its stance.

---

### Persuasion Score

Measures influence exerted by one model over another.

---

### Confidence Shift

Measures changes in confidence levels.

---

### Debate Efficiency

Measures the number of rounds required to reach consensus.

---

# Analytics Layer

## Purpose

Convert debate results into interpretable visual insights.

---

## Dashboard Components

### Consensus Gauge

Displays overall consensus score.

---

### Debate Timeline

Displays progression across debate rounds.

---

### Influence Graph

Visualizes model-to-model influence.

Example:

Claude → GPT

GPT → Gemini

---

### Opinion Evolution

Tracks how each model's stance changes throughout the debate.

---

# Data Flow

```text
User Question
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
Consensus Generation
      │
      ▼
Evaluation Metrics
      │
      ▼
Analytics Dashboard
```

---

# Storage Architecture

## Debate Records

Stores:

* Questions
* Debate rounds
* Model outputs

---

## Evaluation Results

Stores:

* Agreement scores
* Persuasion scores
* Opinion drift metrics

---

## Experiment Data

Stores:

* Research experiments
* Domain-specific evaluations
* Historical comparisons

---

# MVP Architecture Scope

Version 1 includes:

* Three LLM agents
* Single debate round
* Consensus generation
* Agreement scoring
* Basic dashboard

Version 1 excludes:

* Multi-user support
* Authentication
* Long-running experiments
* Distributed execution
* Fine-tuning pipelines

---

# Future Architecture Extensions

## Research Mode

Batch execution of hundreds of debates.

---

## Judge Agent

Independent evaluation model responsible for scoring debate quality.

---

## Evidence Agent

Retrieves supporting evidence from external knowledge sources.

---

## Planner Agent

Creates debate strategies dynamically based on question type.

---

# Architecture Summary

Synapse is designed as a modular, extensible platform for studying how multiple AI systems interact, challenge assumptions, influence one another, and converge toward shared conclusions. Its architecture separates debate orchestration, model execution, consensus generation, and behavioral evaluation to enable both practical experimentation and future research into multi-agent reasoning systems.
