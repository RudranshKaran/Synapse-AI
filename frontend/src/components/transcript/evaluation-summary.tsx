"use client";

import { Card } from "@/components/ui/card";
import { GaugeChart } from "@/components/charts/gauge-chart";
import { DriftChart } from "@/components/charts/drift-chart";
import { ShiftChart } from "@/components/charts/shift-chart";
import type { TranscriptMetricsInfo } from "@/lib/api/types";

interface EvaluationSummaryProps {
  metrics: TranscriptMetricsInfo;
  modelNameMap: Record<string, string>;
}

export function EvaluationSummary({ metrics }: EvaluationSummaryProps) {
  const hasDrifts = Object.keys(metrics.opinion_drifts).length > 0;
  const hasShifts = Object.keys(metrics.confidence_shifts).length > 0;

  return (
    <div className="space-y-4">
      {/* Agreement Score */}
      {metrics.agreement_score !== null && (
        <div className="flex justify-center py-2">
          <GaugeChart value={metrics.agreement_score} label="Agreement Score" />
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {hasDrifts && (
          <Card className="p-4 border-border">
            <h3 className="text-sm font-semibold mb-3">Opinion Drift</h3>
            <p className="text-xs text-muted-foreground mb-3">
              How much each model changed its position (0 = no change, 1 = complete reversal)
            </p>
            <DriftChart data={metrics.opinion_drifts} height={200} />
          </Card>
        )}
        {hasShifts && (
          <Card className="p-4 border-border">
            <h3 className="text-sm font-semibold mb-3">Confidence Shift</h3>
            <p className="text-xs text-muted-foreground mb-3">
              Change in confidence from initial opinion to final revision
            </p>
            <ShiftChart data={metrics.confidence_shifts} height={200} />
          </Card>
        )}
      </div>
    </div>
  );
}
