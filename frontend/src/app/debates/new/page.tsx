"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Sparkles, Loader2, Info } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useCreateDebate } from "@/lib/api/hooks";
import { toast } from "sonner";

const AVAILABLE_MODELS = [
  { value: "agent-a", label: "Agent A — Balanced Analyst", subtitle: "Gemini 2.5 Flash" },
  { value: "agent-b", label: "Agent B — Critical Reviewer", subtitle: "Llama 3.1 via Groq" },
  { value: "agent-c", label: "Agent C — Devil's Advocate", subtitle: "DeepSeek R1 via OpenRouter" },
];

const TEST_MODELS = [
  { value: "model-a", label: "Model A (Mock)" },
  { value: "model-b", label: "Model B (Mock)" },
  { value: "model-c", label: "Model C (Mock)" },
];

export default function NewDebatePage() {
  const router = useRouter();
  const createDebate = useCreateDebate();

  const [question, setQuestion] = useState("");
  const [selectedModels, setSelectedModels] = useState<string[]>(["agent-a", "agent-b", "agent-c"]);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [showTesting, setShowTesting] = useState(false);

  function toggleModel(model: string) {
    setSelectedModels((prev) =>
      prev.includes(model) ? prev.filter((m) => m !== model) : [...prev, model],
    );
    setErrors((prev) => ({ ...prev, models: "" }));
  }

  function validate(): boolean {
    const newErrors: Record<string, string> = {};
    if (!question.trim()) newErrors.question = "Question is required.";
    else if (question.trim().length < 10) newErrors.question = "Question must be at least 10 characters.";
    else if (question.length > 5000) newErrors.question = "Question must be under 5000 characters.";
    if (selectedModels.length === 0) newErrors.models = "Select at least one model.";
    if (selectedModels.length > 10) newErrors.models = "Maximum 10 models allowed.";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validate()) return;

    try {
      const result = await createDebate.mutateAsync({
        question: question.trim(),
        models: selectedModels,
      });
      toast.success("Debate created successfully");
      router.push(`/debates/${result.debate_id}`);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to create debate.";
      toast.error(message);
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link
        href="/debates"
        className="inline-flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to debates
      </Link>

      <div>
        <h1 className="text-2xl font-bold">Create a Debate</h1>
        <p className="text-sm text-muted-foreground mt-1">
          Submit a question for AI agents to discuss, critique, and reach consensus.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Question */}
        <Card className="p-5 border-border space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="h-4 w-4 text-violet-500" />
            <Label htmlFor="question" className="font-semibold">Question</Label>
          </div>
          <Textarea
            id="question"
            placeholder="e.g. Should AI-generated code be deployed directly to production?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={4}
            className={errors.question ? "border-destructive" : ""}
          />
          <div className="flex items-center justify-between text-xs">
            <span className={errors.question ? "text-destructive" : "text-muted-foreground"}>
              {errors.question || "Enter a debate question for the AI agents."}
            </span>
            <span className="text-muted-foreground">{question.length} / 5000</span>
          </div>
        </Card>

        {/* Agent Models */}
        <Card className="p-5 border-border space-y-3">
          <Label className="font-semibold">Synapse AI Agents</Label>
          <p className="text-xs text-muted-foreground">
            Select which AI agents will participate. Each uses a different model with a distinct reasoning style.
          </p>
          <div className="space-y-2">
            {AVAILABLE_MODELS.map((model) => {
              const isSelected = selectedModels.includes(model.value);
              return (
                <button
                  key={model.value}
                  type="button"
                  onClick={() => toggleModel(model.value)}
                  className={`w-full flex items-center justify-between px-4 py-3 rounded-lg border text-sm text-left transition-colors ${
                    isSelected
                      ? "bg-violet-50 dark:bg-violet-950/50 text-violet-700 dark:text-violet-300 border-violet-300 dark:border-violet-700"
                      : "bg-background text-foreground border-border hover:border-violet-300 dark:hover:border-violet-700"
                  }`}
                >
                  <div>
                    <div className="font-medium">{model.label}</div>
                    <div className="text-xs opacity-70">{model.subtitle}</div>
                  </div>
                  <div
                    className={`shrink-0 w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors ${
                      isSelected
                        ? "bg-violet-600 border-violet-600"
                        : "border-muted-foreground"
                    }`}
                  >
                    {isSelected && (
                      <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                      </svg>
                    )}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Toggle test models */}
          <button
            type="button"
            onClick={() => setShowTesting(!showTesting)}
            className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors pt-1"
          >
            <Info className="h-3 w-3" />
            {showTesting ? "Hide" : "Show"} testing models
          </button>

          {showTesting && (
            <div className="flex flex-wrap gap-2 pt-1">
              {TEST_MODELS.map((model) => {
                const isSelected = selectedModels.includes(model.value);
                return (
                  <button
                    key={model.value}
                    type="button"
                    onClick={() => toggleModel(model.value)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                      isSelected
                        ? "bg-amber-100 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300 border-amber-300 dark:border-amber-700"
                        : "bg-muted text-muted-foreground border-border hover:border-amber-300"
                    }`}
                  >
                    {model.label}
                  </button>
                );
              })}
            </div>
          )}

          {errors.models && <p className="text-xs text-destructive">{errors.models}</p>}
        </Card>

        {/* Submit */}
        <div className="flex items-center gap-3 pt-2">
          <Button type="submit" disabled={createDebate.isPending} className="gap-2">
            {createDebate.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4" />
            )}
            {createDebate.isPending ? "Creating..." : "Create Debate"}
          </Button>
          <Link href="/debates">
            <Button type="button" variant="outline">Cancel</Button>
          </Link>
        </div>
      </form>
    </div>
  );
}
