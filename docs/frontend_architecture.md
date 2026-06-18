# Synapse AI — Frontend Architecture

## Overview

Synapse AI's frontend is a Next.js application that serves as the **User Interaction Layer** — the primary interface for creating debates, monitoring debate execution, exploring transcripts, and analyzing behavioral metrics. The frontend consumes the backend API surface (`/api/v1/*`) and visualizes the full debate lifecycle.

This document defines the complete frontend architecture: pages, routing, components, API integration, state management, charting, folder structure, and design system. No implementation code is included — this is the blueprint for development.

---

## 1. Tech Stack

| Concern              | Choice          | Rationale                                 |
| -------------------- | --------------- | ----------------------------------------- |
| Framework            | Next.js 14      | App Router, SSG/SSR, file-based routing   |
| Language             | TypeScript      | Type safety, API contract alignment       |
| Styling              | Tailwind CSS    | Utility-first, design system primitives   |
| UI Components        | shadcn/ui       | Accessible, themeable, Radix-based        |
| State Management     | React Query     | Server state caching, polling, mutations  |
| Charting             | Recharts        | Declarative, React-native, composable     |
| HTTP Client          | fetch + React Query | No extra dependency needed            |
| Form Validation      | React Hook Form + Zod | Schema validation matches Pydantic  |
| Icons                | Lucide React    | Consistent icon set, tree-shakeable       |

---

## 2. Route Structure

```
/                          → Landing / Home
/debates                   → Debate list (paginated, filterable, searchable)
/debates/new               → Create debate form
/debates/[id]              → Debate detail / transcript view
/debates/[id]/run          → Run debate (with progress/realtime status)
/debates/[id]/metrics      → Evaluation metrics dashboard
```

### Routes with their primary API calls

| Route             | API Call(s)                                       |
| ----------------- | ------------------------------------------------- |
| `/`               | `GET /debates?page=1&page_size=5` (recent)        |
| `/debates`        | `GET /debates?page=&page_size=&status=&search=`   |
| `/debates/new`    | — (form submission calls `POST /debates`)         |
| `/debates/[id]`   | `GET /debates/{id}/transcript`                    |
| `/debates/[id]/run` | `POST /debates/{id}/run` (synchronous)         |
| `/debates/[id]/metrics` | `GET /debates/{id}/metrics`                |

---

## 3. Page Specifications

### 3.1 Landing Page (`/`)

**Purpose:** First impression, showcase recent debates, quick-start to create.

**Sections:**
- Hero section: project tagline, brief description, "Create New Debate" CTA
- Recent debates section: last 5 debates from `GET /debates?page=1&page_size=5`
- Quick stats (if available): total debates run, average consensus score
- Footer with link to docs

**States:** Loading (skeleton cards), empty (no debates yet — prompt to create), error (retry button)

---

### 3.2 Debate List (`/debates`)

**Purpose:** Browse, search, and filter all debates.

**UI Components:**
- **Search bar** — text input with debounced search (300ms), triggers `search=` param
- **Status filter** — dropdown or pill buttons (All, Created, Running, Evaluation Complete, etc.)
- **Sort / pagination** — page size selector (10/20/50), page navigation
- **Debate cards table** — table or card grid showing each `DebateListItem`:
  - Question text (truncated to 2 lines)
  - Status badge (color-coded by lifecycle stage)
  - Participant count
  - Agreement score (if available) with mini gauge
  - Created date (relative: "2 hours ago")
  - Click to navigate to `/debates/[id]`

**States:** Loading (skeleton table), empty with search (no results message), empty without search (prompt to create), error (retry banner)

**Query key structure:** `["debates", { page, pageSize, status, search }]`

---

### 3.3 Create Debate (`/debates/new`)

**Purpose:** Configure and start a new debate.

**Form fields:**
- **Question** — textarea, required, 10–5000 chars, character counter
- **Models** — multi-select checkboxes or toggle chips: model-a, model-b, model-c, gpt-4o-mini, gpt-4o
- **Provider** — radio/select: "Mock (fast, for testing)" or "OpenAI (real LLM)"
- **(Future)** Config section — collapsed accordion for advanced settings

**Validation** (matches `DebateCreate` schema):
- `question`: required, 1–5000 chars
- `models`: required, 1–10 items
- `provider`: "mock" or "openai"

**Submission flow:**
1. `POST /debates` → receive `debate_id`
2. Navigate to `/debates/[debate_id]` (detail view)
3. On the detail view, user can click "Run Debate" to start execution

**States:** Idle (empty form), validating (inline field errors), submitting (button loading state), success (redirect), error (API error banner)

