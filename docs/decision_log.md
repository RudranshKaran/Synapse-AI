# Synapse AI Decision Log

## Overview

This document records important engineering, product, and research decisions made during the development of Synapse AI.

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

Project name finalized as **Synapse AI**.

---

### Context

Several names were considered:

* ConvergeAI
* ConsensusAI
* DebateNet
* Agora
* Synapse AI

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

Position Synapse AI as a research and evaluation platform rather than a debate chatbot.

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

These capabilities differentiate Synapse AI from typical multi-agent projects.

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

* Model-A
* Model-B
* Model-C

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

# 2026-06-18

## Decision

Created `docs/ai_development_guidelines.md` to establish AI agent development protocols.

---

### Context

The file was referenced in documentation but did not exist. Agents and contributors lacked explicit guidance on code standards, project structure, and workflow expectations.

---

### Reasoning

A development guidelines document is necessary to ensure consistency across AI-assisted and manual development. It codifies the clean architecture principles, naming conventions, testing expectations, and documentation-first approach already implicit in the other docs.

---

### Impact

Development guidelines are now explicit and enforceable. All future implementation work should reference this document alongside the other core documentation files.

---

# 2026-06-18

## Decision

Use synchronous SQLAlchemy with auto-commit session pattern for the MVP backend.

---

### Context

The database layer needed to support FastAPI request lifecycles with proper transaction management. Both sync (psycopg2) and async (asyncpg) approaches were considered.

---

### Reasoning

Sync SQLAlchemy is simpler to set up, works natively with Alembic migrations, and is sufficient for MVP-level concurrency. The `get_db` dependency was designed to commit on success and rollback on exception, matching the standard FastAPI + SQLAlchemy pattern.

---

### Impact

Database operations are transactional and safe. Migrating to async SQLAlchemy with asyncpg later is possible without changing the repository/service layer interface.

---

# 2026-06-18

## Decision

Use SQLite in-memory database for tests instead of requiring PostgreSQL.

---

### Context

Tests need to run without external infrastructure. PostgreSQL is required for production but adds friction for local development and CI.

---

### Reasoning

SQLite provides sufficient SQL compatibility for testing the repository, service, and API layers. The test conftest creates tables per test function, ensuring isolation. The same SQLAlchemy models work against both databases.

---

### Impact

Tests run quickly without Docker. Real PostgreSQL-specific features (UUID generation, full-text search) are handled at the migration level and tested separately.

---

# 2026-06-18

## Decision

Implement a provider-agnostic LLM abstraction layer with registry, factory, and mock providers.

---

### Context

The system needs to support multiple LLM providers (OpenAI, Anthropic, Google, local models) without coupling business logic to any specific vendor.

---

### Reasoning

The `BaseModelProvider` abstract class defines the three core operations: `generate_response`, `critique_response`, and `revise_position`. The registry maps provider keys to classes, the factory creates instances by model name, and mock providers return deterministic responses for development. This design allows real providers to be added as subclasses without changing any existing code.

---

### Impact

Future provider integrations require only: (1) create a subclass of `BaseModelProvider`, (2) register it in the registry, (3) add a config entry. No service layer or API code needs to change.

---

# 2026-06-18

## Decision

Use UUID primary keys with `gen_random_uuid()` defaults in migrations.

---

### Context

The database schema needed a primary key strategy for all 6 MVP tables.

---

### Reasoning

UUIDs prevent enumeration attacks, work across distributed environments, and avoid ID collision issues when merging data. `gen_random_uuid()` is PostgreSQL-native and more performant than Python-side UUID generation for bulk inserts.

---

### Impact

IDs are non-sequential and globally unique. API responses expose UUIDs as strings. The migration uses server-side default generation.

---

# 2026-06-18

## Decision

Organize the backend into five clean layers: API, Service, Repository, Provider, and Core.

---

### Context

The existing directory structure from the initial scaffolding contained flat directories without implementation. A clear layering strategy was needed.

---

### Reasoning

