"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Brain, Plus, Moon, Sun, Menu, X } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useTheme } from "@/lib/theme-context";

export function Header() {
  const pathname = usePathname();
  const { theme, toggleTheme } = useTheme();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isActive = (path: string) => pathname.startsWith(path);

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold text-lg shrink-0">
          <Brain className="h-5 w-5 text-violet-600 dark:text-violet-400" />
          <span>Synapse AI</span>
        </Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          <Link
            href="/debates"
            className={`text-sm px-3 py-1.5 rounded-md transition-colors ${
              isActive("/debates")
                ? "bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 font-medium"
                : "text-muted-foreground hover:text-foreground hover:bg-muted"
            }`}
          >
            Debates
          </Link>
          <Link href="/debates/new">
            <Button size="sm" className="gap-1.5 ml-2">
              <Plus className="h-4 w-4" />
              New Debate
            </Button>
          </Link>
          <Button variant="ghost" size="icon" onClick={toggleTheme} className="ml-1" aria-label="Toggle theme">
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </nav>

        {/* Mobile menu button */}
        <div className="flex md:hidden items-center gap-1">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setMobileOpen(!mobileOpen)} aria-label="Menu">
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {/* Mobile nav */}
      {mobileOpen && (
        <div className="md:hidden border-t bg-background px-4 py-3 space-y-2">
          <Link
            href="/debates"
            onClick={() => setMobileOpen(false)}
            className={`block text-sm px-3 py-2 rounded-md ${
              isActive("/debates")
                ? "bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 font-medium"
                : "text-muted-foreground hover:text-foreground"
            }`}
          >
            Debates
          </Link>
          <Link
            href="/debates/new"
            onClick={() => setMobileOpen(false)}
            className="block"
          >
            <Button size="sm" className="w-full gap-1.5">
              <Plus className="h-4 w-4" />
              New Debate
            </Button>
          </Link>
        </div>
      )}
    </header>
  );
}