---

### 3.4 Debate Detail & Transcript (`/debates/[id]`)

**Purpose:** View the complete debate transcript. This is the **primary view** users will spend time on.

**Sections (vertical timeline layout):**

#### Header
- Question text (large, prominent)
- Status badge + created/completed timestamps
- Participant badges (model name + provider label)
- Action buttons: "Run Debate" (if status is `created`), "View Metrics" (if `evaluation_complete`)

#### Phase Timeline (accordion or stepper)
Each phase is a collapsible section ordered by `round_number`:

1. **Opinions** (phase: "opinion")
   - One card per participant showing their initial position
   - Card shows: model name badge, confidence score bar, content text
2. **Critiques** (phase: "critique")
   - One card per critique
   - Visual arrow: Critic Model → Target Model (from `relationships`)
   - Critique content, confidence score
3. **Revisions** (phase: "revision")
   - One card per participant showing revised position
   - Visual diff indicator: arrow from opinion → revision
   - Updated confidence score
4. **Consensus** (phase: "consensus")
   - Consensus score gauge (large, animated)
   - Agreements list (green highlight)
   - Disagreements list (amber/orange highlight)
   - Summary text (callout box)
5. **Evaluation** (phase: "evaluation")
   - Agreement score display
   - Per-model opinion drift (bar chart or table)
   - Per-model confidence shift (bar chart or table)

#### Empty/Pre-execution State
If debate status is `created`:
- Show the header with participants
- Show a prompt: "This debate hasn't been run yet"
- "Run Debate" button prominently displayed

**API call:** `GET /debates/{id}/transcript` — single call for all data

**States:** Loading (full-page skeleton with phase placeholders), not found (404 state), pre-execution (created status), completed (full transcript)

---

### 3.5 Run Debate (`/debates/[id]/run`)

**Purpose:** Execute the debate pipeline and show progress.

**Note:** The `/run` endpoint is synchronous. For MVP, this means:
- Show a "running" spinner/progress while the API call is in-flight
- The API returns the full `DebateRunResponse` when complete
- Redirect to the detail view with the transcript

**Implementation approach:**
1. User clicks "Run Debate" on the detail page
2. Transition to a full-screen "Running Debate..." state
3. Show animated phase indicators: Opinions → Critiques → Revisions → Consensus → Evaluation
4. Each phase lights up as it completes (estimate based on progress, or use multiple sequential calls)
5. On completion, redirect to `/debates/[id]` where the full transcript is now available

**Alternative (simpler) approach for MVP:**
- Show a loading spinner with phases listed
- When API returns, redirect immediately
- No real-time progress (API is synchronous)

---

### 3.6 Evaluation Metrics (`/debates/[id]/metrics`)

**Purpose:** Focused dashboard for behavioral metrics.

**Sections:**

#### Overview Cards
- **Agreement Score** — large number with gauge/ring visualization
- **Average Opinion Drift** — computed from per-model values
- **Average Confidence Shift** — computed from per-model values

#### Per-Model Breakdown
- Table or card grid with one row per participant:
  - Model name
  - Opinion Drift (0–1 scale, horizontal bar)
  - Confidence Shift (positive/negative, color-coded bar)
  - Initial confidence vs revised confidence (side-by-side)

#### Consensus Summary
- Reuse consensus section from transcript if needed
- Consensus score gauge
- Agreements / disagreements list

**API call:** `GET /debates/{id}/metrics`

**States:** Loading (skeleton cards), no metrics yet (debate not complete), error

---

## 4. API Integration Layer

### 4.1 API Client

```
frontend/src/lib/api/
  client.ts          — base fetch wrapper, base URL, error handling
  debates.ts         — debate CRUD + list functions
  execution.ts       — run debate
  transcripts.ts     — get transcript
  metrics.ts         — get metrics
  types.ts           — TypeScript interfaces matching API schemas
```

### 4.2 TypeScript Types

Generate types that mirror the Pydantic schemas:

