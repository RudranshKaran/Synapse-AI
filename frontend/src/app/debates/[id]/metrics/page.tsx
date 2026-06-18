"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { GaugeChart } from "@/components/charts/gauge-chart";
import { DriftChart } from "@/components/charts/drift-chart";
import { ShiftChart } from "@/components/charts/shift-chart";
import { useDebate, useMetrics } from "@/lib/api/hooks";
import { formatDate } from "@/lib/utils";

export default function MetricsPage() {
  const params = useParams();
  const router = useRouter();
  const debateId = params.id as string;
  const { data: debate, isLoading: debateLoading } = useDebate(debateId);
  const { data: metrics, isLoading: metricsLoading, isError } = useMetrics(debateId);

  const isLoading = debateLoading || metricsLoading;

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <Skeleton className="h-6 w-32" />
        <Skeleton className="h-8 w-3/4" />
        <div className="grid md:grid-cols-3 gap-4 mt-6">
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
          <Skeleton className="h-48" />
        </div>
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (isError || !metrics) {
    return (
      <div className="max-w-4xl mx-auto text-center py-12 space-y-4">
        <p className="text-destructive">Failed to load metrics.</p>
        <p className="text-sm text-muted-foreground">The debate may not have been run yet.</p>
        <div className="flex gap-2 justify-center">
          <Button variant="outline" onClick={() => router.push(`/debates/${debateId}/transcript`)}>
            View Transcript
          </Button>
          <Button variant="outline" onClick={() => router.push("/debates")}>
            Back to Debates
          </Button>
        </div>
      </div>
    );
  }

  const driftValues = Object.values(metrics.opinion_drifts);
  const shiftValues = Object.values(metrics.confidence_shifts);
  const avgDrift = driftValues.length ? driftValues.reduce((a, b) => a + b, 0) / driftValues.length : 0;
  const avgShift = shiftValues.length ? shiftValues.reduce((a, b) => a + b, 0) / shiftValues.length : 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back link */}
      <Link
        href={`/debates/${debateId}`}
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to debate
      </Link>

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold leading-snug">{debate?.question || "Evaluation Metrics"}</h1>
        <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
          {debate && <StatusBadge status={debate.status} />}
          {debate?.created_at && <span>Created {formatDate(debate.created_at)}</span>}
          {debate?.completed_at && <span>Completed {formatDate(debate.completed_at)}</span>}
        </div>
      </div>

      {/* Overview cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-5 border-border flex flex-col items-center justify-center min-h-[180px]">
          <GaugeChart value={metrics.agreement_score ?? 0} label="Agreement Score" />
        </Card>
        <Card className="p-5 border-border flex flex-col items-center justify-center min-h-[180px]">
          <span className="text-3xl font-bold text-orange-500">{avgDrift.toFixed(4)}</span>
          <span className="text-xs text-muted-foreground mt-1 text-center">Average Opinion Drift</span>
          <span className="text-[10px] text-muted-foreground mt-1">0 = no change, 1 = complete reversal</span>
        </Card>
        <Card className="p-5 border-border flex flex-col items-center justify-center min-h-[180px]">
          <span className={`text-3xl font-bold ${avgShift >= 0 ? "text-green-500" : "text-red-500"}`}>
            {avgShift >= 0 ? "+" : ""}{avgShift.toFixed(1)}
          </span>
          <span className="text-xs text-muted-foreground mt-1 text-center">Average Confidence Shift</span>
          <span className="text-[10px] text-muted-foreground mt-1">Positive = more confident</span>
        </Card>
      </div>

      {/* Opinion Drift Chart */}
      {Object.keys(metrics.opinion_drifts).length > 0 && (
        <Card className="p-5 border-border">
          <h2 className="font-semibold text-base mb-1">Opinion Drift by Model</h2>
          <p className="text-xs text-muted-foreground mb-4">
            How much each model changed its position from initial opinion to final revision
          </p>
          <DriftChart data={metrics.opinion_drifts} />
        </Card>
      )}

      {/* Confidence Shift Chart */}
      {Object.keys(metrics.confidence_shifts).length > 0 && (
        <Card className="p-5 border-border">
          <h2 className="font-semibold text-base mb-1">Confidence Shift by Model</h2>
          <p className="text-xs text-muted-foreground mb-4">
            Change in confidence from initial opinion to final revised position
          </p>
          <ShiftChart data={metrics.confidence_shifts} />
        </Card>
      )}

      {/* Per-model breakdown table */}
      {Object.keys(metrics.opinion_drifts).length > 0 && (
        <Card className="p-5 border-border">
          <h2 className="font-semibold text-base mb-3">Per-Model Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-muted-foreground text-xs uppercase tracking-wide">
                  <th className="text-left py-2 px-2 font-medium">Model</th>
                  <th className="text-right py-2 px-2 font-medium">Opinion Drift</th>
                  <th className="text-right py-2 px-2 font-medium">Confidence Shift</th>
                  <th className="text-right py-2 px-2 font-medium">Initial Confidence</th>
                  <th className="text-right py-2 px-2 font-medium">Revised Confidence</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(metrics.opinion_drifts).map((key) => {
                  const drift = metrics.opinion_drifts[key];
                  const shift = metrics.confidence_shifts[key] ?? 0;
                  return (
                    <tr key={key} className="border-b border-border/50 hover:bg-muted/50 transition-colors">
                      <td className="py-2.5 px-2 font-medium">{key}</td>
                      <td className="py-2.5 px-2 text-right font-mono text-xs">{drift.toFixed(4)}</td>
                      <td className={`py-2.5 px-2 text-right font-mono text-xs ${shift >= 0 ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"}`}>
                        {shift >= 0 ? "+" : ""}{shift.toFixed(1)}
                      </td>
                      <td className="py-2.5 px-2 text-right text-muted-foreground">—</td>
                      <td className="py-2.5 px-2 text-right text-muted-foreground">—</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Nav footer */}
      <div className="flex items-center justify-between pt-4 border-t border-border">
        <Link href={`/debates/${debateId}`}>
          <Button variant="outline" size="sm" className="gap-1.5">
            <ArrowLeft className="h-4 w-4" />
            Debate Details
          </Button>
        </Link>
        <Link href={`/debates/${debateId}/transcript`}>
          <Button variant="outline" size="sm" className="gap-1.5">
            <BookOpen className="h-4 w-4" />
            Full Transcript
          </Button>
        </Link>
      </div>
    </div>
  );
}