Clean architecture principles ensure that each layer has a single responsibility and can be tested independently. The dependency flow is: API → Service → Repository → Database, with Core providing shared configuration. The Provider layer is separate and injectable.

---

### Impact

The codebase is navigable, testable, and extensible. New endpoints require adding route handlers (API), business logic (Service), and data queries (Repository) in their respective layers.

---

# 2026-06-18

## Decision

Created `DebateState` orchestration model to represent the complete debate lifecycle.

---

### Context

The opinion generation phase needed a state object to track debate progress across the full lifecycle. Future phases (critique, revision, consensus, evaluation) need to add data to this state.

---

### Reasoning

A single `DebateState` dataclass with pre-defined fields for opinions, critiques, revisions, consensus, and metrics provides a stable contract that won't need refactoring as phases are added. Empty collections for future phases are acceptable — they default to empty lists or None.

---

### Impact

The state model is stable and extensible. Future phases will populate the pre-defined fields without changing the class signature.

---

# 2026-06-18

## Decision

Extended `DebateRepository` with methods for rounds, responses, and status updates.

---

### Context

The opinion generation phase needs to create debate round records, store responses, and update debate status in the database. These operations were not supported by the existing repository.

---

### Reasoning

Keeping all database operations in the repository layer maintains clean architecture separation. The new methods (`create_round`, `create_response`, `update_debate_status`) follow the same patterns as the existing repository methods.

---

### Impact

The repository now supports the full set of operations needed for debate execution. Future phases will use the same methods.

---

# 2026-06-18

## Decision

Created separate `ExecutionService` for debate orchestration, distinct from `DebateService`.

---

### Context

The existing `DebateService` handles debate CRUD (create, get). Debate execution is an orchestration concern with different complexity — it coordinates providers, rounds, responses, and state tracking.

---

### Reasoning

Separating execution from CRUD follows single responsibility. `ExecutionService` handles the debate lifecycle pipeline, while `DebateService` handles debate management. The `ExecutionService` is designed so each future phase (critique, revision, etc.) becomes a method on it.

---

### Impact

Clear separation between debate management and debate execution. The execution service is the natural home for the LangGraph integration planned for later phases.

---

# 2026-06-18

## Decision

Run endpoint returns generated opinions directly in the response, diverging from the API spec.

---

### Context

The API spec (docs/api_specification.md) defines `POST /debates/{debate_id}/run` as returning `{"debate_id": "...", "status": "running"}`. For the MVP implementation, returning opinions directly avoids an extra round-trip to `GET /debates/{debate_id}/opinions`.

---

### Reasoning

The MVP prioritizes functional completeness. The opinion retrieval endpoint (`GET /debates/{debate_id}/opinions`) will be added in a later phase. The current response includes debate_id, status, and opinions — status is `opinions_generated` instead of `running` to indicate the phase completed.

---

### Impact

Clients receive opinions immediately after calling run. The API response contract is documented in the `DebateRunResponse` schema. A separate opinions endpoint can be added later without breaking this response.

---

# 2026-06-18

## Decision

Debate status values follow a progressive lifecycle pattern: created, running, opinions_generated.

---

### Context

The existing debate model supports a `status` field and a `completed_at` timestamp. A status progression was needed for the execution lifecycle.

---

### Reasoning

Explicit status values at each phase enable debugging, observability, and partial resumption. The `completed_at` field will be set when the debate reaches a terminal status.

---

### Impact

Status progression is extensible. Future phases will add new status values that slot between existing ones without changing prior logic.

---

# 2026-06-18

## Decision

Implemented the critique phase using the existing `response_relationships` table.

---

### Context

The critique phase is the second stage of the debate lifecycle. After opinions are generated, each participant needs to critique another participant's opinion. The database schema already documented a `response_relationships` table for tracking influence between responses, but it had not been implemented as an ORM model.

---

### Reasoning

The `response_relationships` table is the correct persistence mechanism for linking critiques to the opinions they target. Each critique generates a row with `source_response_id` (the critique), `target_response_id` (the opinion), and `relationship_type="critiques"`. This design enables future persuasion and influence metrics to trace which critiques influenced which opinions.