| Pydantic Schema              | TypeScript Interface           |
| ---------------------------- | ------------------------------ |
| `DebateCreate`               | `CreateDebateRequest`          |
| `DebateResponse`             | `DebateResponse`               |
| `DebateListItem`             | `DebateListItem`               |
| `DebateListParams`           | `DebateListParams`             |
| `DebateListResponse`         | `DebateListResponse`           |
| `DebateRunRequest`           | `RunDebateRequest`             |
| `DebateRunResponse`          | `RunDebateResponse`            |
| `OpinionResult`              | `OpinionResult`                |
| `CritiqueResult`             | `CritiqueResult`               |
| `RevisionResult`             | `RevisionResult`               |
| `ConsensusResult`            | `ConsensusResult`              |
| `EvaluationResult`           | `EvaluationResult`             |
| `MetricsResponse`            | `MetricsResponse`              |
| `Transcript`                 | `Transcript`                   |
| `TranscriptRound`            | `TranscriptRound`              |
| `TranscriptEntry`            | `TranscriptEntry`              |
| `TranscriptConsensus`        | `TranscriptConsensus`          |
| `TranscriptMetricsInfo`      | `TranscriptMetricsInfo`        |

### 4.3 React Query Hooks

```
frontend/src/hooks/
  useDebates.ts        — useDebateList(params), useDebate(id)
  useCreateDebate.ts   — useCreateDebate() mutation
  useRunDebate.ts      — useRunDebate() mutation
  useTranscript.ts     — useTranscript(id)
  useMetrics.ts        — useMetrics(id)
```

**Key query configurations:**

| Hook               | Query Key Pattern                 | Stale Time | Refetch        |
| ------------------ | --------------------------------- | ---------- | -------------- |
| `useDebateList`    | `["debates", params]`             | 30s        | On window focus|
| `useDebate`        | `["debates", id]`                 | 30s        | On window focus|
| `useTranscript`    | `["transcript", id]`              | Infinity   | Manual only    |
| `useMetrics`       | `["metrics", id]`                 | Infinity   | Manual only    |
| `useCreateDebate`  | — (mutation)                      | —          | Invalidate list|
| `useRunDebate`     | — (mutation)                      | —          | Invalidate all |

**Invalidation strategy after running a debate:**
```typescript
// After successful run mutation:
queryClient.invalidateQueries({ queryKey: ["debates"] });
queryClient.invalidateQueries({ queryKey: ["transcript", debateId] });
queryClient.invalidateQueries({ queryKey: ["metrics", debateId] });
```

---

## 5. State Management

**Server state** (all data from API): React Query — no Redux, no Zustand needed.

**UI state** (local component state): React `useState` / `useReducer`.

**URL state** (pagination, filters, search): Next.js search params (`useSearchParams`).

**No global client-state store** — React Query handles caching, deduplication, and background refetching. The transcript endpoint returns everything in one call, so there's no need to share debate data between components via a store.

---

## 6. Component Architecture

### 6.1 Layout Components

```
frontend/src/components/layout/
  RootLayout.tsx         — App shell: header, main, footer
  Header.tsx             — Logo, navigation, "New Debate" button
  Footer.tsx             — Links, version
  PageContainer.tsx      — Max-width wrapper with consistent padding
```

### 6.2 Shared UI Components

Built with shadcn/ui primitives:

```
frontend/src/components/ui/        (shadcn/ui generated)
  button.tsx
  card.tsx
  badge.tsx
  input.tsx
  textarea.tsx
  select.tsx
  skeleton.tsx
  dialog.tsx
  accordion.tsx
  tabs.tsx
  table.tsx
  toast.tsx
```

### 6.3 Feature Components

```
frontend/src/components/debates/
  DebateCard.tsx               — Summary card for list view
  DebateCardSkeleton.tsx       — Loading placeholder
  DebateTable.tsx              — Table/grid of DebateCards
  StatusBadge.tsx              — Color-coded status pill
  ParticipantBadge.tsx         — Model name + provider chip
  ConfidenceBar.tsx            — Horizontal confidence bar (0–100)
  QuestionText.tsx             — Truncated/question display

frontend/src/components/transcript/
  TranscriptTimeline.tsx       — Vertical timeline of all phases
  PhaseSection.tsx             — Collapsible phase accordion
  OpinionCard.tsx              — Single opinion display
  CritiqueCard.tsx             — Critique with target arrow
  RevisionCard.tsx             — Revision with drift indicator
  ConsensusDisplay.tsx         — Score gauge + agreements/disagreements
  EvaluationSummary.tsx        — Metrics cards + per-model breakdown
  PhaseIndicator.tsx           — Phase step in progress view

frontend/src/components/forms/
  CreateDebateForm.tsx         — Full create debate form
  ModelSelector.tsx            — Multi-select model chips
  ProviderSelector.tsx         — Mock / OpenAI radio
  QuestionInput.tsx            — Textarea with validation

frontend/src/components/charts/
  ConsensusGauge.tsx           — Circular gauge (0–100)
  AgreementGauge.tsx           — Score ring
  OpinionDriftChart.tsx        — Per-model horizontal bars
  ConfidenceShiftChart.tsx     — Per-model positive/negative bars
  PairwiseComparisonChart.tsx  — Heatmap or bar chart
```

