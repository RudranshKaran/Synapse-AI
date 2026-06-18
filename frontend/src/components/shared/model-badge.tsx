import { Badge } from "@/components/ui/badge";
import { getModelDisplayName } from "@/lib/utils";

interface ModelBadgeProps {
  modelName: string;
  provider?: string;
}

const MODEL_COLORS: Record<string, string> = {
  "model-a": "bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-800",
  "model-b": "bg-green-50 dark:bg-green-950 text-green-700 dark:text-green-300 border-green-200 dark:border-green-800",
  "model-c": "bg-amber-50 dark:bg-amber-950 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800",
  "gpt-4o-mini": "bg-purple-50 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800",
  "gpt-4o": "bg-purple-50 dark:bg-purple-950 text-purple-700 dark:text-purple-300 border-purple-200 dark:border-purple-800",
};

export function ModelBadge({ modelName, provider }: ModelBadgeProps) {
  const color = MODEL_COLORS[modelName] || "bg-muted text-muted-foreground border-border";
  return (
    <Badge variant="outline" className={`font-medium ${color}`}>
      {getModelDisplayName(modelName)}
      {provider && provider !== "mock" && (
        <span className="ml-1 opacity-60 text-[10px]">({provider})</span>
      )}
    </Badge>
  );
}