---

### Impact

The `ResponseRelationship` model and migration (002) have been added. The critique phase creates round 2 with phase "critique", stores critique responses with type "critique", and links each to its target opinion via a "critiques" relationship.

---

# 2026-06-18

## Decision

Circular critique pairing strategy: each participant critiques the next participant's opinion.

---

### Context

With N participants, every model needs to both give and receive a critique. A pairing strategy was needed that ensures full coverage.

---

### Reasoning

The circular strategy assigns participant[i] to critique participant[(i+1) % N]. This guarantees:
- Every participant generates exactly one critique.
- Every opinion receives exactly one critique.
- No self-targeting.
- Works for any number of participants >= 2.

For 3 models: A critiques B, B critiques C, C critiques A.
For 2 models: A critiques B, B critiques A.

---

### Impact

The pairing is deterministic and testable. It can be replaced with more sophisticated strategies (round-robin, randomized, all-pairs) as the system evolves.

---

# 2026-06-18

## Decision

Extended `DebateRunResponse` to include critiques; the `/run` endpoint now executes the full pipeline.

---

### Context

The API spec documents `POST /debates/{id}/run` as starting the complete debate pipeline. Previously it only ran opinion generation.

---

### Reasoning

Opinion generation alone is not a complete pipeline. The response now includes both `opinions` and `critiques` fields, with `critiques` being optional (None when only opinions are run). The `status` value is now "critiques_generated" when the full pipeline completes. The `run_opinion_generation()` method is still available for independent phase execution.

---

### Impact

Existing code using the `/run` endpoint automatically gets critiques in the response. The pipeline is extensible — future phases (revision, consensus) will be added to `run_debate()` as sequential steps.

---

# 2026-06-18

## Decision

Implemented the revision phase with self-targeting: each participant revises its own original opinion after receiving critiques.

---

### Context

The revision phase is the third stage of the debate lifecycle. After opinions are generated and critiques are exchanged, each participant needs to revise its position based on the critiques targeting its original opinion.

---

### Reasoning