---

## 7. Charting Approach

Use **Recharts** for all visualizations. Charts are thin wrappers around Recharts primitives.

### Chart Inventory

| Chart                          | Type                      | Data Source                         |
| ------------------------------ | ------------------------- | ----------------------------------- |
| Consensus Score Gauge          | Circular progress (SVG)   | `transcript.consensus.consensus_score` |
| Agreement Score Ring           | Circular progress (SVG)   | `metrics.agreement_score`           |
| Opinion Drift (per model)      | Horizontal bar chart      | `metrics.opinion_drifts`            |
| Confidence Shift (per model)   | Horizontal bar (+/− color)| `metrics.confidence_shifts`         |
| Pairwise Agreement (future)    | Heatmap                   | (future endpoint)                   |
| Debate Timeline (future)       | Gantt or step chart       | `transcript.rounds[*].created_at`   |

### Recharts Configuration Patterns

```typescript
// Shared responsive container
<ResponsiveContainer width="100%" height={300}>
  <BarChart data={...}>...</BarChart>
</ResponsiveContainer>

// Consistent colors
const MODEL_COLORS = {
  "model-a": "#3b82f6",  // blue
  "model-b": "#10b981",  // green
  "model-c": "#f59e0b",  // amber
};
```

For the gauges, use a custom SVG circle component rather than Recharts (simpler, more control). The gauge takes a `value: number (0–100)` and renders a semi-circle or full-circle with animated arc.

---

