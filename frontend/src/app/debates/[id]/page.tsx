"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Loader2,
  Play,
  BarChart3,
  CheckCircle2,
  Clock,
  BookOpen,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { ModelBadge } from "@/components/shared/model-badge";
import { useDebate, useRunDebate } from "@/lib/api/hooks";
import { formatDate } from "@/lib/utils";
import { toast } from "sonner";

const PHASE_LABELS: Record<string, string> = {
  opinion: "Opinion Generation",
  critique: "Critique Phase",
  revision: "Revision Phase",
  consensus: "Consensus Generation",
  evaluation: "Evaluation",
};

const PHASE_ORDER = ["opinion", "critique", "revision", "consensus", "evaluation"];

export default function DebateDetailPage() {
  const params = useParams();
  const router = useRouter();
  const debateId = params.id as string;
  const { data: debate, isLoading, isError } = useDebate(debateId);
  const runDebate = useRunDebate();
  const [isRunning, setIsRunning] = useState(false);
  const [currentPhase, setCurrentPhase] = useState(0);

  async function handleRun() {
    setIsRunning(true);
    setCurrentPhase(0);

    // Animate through phases while the request is in-flight
    const phaseInterval = setInterval(() => {
      setCurrentPhase((p) => Math.min(p + 1, PHASE_ORDER.length - 1));
    }, 1200);

    try {
      await runDebate.mutateAsync({ id: debateId, data: { rounds: 1 } });
      clearInterval(phaseInterval);
      setCurrentPhase(PHASE_ORDER.length);
      toast.success("Debate completed successfully");
      router.refresh();
    } catch (err: unknown) {
      clearInterval(phaseInterval);
      const message = err instanceof Error ? err.message : "Failed to run debate.";
      toast.error(message);
    } finally {
      setIsRunning(false);
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-3xl mx-auto">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-4 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }

  if (isError || !debate) {
    return (
      <div className="max-w-3xl mx-auto text-center py-12">
        <p className="text-red-600 mb-4">Failed to load debate.</p>
        <Button variant="outline" onClick={() => router.push("/debates")}>
          Back to debates
        </Button>
      </div>
    );
  }

  const isCompleted = debate.status === "evaluation_complete";
  const isRunnable = debate.status === "created";

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Back link */}
      <Link
        href="/debates"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to debates
      </Link>

      {/* Header */}
      <div>
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1 flex-1 min-w-0">
            <h1 className="text-xl font-bold leading-snug">{debate.question}</h1>
            <div className="flex items-center gap-3 text-sm text-muted-foreground">
              <StatusBadge status={debate.status} />
              <span>Created {formatDate(debate.created_at)}</span>
              {debate.completed_at && <span>Completed {formatDate(debate.completed_at)}</span>}
            </div>
          </div>
        </div>
      </div>

      {/* Participants */}
      <Card className="p-4 border-border">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
          Participants
        </h2>
        <div className="flex flex-wrap gap-2">
          {debate.participants.map((p) => (
            <ModelBadge key={p.participant_id} modelName={p.model_name} provider={p.provider} />
          ))}
        </div>
      </Card>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {isRunnable && !isRunning && (
          <Button onClick={handleRun} className="gap-2">
            <Play className="h-4 w-4" />
            Run Debate
          </Button>
        )}
        {isCompleted && (
          <>
            <Link href={`/debates/${debateId}/transcript`}>
              <Button className="gap-2">
                <BookOpen className="h-4 w-4" />
                View Transcript
              </Button>
            </Link>
            <Link href={`/debates/${debateId}/metrics`}>
              <Button variant="outline" className="gap-2">
                <BarChart3 className="h-4 w-4" />
                View Metrics
              </Button>
            </Link>
          </>
        )}
      </div>

      {/* Running state */}
      {isRunning && (
        <Card className="p-6 border-border">
          <div className="flex items-center gap-3 mb-4">
            <Loader2 className="h-5 w-5 animate-spin text-violet-600 dark:text-violet-400" />
            <span className="font-semibold">Running Debate...</span>
          </div>
          <div className="space-y-2">
            {PHASE_ORDER.map((phase, i) => {
              const isActive = i === currentPhase;
              const isDone = i < currentPhase;
              return (
                <div
                  key={phase}
                  className={`flex items-center gap-3 text-sm px-3 py-2 rounded-lg transition-colors ${
                    isActive ? "bg-violet-50 dark:bg-violet-950/50 text-violet-700 dark:text-violet-300 font-medium" : ""
                  } ${isDone ? "text-green-600 dark:text-green-400" : "text-muted-foreground"}`}
                >
                  {isDone ? (
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                  ) : isActive ? (
                    <Loader2 className="h-4 w-4 animate-spin shrink-0 text-violet-600 dark:text-violet-400" />
                  ) : (
                    <Clock className="h-4 w-4 shrink-0" />
                  )}
                  <span>{PHASE_LABELS[phase]}</span>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Pre-run state */}
      {!isCompleted && !isRunning && (
        <Card className="p-8 text-center border-border">
          <p className="text-muted-foreground">
            This debate hasn&apos;t been run yet. Click &quot;Run Debate&quot; to start the pipeline.
          </p>
        </Card>
      )}

      {/* Completed state */}
      {isCompleted && (
        <Card className="p-6 border-border">
          <div className="flex items-center gap-2 mb-4">
            <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            <h2 className="font-semibold">Debate Complete</h2>
          </div>
          <p className="text-sm text-muted-foreground">
            Explore the full debate transcript or view the evaluation metrics.
          </p>
          <div className="flex gap-2 mt-4">
            <Link href={`/debates/${debateId}/transcript`}>
              <Button size="sm" className="gap-1.5">
                <BookOpen className="h-4 w-4" />
                View Transcript
              </Button>
            </Link>
            <Link href={`/debates/${debateId}/metrics`}>
              <Button variant="outline" size="sm" className="gap-1.5">
                <BarChart3 className="h-4 w-4" />
                View Metrics
              </Button>
            </Link>
          </div>
        </Card>
      )}
    </div>
  );
}
