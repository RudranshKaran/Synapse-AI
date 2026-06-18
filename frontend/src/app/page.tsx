"use client";

import Link from "next/link";
import { ArrowRight, Brain, FlaskConical, BarChart3, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { DebateCard, DebateCardSkeleton } from "@/components/debates/debate-card";
import { useDebateList } from "@/lib/api/hooks";

export default function HomePage() {
  const { data, isLoading } = useDebateList({ page: 1, page_size: 5 });

  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center py-12 space-y-4">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-violet-100 mb-2">
          <Brain className="h-6 w-6 text-violet-600" />
        </div>
        <h1 className="text-4xl font-bold tracking-tight">Synapse AI</h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed">
          A platform for studying how AI systems reason, disagree, influence one another,
          and converge toward shared conclusions through structured debate.
        </p>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Link href="/debates/new">
            <Button size="lg" className="gap-2">
              <Plus className="h-5 w-5" />
              Create Debate
            </Button>
          </Link>
          <Link href="/debates">
            <Button size="lg" variant="outline" className="gap-2">
              Browse Debates
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* How it works */}
      <section className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
        <Card className="p-6 text-center space-y-2 border-gray-200">
          <FlaskConical className="h-8 w-8 mx-auto text-violet-500" />
          <h3 className="font-semibold">1. Ask a Question</h3>
          <p className="text-sm text-gray-600">Submit a question for AI models to debate.</p>
        </Card>
        <Card className="p-6 text-center space-y-2 border-gray-200">
          <Brain className="h-8 w-8 mx-auto text-violet-500" />
          <h3 className="font-semibold">2. Models Debate</h3>
          <p className="text-sm text-gray-600">Models generate opinions, critique each other, and revise positions.</p>
        </Card>
        <Card className="p-6 text-center space-y-2 border-gray-200">
          <BarChart3 className="h-8 w-8 mx-auto text-violet-500" />
          <h3 className="font-semibold">3. Measure Consensus</h3>
          <p className="text-sm text-gray-600">Evaluate agreement, opinion drift, and confidence shifts.</p>
        </Card>
      </section>

      {/* Recent debates */}
      <section className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Recent Debates</h2>
          <Link href="/debates" className="text-sm text-violet-600 hover:text-violet-700 font-medium">
            View all
          </Link>
        </div>
        <div className="space-y-3">
          {isLoading ? (
            <>
              <DebateCardSkeleton />
              <DebateCardSkeleton />
              <DebateCardSkeleton />
            </>
          ) : data?.debates.length ? (
            data.debates.slice(0, 5).map((d) => <DebateCard key={d.debate_id} debate={d} />)
          ) : (
            <Card className="p-8 text-center border-gray-200">
              <p className="text-gray-500 mb-3">No debates yet.</p>
              <Link href="/debates/new">
                <Button variant="outline" size="sm" className="gap-1.5">
                  <Plus className="h-4 w-4" />
                  Create the first debate
                </Button>
              </Link>
            </Card>
          )}
        </div>
      </section>
    </div>
  );
}