## 8. Folder Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── logo.svg
│
├── src/
│   ├── app/
│   │   ├── layout.tsx              — Root layout (RootLayout)
│   │   ├── page.tsx                — Landing page
│   │   ├── debates/
│   │   │   ├── page.tsx            — Debate list
│   │   │   ├── new/
│   │   │   │   └── page.tsx        — Create debate
│   │   │   └── [id]/
│   │   │       ├── page.tsx        — Debate detail / transcript
│   │   │       ├── run/
│   │   │       │   └── page.tsx    — Run debate (progress)
│   │   │       └── metrics/
│   │   │           └── page.tsx    — Evaluation metrics
│   │   └── globals.css             — Tailwind entry point
│   │
│   ├── components/
│   │   ├── ui/                     — shadcn/ui primitives
│   │   ├── layout/                 — RootLayout, Header, Footer
│   │   ├── debates/                — Debate-specific components
│   │   ├── transcript/             — Transcript-specific components
│   │   ├── forms/                  — Form components
│   │   └── charts/                 — Chart components
│   │
│   ├── hooks/
│   │   ├── useDebates.ts
│   │   ├── useCreateDebate.ts
│   │   ├── useRunDebate.ts
│   │   ├── useTranscript.ts
│   │   └── useMetrics.ts
│   │
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts
│   │   │   ├── debates.ts
│   │   │   ├── execution.ts
│   │   │   ├── transcripts.ts
│   │   │   ├── metrics.ts
│   │   │   └── types.ts
│   │   └── utils.ts                — cn(), formatDate(), etc.
│   │
│   └── config/
│       └── index.ts                — API_BASE_URL, constants
│
├── tailwind.config.ts
├── next.config.ts
├── tsconfig.json
├── package.json
└── components.json                 — shadcn/ui config
```

---

## 9. Design System

### 9.1 Colors

Derived from the research/analytics theme — professional, data-focused, not playful.

```typescript
// Tailwind theme extensions
colors: {
  // Status colors
  "status-created":        "#6b7280",  // gray-500
  "status-running":         "#3b82f6",  // blue-500
  "status-opinions":        "#8b5cf6",  // violet-500
  "status-critiques":       "#f59e0b",  // amber-500
  "status-revisions":       "#f97316",  // orange-500
  "status-consensus":       "#06b6d4",  // cyan-500
  "status-evaluation":      "#10b981",  // emerald-500
  "status-complete":        "#22c55e",  // green-500

  // Model colors
  "model-a":               "#3b82f6",  // blue
  "model-b":               "#10b981",  // green
  "model-c":               "#f59e0b",  // amber

  // Semantic
  "agreement":             "#22c55e",  // green
  "disagreement":          "#ef4444",  // red
  "drift-high":            "#f97316",  // orange
  "shift-positive":        "#22c55e",  // green
  "shift-negative":        "#ef4444",  // red
}
```

### 9.2 Typography

| Element          | Font    | Size  | Weight  |
| ---------------- | ------- | ----- | ------- |
| Page title       | Inter   | 3xl   | Bold    |
| Section heading  | Inter   | 2xl   | Semibold|
| Card title       | Inter   | base  | Semibold|
| Body             | Inter   | sm    | Normal  |
| Code / content   | mono    | sm    | Normal  |
| Status badge     | Inter   | xs    | Medium  |

### 9.3 Spacing

Consistent 4px grid: `space-y-4`, `space-y-6`, `gap-4`, `p-4`, `p-6` for cards.

### 9.4 Status Badge Color Mapping

```typescript
const STATUS_COLORS: Record<string, string> = {
  created:             "bg-gray-100 text-gray-700",
  running:             "bg-blue-100 text-blue-700",
  opinions_generated:  "bg-violet-100 text-violet-700",
  critiques_generated: "bg-amber-100 text-amber-700",
  revisions_generated: "bg-orange-100 text-orange-700",
  consensus_reached:   "bg-cyan-100 text-cyan-700",
  evaluation_complete: "bg-emerald-100 text-emerald-700",
};
```

---

## 10. Key Implementation Decisions

### 10.1 Server Components vs Client Components

- **Page layouts, headers, metadata**: Server Components
- **Interactive pages (forms, lists with filters, transcript)**: Client Components (`"use client"`)
- **Charts**: Client Components (Recharts requires browser APIs)
- **Data fetching**: React Query in Client Components (App Router's `fetch` not needed for this use case since we need polling/caching)

### 10.2 Transcript as Single Source of Truth

The `GET /debates/{id}/transcript` endpoint returns everything needed for the detail view. The frontend should make **one API call** for the detail page and derive all sub-views from it (rather than calling separate endpoints for opinions, critiques, etc.). The `/metrics` tab is the only exception — it calls `GET /debates/{id}/metrics`.

### 10.3 Run Debate UX

Since the `/run` endpoint is synchronous:
- For MVP, show a loading state with phase labels that animate sequentially
- Estimate each phase at ~20% of total time
- On response, redirect to transcript view
- Future: switch to async with WebSocket or polling for real-time phase updates

### 10.4 Error Handling Pattern

All API calls follow the same error pattern:

```typescript
interface ApiError {
  error: {
    code: string;
    message: string;
  };
}
```

React Query's `onError` callbacks display toast notifications. 4xx errors show inline field validation. 5xx errors show a banner with retry.

### 10.5 Debounced Search

The debate list search input debounces at 300ms before updating URL search params and triggering a new query. Use `useDeferredValue` or a custom `useDebounce` hook.

---

## 11. Implementation Order

| Step | Deliverable                          | Depends On      |
| ---- | ------------------------------------ | --------------- |
| 1    | Next.js project setup + Tailwind + shadcn/ui | —              |
| 2    | Layout components (RootLayout, Header, Footer) | Step 1         |
| 3    | API client layer + TypeScript types  | Step 1          |
| 4    | React Query hooks                    | Step 3          |
| 5    | `GET /debates` list page + pagination + search | Steps 2, 4     |
| 6    | Create debate form (`POST /debates`) | Steps 2, 4      |
| 7    | Debate detail / transcript page (`GET /debates/{id}/transcript`) | Steps 2, 4     |
| 8    | Run debate flow (`POST /debates/{id}/run`) | Step 7          |
| 9    | Metrics page (`GET /debates/{id}/metrics`) + charts | Steps 2, 4     |
| 10   | Landing page                         | Steps 5, 6      |
| 11   | Polish: loading states, error handling, empty states | All steps |

---

## 12. Docker Compose Integration

The existing `docker-compose.yml` runs the backend at `localhost:8000`. The frontend dev server runs at `localhost:3000`. Add the frontend as a third service:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
  ports:
    - "3000:3000"
  environment:
    - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
  depends_on:
    - backend
```

The API base URL is configured via `NEXT_PUBLIC_API_URL` environment variable, defaulting to `http://localhost:8000/api/v1` in development.

---

## 13. Summary

The frontend architecture follows the backend's clean separation philosophy:
- **6 pages** mapped directly to API endpoints
- **Single API call** for the transcript view (the primary user-facing feature)
- **React Query** for all server state — no global store
- **Recharts** for charting, shadcn/ui for primitives, Tailwind for styling
- **TypeScript types** mirroring Pydantic schemas for end-to-end type safety
- **No real-time infrastructure** needed for MVP — synchronous run with loading state
- **All components** organize by feature domain (debates, transcript, forms, charts)
