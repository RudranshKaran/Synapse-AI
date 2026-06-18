"use client";

import { Card } from "@/components/ui/card";
import { CheckCircle2, AlertCircle, FileText } from "lucide-react";
import { GaugeChart } from "@/components/charts/gauge-chart";
import type { TranscriptConsensus } from "@/lib/api/types";

interface ConsensusSummaryProps {
  consensus: TranscriptConsensus;
}

export function ConsensusSummary({ consensus }: ConsensusSummaryProps) {
  const score = consensus.consensus_score ?? 0;

  return (
    <div className="space-y-4">
      {/* Gauge */}
      <div className="flex justify-center py-2">
        <GaugeChart value={score} label="Consensus Score" />
      </div>

      {/* Summary */}
      {consensus.summary && (
        <Card className="p-4 border-border bg-muted/50">
          <div className="flex gap-2">
            <FileText className="h-4 w-4 text-muted-foreground shrink-0 mt-0.5" />
            <p className="text-sm text-foreground/80 leading-relaxed">{consensus.summary}</p>
          </div>
        </Card>
      )}

      <div className="grid md:grid-cols-2 gap-3">
        {/* Agreements */}
        {consensus.agreements.length > 0 && (
          <Card className="p-4 border-green-200 dark:border-green-900 bg-green-50/50 dark:bg-green-950/30">
            <h3 className="text-sm font-semibold text-green-700 dark:text-green-400 flex items-center gap-1.5 mb-2">
              <CheckCircle2 className="h-4 w-4" />
              Agreements
            </h3>
            <ul className="space-y-1.5">
              {consensus.agreements.map((item, i) => (
                <li key={i} className="text-sm text-green-800 dark:text-green-300 flex gap-2">
                  <span className="text-green-400 mt-0.5 shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}

        {/* Disagreements */}
        {consensus.disagreements.length > 0 && (
          <Card className="p-4 border-amber-200 dark:border-amber-900 bg-amber-50/50 dark:bg-amber-950/30">
            <h3 className="text-sm font-semibold text-amber-700 dark:text-amber-400 flex items-center gap-1.5 mb-2">
              <AlertCircle className="h-4 w-4" />
              Disagreements
            </h3>
            <ul className="space-y-1.5">
              {consensus.disagreements.map((item, i) => (
                <li key={i} className="text-sm text-amber-800 dark:text-amber-300 flex gap-2">
                  <span className="text-amber-400 mt-0.5 shrink-0">•</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </div>
    </div>
  );
}
