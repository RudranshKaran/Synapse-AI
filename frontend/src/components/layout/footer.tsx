import Link from "next/link";
import { Brain } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-t border-border py-8 mt-12">
      <div className="mx-auto max-w-6xl px-4">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Brain className="h-4 w-4 text-violet-500" />
            <span>Synapse AI</span>
            <span className="text-border">|</span>
            <span>Multi-LLM Consensus &amp; Evaluation Platform</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <Link href="/debates" className="hover:text-foreground transition-colors">
              Debates
            </Link>
            <Link href="/debates/new" className="hover:text-foreground transition-colors">
              New Debate
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-foreground transition-colors"
            >
              GitHub
            </a>
          </div>
        </div>
        <p className="text-[10px] text-muted-foreground text-center mt-4 opacity-60">
          Built for studying reasoning convergence, persuasion dynamics, and consensus formation across AI systems.
        </p>
      </div>
    </footer>
  );
}