Unlike critiques (which target another participant's opinion), revisions are self-referential. Each participant receives its original opinion plus all critiques that targeted that opinion, then generates a revised position. The revision is linked back to its original opinion via a `ResponseRelationship` with `relationship_type="revises"`, enabling future Opinion Drift calculations by comparing original vs. revised positions.

---

### Impact

The revision phase creates round 3 with phase "revision", stores revision responses with type "revision", and links each revision to its source opinion. The execution pipeline now produces a complete Opinion-Critique-Revision workflow. Status progression ends at "revisions_generated".

---

# 2026-06-18

## Decision

Critiques are consolidated when multiple target the same opinion before revision generation.

---

### Context

With the circular critique pairing strategy, each opinion receives exactly one critique (from the previous participant). However, future debate configurations may use different pairing strategies where an opinion receives multiple critiques.

---

### Reasoning

The revision phase collects all critiques targeting a given opinion and concatenates them with newline separators before passing them to `provider.revise_position()`. This design naturally handles both single-critique (current) and multi-critique (future) scenarios. The provider interface accepts a single `critique` string, so consolidation happens at the service layer.

---

### Impact

The revision phase is strategy-agnostic. It doesn't need to change regardless of how opinions are paired in the critique phase. The `RevisionRecord` tracks the `original_opinion_id` to support future Opinion Drift analysis.

---

# 2026-06-18

## Decision

Implemented consensus phase with a deterministic sentence-overlap ConsensusEngine.

---

### Context

The consensus phase is the fourth stage of the debate lifecycle. After revisions are generated, the system needs to produce a consensus artifact (score, agreements, disagreements, summary) from the final revised positions. The evaluation framework specifies embedding-based similarity as the long-term approach, but a simpler strategy is needed for MVP.

---

### Reasoning

The ConsensusEngine is implemented as an independent component in `app/consensus/engine.py`, separate from the execution service. It uses deterministic sentence-level overlap analysis: sentences that appear (normalized) across all positions become agreements, unique sentences become disagreements, and the consensus score is the ratio of shared to total sentences. This design is extensible -- the engine can be swapped for embedding-based or LLM-based strategies later without changing the service layer.

---

### Impact

The full pipeline now produces a ConsensusResult with score, agreements, disagreements, and summary. The consensus report is persisted to `consensus_reports` and individual items to `consensus_items` (migration 003). Status progression ends at "consensus_reached". The execution service accepts an optional `ConsensusEngine` instance, enabling dependency injection for testing.

---

# 2026-06-18

## Decision

Created the ConsensusItem ORM model for the consensus_items table documented in the database schema.

---

### Context

The database schema documents a `consensus_items` table with columns `id`, `consensus_report_id`, `item_type`, and `content`, but no ORM model or migration existed.

---

### Reasoning

Storing agreements and disagreements as individual rows rather than embedded JSON enables querying, filtering, and future analytics (e.g. "which agreements are most common across debates"). The `item_type` field supports "agreement", "disagreement", and "uncertainty" types.

---

### Impact

Migration 003 creates the `consensus_items` table with foreign key to `consensus_reports`. Each consensus run stores N agreement items + M disagreement items, linked back to the report.

---

# 2026-06-18

## Decision

Used `all-MiniLM-L6-v2` as the embedding model for semantic similarity.

---

### Context

The evaluation framework requires embedding-based semantic similarity for Agreement Score and Opinion Drift calculations. The tech stack documents Sentence Transformers as the evaluation engine.

---

### Reasoning

`all-MiniLM-L6-v2` is a lightweight, well-supported model that produces 384-dimensional normalized embeddings. It runs efficiently on CPU (~80MB model size), has strong benchmark performance on semantic similarity (STS), and is widely used in production. The embedding utility is designed with `lru_cache` so the model is loaded once and reused across all metric calculations.

---

### Impact

Embedding generation adds ~1-2 seconds on first call (model loading), then runs in milliseconds. The model choice is configurable via the `model_name` parameter for future upgrades.

---

# 2026-06-18

## Decision

Implemented three evaluation metrics: Agreement Score, Opinion Drift, and Confidence Shift.

---

### Context

The evaluation framework defines five primary metrics. Three are implemented now: Agreement Score (pairwise embedding similarity of revised positions), Opinion Drift (embedding distance between original and revised), and Confidence Shift (difference in confidence scores). Persuasion Score and Debate Efficiency are deferred to a future phase.

---

### Reasoning

Each metric is implemented as an independent calculator function in `app/evaluation/metrics/`, making them individually testable and extensible. The `EvaluationEngine` orchestrates them, accepting debate data and returning an `EvaluationResult` dataclass. The architecture supports adding new metrics without modifying existing code.

---

### Impact

The execution pipeline now runs all five phases and completes with status "evaluation_complete". Metrics are persisted to `evaluation_metrics` (agreement_score) and `participant_metrics` (opinion_drift, confidence_shift). A `GET /debates/{id}/metrics` endpoint exposes computed values. The evaluation runs synchronously as phase 5.

---

# 2026-06-18

## Decision

Added `ParticipantMetric` ORM model for per-participant metrics storage.

---

### Context

The database schema documents a `participant_metrics` table but no ORM model or migration existed. Opinion Drift and Confidence Shift are per-participant metrics (different values for each model) and require their own table rather than the debate-level `evaluation_metrics` table.

---

### Reasoning

Separating debate-level metrics (`evaluation_metrics`) from participant-level metrics (`participant_metrics`) follows the documented schema design. Each row stores a single metric value for a specific participant, enabling per-model analysis and future queries like "which model had the highest opinion drift across all debates".

---

### Impact

Migration 004 creates the `participant_metrics` table with foreign keys to both debates and participants. The repository has `create_participant_metric()` and `get_participant_metrics_for_debate()` methods. The metrics endpoint returns per-model values using model names as keys.

---

# Usage Guidelines

A new entry should be added whenever a decision:

* Changes architecture