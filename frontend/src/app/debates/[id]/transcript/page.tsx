"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  MessageSquare,
  Shield,
  RefreshCw,
  GitMerge,
  BarChart3,
  Lightbulb,
  Loader2,
  Target,
  ArrowRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { StatusBadge } from "@/components/shared/status-badge";
import { ModelBadge } from "@/components/shared/model-badge";
import { PhaseSection } from "@/components/transcript/phase-section";
import { ResponseCard } from "@/components/transcript/response-card";
import { ConsensusSummary } from "@/components/transcript/consensus-summary";
import { EvaluationSummary } from "@/components/transcript/evaluation-summary";
import { useTranscript } from "@/lib/api/hooks";
import { formatDate, getModelDisplayName } from "@/lib/utils";
import type { TranscriptEntry } from "@/lib/api/types";

const PHASES = [
  { id: "opinion",   label: "Opinions",     icon: Lightbulb,    color: "border-l-violet-500" },
  { id: "critique",  label: "Critiques",    icon: Shield,       color: "border-l-amber-500" },
  { id: "revision",  label: "Revisions",    icon: RefreshCw,    color: "border-l-orange-500" },
  { id: "consensus", label: "Consensus",    icon: GitMerge,     color: "border-l-cyan-500" },
  { id: "evaluation",label: "Evaluation",   icon: BarChart3,    color: "border-l-emerald-500" },
];

function TranscriptSkeleton() {
  return (
    <div className="space-y-4 max-w-4xl mx-auto">
      <Skeleton className="h-6 w-32" />
      <Skeleton className="h-8 w-3/4" />
      <Skeleton className="h-4 w-48" />
      <div className="flex gap-2 mt-4">
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-6 w-20" />
        <Skeleton className="h-6 w-20" />
      </div>
      {Array.from({ length: 3 }).map((_, i) => (
        <Skeleton key={i} className="h-32 w-full" />
      ))}
    </div>
  );
}

