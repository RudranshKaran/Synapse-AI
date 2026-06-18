"use client";

import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { getModelDisplayName } from "@/lib/utils";
import type { TranscriptEntry } from "@/lib/api/types";

interface ResponseCardProps {
  entry: TranscriptEntry;
  icon?: React.ReactNode;
  accentColor?: string;
}

export function ResponseCard({ entry, icon, accentColor = "border-l-muted-foreground" }: ResponseCardProps) {
  return (
    <Card className={`border-l-4 ${accentColor} p-4 border-border`}>
      <div className="flex items-center gap-2 mb-2">
        {icon && <span className="shrink-0">{icon}</span>}
        <Badge variant="outline" className="font-medium text-xs bg-muted">
          {getModelDisplayName(entry.model_name)}
        </Badge>
        {entry.confidence_score !== null && (
          <span className="text-xs text-muted-foreground">
            Confidence: {entry.confidence_score.toFixed(0)}%
          </span>
        )}
      </div>
      <p className="text-sm leading-relaxed whitespace-pre-wrap text-foreground/90">{entry.content}</p>
    </Card>
  );
}
