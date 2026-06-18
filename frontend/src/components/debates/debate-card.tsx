"use client";

import Link from "next/link";
import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { StatusBadge } from "@/components/shared/status-badge";
import { formatRelativeTime, truncate } from "@/lib/utils";
import type { DebateListItem } from "@/lib/api/types";

interface DebateCardProps {
  debate: DebateListItem;
}

export function DebateCard({ debate }: DebateCardProps) {
  return (
    <Link href={`/debates/${debate.debate_id}`}>
      <Card className="p-4 hover:shadow-md hover:shadow-black/5 dark:hover:shadow-black/20 transition-all cursor-pointer border-border h-full">
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-semibold text-sm leading-snug flex-1 min-w-0">
            {truncate(debate.question, 120)}
          </h3>
          <StatusBadge status={debate.status} />
        </div>
        <div className="flex items-center gap-4 text-xs text-muted-foreground mt-3">
          <span>{debate.participant_count} participant{debate.participant_count !== 1 ? "s" : ""}</span>
          <span>{formatRelativeTime(debate.created_at)}</span>
          {debate.agreement_score !== null && (
            <span className="font-medium text-foreground/70">
              Score: {debate.agreement_score.toFixed(1)}
            </span>
          )}
        </div>
      </Card>
    </Link>
  );
}

export function DebateCardSkeleton() {
  return (
    <Card className="p-4 border-border">
      <Skeleton className="h-4 w-3/4 mb-3" />
      <Skeleton className="h-3 w-1/2" />
    </Card>
  );
}