export default function TranscriptPage() {
  const params = useParams();
  const router = useRouter();
  const debateId = params.id as string;
  const { data: transcript, isLoading, isError } = useTranscript(debateId);

  if (isLoading) return <TranscriptSkeleton />;

  if (isError || !transcript) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12 space-y-4">
        <p className="text-red-600">Failed to load transcript.</p>
        <Button variant="outline" onClick={() => router.push("/debates")}>
          Back to debates
        </Button>
      </div>
    );
  }

  // Build model name lookup
  const modelNameMap: Record<string, string> = {};
  transcript.participants.forEach((p) => {
    modelNameMap[p.participant_id] = p.model_name;
  });

  // Group responses by phase
  const phaseResponses: Record<string, TranscriptEntry[]> = {};
  transcript.rounds.forEach((round) => {
    phaseResponses[round.phase] = round.responses;
  });

  // Build critique target map: response_id → list of critique entries
  const critiqueTargetMap: Record<string, TranscriptEntry[]> = {};
  const critiqueEntries = phaseResponses["critique"] || [];
  critiqueEntries.forEach((entry) => {
    const targetId = entry.relationships?.[0]?.target_response_id;
    if (targetId) {
      if (!critiqueTargetMap[targetId]) critiqueTargetMap[targetId] = [];
      critiqueTargetMap[targetId].push(entry);
    }
  });

  // Build revision mapping: find which opinions each revision revises
  const revisionMap: Record<string, TranscriptEntry> = {};
  const revisionEntries = phaseResponses["revision"] || [];
  revisionEntries.forEach((entry) => {
    const targetId = entry.relationships?.[0]?.target_response_id;
    if (targetId) revisionMap[targetId] = entry;
  });

  // For each opinion, find critiques targeting it and the revision
  const opinionEntries = phaseResponses["opinion"] || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back link */}
      <Link
        href={`/debates/${debateId}`}
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to debate
      </Link>

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold leading-snug">{transcript.question}</h1>
        <div className="flex items-center gap-3 mt-2 text-sm text-gray-500">
          <StatusBadge status={transcript.status} />
          <span>Created {formatDate(transcript.created_at)}</span>
          {transcript.completed_at && (
            <span>Completed {formatDate(transcript.completed_at)}</span>
          )}
        </div>
      </div>

      {/* Participants */}
      <div className="flex flex-wrap gap-2">
        {transcript.participants.map((p) => (
          <ModelBadge key={p.participant_id} modelName={p.model_name} provider={p.provider} />
        ))}
      </div>

      {/* Sticky phase navigation */}
      <nav className="sticky top-14 z-40 bg-background/95 backdrop-blur border-b border-border -mx-4 px-4 py-2 flex items-center gap-1 overflow-x-auto">
        {PHASES.map((phase, i) => {
          const PhaseIcon = phase.icon;
          const hasData = (phaseResponses[phase.id]?.length ?? 0) > 0 ||
            (phase.id === "consensus" && transcript.consensus) ||
            (phase.id === "evaluation" && transcript.metrics);
          return (
            <a
              key={phase.id}
              href={`#phase-${phase.id}`}
              className="flex items-center gap-1.5 text-xs font-medium px-2.5 py-1.5 rounded-md hover:bg-gray-100 transition-colors whitespace-nowrap text-gray-600"
            >
              <PhaseIcon className="h-3.5 w-3.5" />
              <span>{phase.label}</span>
              {hasData && (
                <span className="w-1.5 h-1.5 rounded-full bg-green-400" />
              )}
              {i < PHASES.length - 1 && (
                <ArrowRight className="h-3 w-3 text-gray-300 ml-0.5" />
              )}
            </a>
          );
        })}
      </nav>

      {/* Timeline content */}
      <div className="space-y-6">
        {/* ── Phase 1: Opinions ── */}
        <PhaseSection
          id="phase-opinion"
          title="Initial Opinions"
          subtitle="Each model's independent position on the question"
          icon={<Lightbulb className="h-5 w-5 text-violet-500" />}
        >
          {opinionEntries.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">No opinions recorded.</p>
          ) : (
            opinionEntries.map((entry, i) => {
              const critiques = critiqueTargetMap[entry.response_id] || [];
              const revision = revisionMap[entry.response_id];
              return (
                <div key={entry.response_id} className="space-y-2">
                  <ResponseCard
                    entry={entry}
                    accentColor="border-l-violet-500"
                    icon={<MessageSquare className="h-4 w-4 text-violet-500" />}
                  />
                  {/* Inline critique/revision summary under each opinion */}
                  {critiques.length > 0 && (
                    <div className="flex items-center gap-2 pl-4">
                      <Target className="h-3 w-3 text-amber-400" />
                      <span className="text-xs text-gray-400">
                        {critiques.length} critique{critiques.length > 1 ? "s" : ""} received
                      </span>
                    </div>
                  )}
                  {revision && (
                    <div className="flex items-center gap-2 pl-4">
                      <RefreshCw className="h-3 w-3 text-orange-400" />
                      <span className="text-xs text-gray-400">Revised position available</span>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </PhaseSection>

        {/* ── Phase 2: Critiques ── */}
        <PhaseSection
          id="phase-critique"
          title="Critiques"
          subtitle="Models challenge each other's reasoning"
          icon={<Shield className="h-5 w-5 text-amber-500" />}
        >
          {critiqueEntries.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">No critiques recorded.</p>
          ) : (
            critiqueEntries.map((entry) => {
              const targetResponseId = entry.relationships?.[0]?.target_response_id;
              const targetOpinion = targetResponseId
                ? opinionEntries.find((o) => o.response_id === targetResponseId)
                : null;
              const targetName = targetOpinion
                ? getModelDisplayName(targetOpinion.model_name)
                : "unknown";
              return (
                <div key={entry.response_id}>
                  {/* Critique arrow indicator */}
                  <div className="flex items-center gap-2 text-xs text-gray-500 mb-1.5 ml-1">
                    <Badge variant="outline" className="text-[10px] font-medium bg-amber-50 text-amber-700 border-amber-200">
                      {getModelDisplayName(entry.model_name)}
                    </Badge>
                    <ArrowRight className="h-3 w-3 text-amber-400" />
                    <Badge variant="outline" className="text-[10px] font-medium bg-gray-50 text-gray-600 border-gray-200">
                      {targetName}
                    </Badge>
                  </div>
                  <ResponseCard
                    entry={entry}
                    accentColor="border-l-amber-500"
                    icon={<Shield className="h-4 w-4 text-amber-500" />}
                  />
                </div>
              );
            })
          )}
        </PhaseSection>

        {/* ── Phase 3: Revisions ── */}
        <PhaseSection
          id="phase-revision"
          title="Revisions"
          subtitle="How positions evolved after receiving critiques"
          icon={<RefreshCw className="h-5 w-5 text-orange-500" />}
        >
          {revisionEntries.length === 0 ? (
            <p className="text-sm text-gray-400 py-4 text-center">No revisions recorded.</p>
          ) : (
            <div className="space-y-4">
              {opinionEntries.map((opinionEntry) => {
                const revision = revisionMap[opinionEntry.response_id];
                if (!revision) return null;
                return (
                  <div key={revision.response_id} className="space-y-2">
                    <div className="flex items-center gap-2 text-xs text-gray-500 ml-1">
                      <Badge variant="outline" className="text-[10px] font-medium bg-orange-50 text-orange-700 border-orange-200">
                        {getModelDisplayName(opinionEntry.model_name)}
                      </Badge>
                      <ArrowRight className="h-3 w-3 text-orange-400" />
                      <span className="text-gray-400">revised position</span>
                    </div>
                    <ResponseCard
                      entry={revision}
                      accentColor="border-l-orange-500"
                      icon={<RefreshCw className="h-4 w-4 text-orange-500" />}
                    />
                    {/* Mini comparison: original confidence → revised confidence */}
                    {opinionEntry.confidence_score !== null && revision.confidence_score !== null && (
                      <div className="flex items-center gap-2 pl-4 text-xs text-gray-400">
                        <span>Confidence: {opinionEntry.confidence_score.toFixed(0)}%</span>
                        <ArrowRight className="h-3 w-3" />
                        <span className={revision.confidence_score >= opinionEntry.confidence_score ? "text-green-600" : "text-red-600"}>
                          {revision.confidence_score.toFixed(0)}%
                          <span className="text-gray-400 ml-1">
                            ({revision.confidence_score - opinionEntry.confidence_score >= 0 ? "+" : ""}
                            {(revision.confidence_score - opinionEntry.confidence_score).toFixed(0)})
                          </span>
                        </span>
                      </div>
                    )}
                  </div>
                );
              })}
              {/* Show any revisions that don't match an opinion */}
              {revisionEntries
                .filter((r) => !r.relationships?.[0]?.target_response_id)
                .map((entry) => (
                  <ResponseCard
                    key={entry.response_id}
                    entry={entry}
                    accentColor="border-l-orange-500"
                    icon={<RefreshCw className="h-4 w-4 text-orange-500" />}
                  />
                ))}
            </div>
          )}
        </PhaseSection>

        {/* ── Phase 4: Consensus ── */}
        <PhaseSection
          id="phase-consensus"
          title="Consensus"
          subtitle="Shared conclusions and remaining disagreements"
          icon={<GitMerge className="h-5 w-5 text-cyan-500" />}
        >
          {transcript.consensus ? (
            <ConsensusSummary consensus={transcript.consensus} />
          ) : (
            <p className="text-sm text-gray-400 py-4 text-center">No consensus available.</p>
          )}
        </PhaseSection>

        {/* ── Phase 5: Evaluation ── */}
        <PhaseSection
          id="phase-evaluation"
          title="Evaluation"
          subtitle="Behavioral metrics and analysis"
          icon={<BarChart3 className="h-5 w-5 text-emerald-500" />}
        >
          {transcript.metrics ? (
            <EvaluationSummary metrics={transcript.metrics} modelNameMap={modelNameMap} />
          ) : (
            <p className="text-sm text-gray-400 py-4 text-center">No evaluation data available.</p>
          )}
        </PhaseSection>
      </div>

      {/* Footer nav */}
      <div className="flex items-center justify-between pt-4 border-t border-gray-200">
        <Link href={`/debates/${debateId}`}>
          <Button variant="outline" size="sm" className="gap-1.5">
            <ArrowLeft className="h-4 w-4" />
            Debate Details
          </Button>
        </Link>
        <Link href={`/debates/${debateId}/metrics`}>
          <Button variant="outline" size="sm" className="gap-1.5">
            <BarChart3 className="h-4 w-4" />
            Detailed Metrics
          </Button>
        </Link>
      </div>
    </div>
  );
}
