import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function formatRelativeTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "";
  const now = Date.now();
  const then = new Date(dateStr).getTime();
  const diffSec = Math.floor((now - then) / 1000);
  if (diffSec < 60) return "just now";
  if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
  if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
  if (diffSec < 2592000) return `${Math.floor(diffSec / 86400)}d ago`;
  return formatDate(dateStr);
}

export function truncate(text: string, max: number): string {
  if (text.length <= max) return text;
  return text.slice(0, max).trimEnd() + "…";
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    created: "bg-gray-100 text-gray-700 border-gray-200",
    running: "bg-blue-100 text-blue-700 border-blue-200",
    opinions_generated: "bg-violet-100 text-violet-700 border-violet-200",
    critiques_generated: "bg-amber-100 text-amber-700 border-amber-200",
    revisions_generated: "bg-orange-100 text-orange-700 border-orange-200",
    consensus_reached: "bg-cyan-100 text-cyan-700 border-cyan-200",
    evaluation_complete: "bg-emerald-100 text-emerald-700 border-emerald-200",
  };
  return colors[status] || "bg-gray-100 text-gray-700 border-gray-200";
}

export function getStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    created: "Created",
    running: "Running",
    opinions_generated: "Opinions Ready",
    critiques_generated: "Critiques Ready",
    revisions_generated: "Revisions Ready",
    consensus_reached: "Consensus Reached",
    evaluation_complete: "Complete",
  };
  return labels[status] || status;
}

export function getModelDisplayName(name: string): string {
  const names: Record<string, string> = {
    "model-a": "Model A",
    "model-b": "Model B",
    "model-c": "Model C",
    "gpt-4o-mini": "GPT-4o Mini",
    "gpt-4o": "GPT-4o",
  };
  return names[name] || name;
}
