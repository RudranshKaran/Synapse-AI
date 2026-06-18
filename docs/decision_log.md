# Synapse Decision Log

## Overview

This document records important engineering, product, and research decisions made during the development of Synapse.

Unlike `system_design_decisions.md`, which documents long-term architectural choices, this log captures the evolution of the project over time.

The purpose of this document is to:

* Preserve engineering context
* Record tradeoffs
* Explain changes
* Improve future maintainability

---

# Log Format

Each entry contains:

* Date
* Decision
* Context
* Reasoning
* Impact

---

# 2026-06-18

## Decision

Project name finalized as **Synapse**.

---

### Context

Several names were considered:

* ConvergeAI
* ConsensusAI
* DebateNet
* Agora
* Synapse

---

### Reasoning

The project focuses on how AI systems exchange information, influence one another, and form collective conclusions.

The concept of a synapse closely reflects the transfer of information between intelligent entities.

---

### Impact

Established project identity and repository naming.

---

# 2026-06-18

## Decision

Position Synapse as a research and evaluation platform rather than a debate chatbot.

---

### Context

Initial project discussions focused on multiple LLMs debating a topic.

---

### Reasoning

A debate interface alone does not provide significant research value.

The evaluation layer introduces:

* Agreement analysis
* Opinion drift tracking
* Persuasion measurement
* Consensus analysis

These capabilities differentiate Synapse from typical multi-agent projects.

---

### Impact

Changed overall project direction.

Evaluation became a first-class component.

---

# 2026-06-18

## Decision

Adopt role-based agents instead of model-based agents.

---

### Context

Initial architecture treated:

* GPT
* Claude
* Gemini

as independent agents.

---

### Reasoning

Models are implementations.

Agents are responsibilities.

Separating the two improves flexibility and system design.

---

### Impact

Introduced:

* Opinion Agent
* Critique Agent
* Defense Agent
* Revision Agent
* Consensus Agent
* Evaluation Agent

---

# 2026-06-18

## Decision

Use LangGraph for orchestration.

---

### Context

Several orchestration approaches were evaluated.

---

### Alternatives Considered

* CrewAI
* AutoGen
* Custom Orchestrator

---

### Reasoning

Debates naturally form a stateful workflow.

LangGraph provides:

* State management
* Explicit execution flow
* Conditional branching

---

### Impact

Established orchestration layer.

---

# 2026-06-18

## Decision

Use PostgreSQL as the primary database.

---

### Context

Evaluated relational and document-based databases.

---

### Alternatives Considered

* PostgreSQL
* MongoDB

---

### Reasoning

Debates, responses, consensus reports, and metrics are strongly related entities.

Relational modeling better represents these relationships.

---

### Impact

Database schema designed around PostgreSQL.

---

# 2026-06-18

## Decision

Use embedding-based similarity for evaluation.

---

### Context

The system requires methods for comparing responses and measuring agreement.

---

### Alternatives Considered

* Keyword matching
* LLM-as-a-Judge
* Embedding similarity

---

### Reasoning

Embedding similarity provides:

* Semantic understanding
* Reproducibility
* Lower cost

while avoiding the variability of LLM-based evaluation.

---

### Impact

Evaluation framework built around semantic similarity metrics.

---

# 2026-06-18

## Decision

Exclude Celery and Redis from the MVP.

---

### Context

Early discussions considered introducing distributed task processing.

---

### Reasoning

The MVP workload is relatively small.

Additional infrastructure would increase complexity without providing immediate value.

---

### Future Revisit Trigger

* Large-scale experiments
* Batch processing
* Long-running workflows

---

### Impact

Simplified initial architecture.

---

# 2026-06-18

## Decision

Use Sentence Transformers for semantic evaluation.

---

### Context

Evaluation metrics require semantic similarity calculations.

---

### Reasoning

Sentence Transformers provide:

* Strong embedding quality
* Fast inference
* Open-source deployment

---

### Impact

Forms the foundation of:

* Agreement Score
* Opinion Drift
* Consensus Analysis

---

# 2026-06-18

## Decision

Store complete debate history.

---

### Context

Considered storing only final debate outputs.

---

### Reasoning

Research goals require access to intermediate reasoning stages.

Examples:

* Initial opinions
* Critiques
* Revisions

These are necessary for analyzing influence and persuasion.

---

### Impact

Expanded database design to preserve all debate artifacts.

---

# Future Entries

Examples of future decisions:

---

## Consensus Algorithm Revision

When:

Consensus scoring methodology changes.

---

## Prompt Design Changes

When:

Agent prompts are updated.

---

## New Model Integrations

When:

Additional LLM providers are introduced.

---

## Evaluation Framework Changes

When:

New metrics are added or existing metrics are modified.

---

## Infrastructure Changes

When:

Redis, Celery, AWS, or other components are introduced.

---

# Usage Guidelines

A new entry should be added whenever a decision:

* Changes architecture
* Changes evaluation methodology
* Changes research methodology
* Changes infrastructure
* Changes data models

Minor implementation details should not be recorded.

---

# Summary

The Decision Log serves as the historical record of Synapse's evolution. It captures the reasoning behind important choices and ensures that future development remains understandable, reproducible, and maintainable.
