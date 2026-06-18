// ── Request types ─────────────────────────────────────────

export interface CreateDebateRequest {
  question: string;
  models: string[];
  provider?: string;
  config?: Record<string, unknown>;
}

export interface DebateListParams {
  page?: number;
  page_size?: number;
  status?: string;
  search?: string;
}

export interface RunDebateRequest {
  rounds?: number;
}

// ── Response types ────────────────────────────────────────

export interface ParticipantInfo {
  participant_id: string;
  model_name: string;
  provider: string;
}

export interface DebateResponse {
  debate_id: string;
  question: string;
  status: string;
  participants: ParticipantInfo[];
  created_at: string | null;
  completed_at: string | null;
}

export interface DebateListItem {
  debate_id: string;
  question: string;
  status: string;
  created_at: string | null;
  completed_at: string | null;
  participant_count: number;
  agreement_score: number | null;
}

export interface DebateListResponse {
  total: number;
  page: number;
  page_size: number;
  debates: DebateListItem[];
}

export interface OpinionResult {
  participant_id: string;
  model_name: string;
  content: string;
  confidence_score: number | null;
}

export interface CritiqueResult {
  participant_id: string;
  model_name: string;
  content: string;
  confidence_score: number | null;
  target_participant_id: string;
  target_model_name: string;
}

export interface RevisionResult {
  participant_id: string;
  model_name: string;
  content: string;
  confidence_score: number | null;
  original_participant_id: string;
  original_model_name: string;
}

export interface ConsensusResult {
  consensus_score: number;
  agreements: string[];
  disagreements: string[];
  summary: string;
}

export interface EvaluationResult {
  agreement_score: number;
  opinion_drifts: Record<string, number>;
  confidence_shifts: Record<string, number>;
}

export interface RunDebateResponse {
  debate_id: string;
  status: string;
  opinions: OpinionResult[];
  critiques: CritiqueResult[] | null;
  revisions: RevisionResult[] | null;
  consensus: ConsensusResult | null;
  evaluation: EvaluationResult | null;
}

export interface TranscriptEntry {
  response_id: string;
  participant_id: string;
  model_name: string;
  response_type: string;
  content: string;
  confidence_score: number | null;
  created_at: string | null;
  relationships: Record<string, string>[];
}

export interface TranscriptRound {
  round_id: string;
  round_number: number;
  phase: string;
  created_at: string | null;
  responses: TranscriptEntry[];
}

export interface TranscriptConsensus {
  consensus_score: number | null;
  agreements: string[];
  disagreements: string[];
  summary: string | null;
}

export interface TranscriptMetricsInfo {
  agreement_score: number | null;
  opinion_drifts: Record<string, number>;
  confidence_shifts: Record<string, number>;
}

export interface Transcript {
  debate_id: string;
  question: string;
  status: string;
  participants: ParticipantInfo[];
  rounds: TranscriptRound[];
  consensus: TranscriptConsensus | null;
  metrics: TranscriptMetricsInfo | null;
  created_at: string | null;
  completed_at: string | null;
}

export interface MetricsResponse {
  debate_id: string;
  agreement_score: number | null;
  opinion_drifts: Record<string, number>;
  confidence_shifts: Record<string, number>;
}

export interface ApiError {
  error: {
    code: string;
    message: string;
  };
}

// ── Constants ─────────────────────────────────────────────

export const STATUS_COLORS: Record<string, string> = {
  created: "bg-gray-100 text-gray-700 border-gray-200",
  running: "bg-blue-100 text-blue-700 border-blue-200",
  opinions_generated: "bg-violet-100 text-violet-700 border-violet-200",
  critiques_generated: "bg-amber-100 text-amber-700 border-amber-200",
  revisions_generated: "bg-orange-100 text-orange-700 border-orange-200",
  consensus_reached: "bg-cyan-100 text-cyan-700 border-cyan-200",
  evaluation_complete: "bg-emerald-100 text-emerald-700 border-emerald-200",
};

export const MODEL_NAMES: Record<string, string> = {
  "model-a": "Model A",
  "model-b": "Model B",
  "model-c": "Model C",
  "gpt-4o-mini": "GPT-4o Mini",
  "gpt-4o": "GPT-4o",
};

export const STATUS_LABELS: Record<string, string> = {
  created: "Created",
  running: "Running",
  opinions_generated: "Opinions Ready",
  critiques_generated: "Critiques Ready",
  revisions_generated: "Revisions Ready",
  consensus_reached: "Consensus Reached",
  evaluation_complete: "Complete",
};
