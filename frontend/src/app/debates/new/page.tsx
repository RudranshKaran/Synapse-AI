"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Sparkles, Loader2 } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useCreateDebate } from "@/lib/api/hooks";
import { toast } from "sonner";

const AVAILABLE_MODELS = [
  { value: "model-a", label: "Model A", provider: "mock" },
  { value: "model-b", label: "Model B", provider: "mock" },
  { value: "model-c", label: "Model C", provider: "mock" },
  { value: "gpt-4o-mini", label: "GPT-4o Mini", provider: "openai" },
  { value: "gpt-4o", label: "GPT-4o", provider: "openai" },
];

export default function NewDebatePage() {
  const router = useRouter();
  const createDebate = useCreateDebate();

  const [question, setQuestion] = useState("");
  const [selectedModels, setSelectedModels] = useState<string[]>(["model-a", "model-b", "model-c"]);
  const [provider, setProvider] = useState<"mock" | "openai">("mock");
  const [errors, setErrors] = useState<Record<string, string>>({});

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
        provider,
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
      {/* Back link */}
      <Link
        href="/debates"
        className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft className="h-4 w-4" />
        Back to debates
      </Link>

      <div>
        <h1 className="text-2xl font-bold">Create a Debate</h1>
        <p className="text-sm text-gray-500 mt-1">
          Submit a question for AI models to discuss and analyze.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Question */}
        <Card className="p-5 border-gray-200 space-y-3">
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
            className={errors.question ? "border-red-400" : ""}
          />
          <div className="flex items-center justify-between text-xs">
            <span className={errors.question ? "text-red-500" : "text-gray-400"}>
              {errors.question || ""}
            </span>
            <span className="text-gray-400">{question.length} / 5000</span>
          </div>
        </Card>

        {/* Models */}
        <Card className="p-5 border-gray-200 space-y-3">
          <Label className="font-semibold">Models</Label>
          <p className="text-xs text-gray-500">Select which AI models will participate.</p>
          <div className="flex flex-wrap gap-2">
            {AVAILABLE_MODELS.map((model) => {
              const isSelected = selectedModels.includes(model.value);
              return (
                <button
                  key={model.value}
                  type="button"
                  onClick={() => toggleModel(model.value)}
                  className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
                    isSelected
                      ? "bg-violet-100 text-violet-700 border-violet-300"
                      : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
                  }`}
                >
                  {model.label}
                  {model.provider !== "mock" && (
                    <span className="ml-1 text-[10px] opacity-60">({model.provider})</span>
                  )}
                </button>
              );
            })}
          </div>
          {errors.models && <p className="text-xs text-red-500">{errors.models}</p>}
        </Card>

        {/* Provider */}
        <Card className="p-5 border-gray-200 space-y-3">
          <Label className="font-semibold">Provider</Label>
          <p className="text-xs text-gray-500">
            Mock providers respond instantly for testing. OpenAI uses real LLM calls (requires API key).
          </p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setProvider("mock")}
              className={`flex-1 px-4 py-3 rounded-lg border text-sm font-medium text-left transition-colors ${
                provider === "mock"
                  ? "bg-violet-100 text-violet-700 border-violet-300"
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="font-semibold">Mock</div>
              <div className="text-xs opacity-70 mt-0.5">Fast, for testing</div>
            </button>
            <button
              type="button"
              onClick={() => setProvider("openai")}
              className={`flex-1 px-4 py-3 rounded-lg border text-sm font-medium text-left transition-colors ${
                provider === "openai"
                  ? "bg-violet-100 text-violet-700 border-violet-300"
                  : "bg-white text-gray-600 border-gray-200 hover:border-gray-300"
              }`}
            >
              <div className="font-semibold">OpenAI</div>
              <div className="text-xs opacity-70 mt-0.5">Real LLM responses</div>
            </button>
          </div>
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
