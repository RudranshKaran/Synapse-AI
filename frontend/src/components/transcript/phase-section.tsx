"use client";

import { ChevronDown, ChevronRight } from "lucide-react";
import { useState } from "react";

interface PhaseSectionProps {
  id: string;
  title: string;
  subtitle?: string;
  icon: React.ReactNode;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

export function PhaseSection({
  id,
  title,
  subtitle,
  icon,
  defaultOpen = true,
  children,
}: PhaseSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <section id={id} className="scroll-mt-20">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center gap-3 py-3 px-4 rounded-lg hover:bg-muted transition-colors text-left"
      >
        <span className="shrink-0">{icon}</span>
        <div className="flex-1 min-w-0">
          <h2 className="font-semibold text-base">{title}</h2>
          {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        </div>
        <span className="shrink-0 text-muted-foreground">
          {open ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
        </span>
      </button>
      {open && <div className="pl-4 pr-4 pb-4 space-y-3 mt-2">{children}</div>}
    </section>
  );
}
