"use client";

import { Suspense, useCallback, useMemo } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { Plus, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card } from "@/components/ui/card";
import { DebateCard, DebateCardSkeleton } from "@/components/debates/debate-card";
import { useDebateList } from "@/lib/api/hooks";
import { STATUS_LABELS } from "@/lib/api/types";

const PAGE_SIZES = [10, 20, 50];
const STATUS_OPTIONS = [
  { value: "", label: "All Statuses" },
  ...Object.entries(STATUS_LABELS).map(([value, label]) => ({ value, label })),
];

function DebatesContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "20", 10);
  const status: string = searchParams.get("status") || "";
  const search: string = searchParams.get("search") || "";

  const { data, isLoading, isError } = useDebateList({
    page,
    page_size: pageSize,
    status: status || undefined,
    search: search || undefined,
  });

  const totalPages = data ? Math.ceil(data.total / data.page_size) : 0;

  const updateParam = useCallback(
    (key: string, value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value) params.set(key, value);
      else params.delete(key);
      if (key !== "page") params.set("page", "1");
      router.push(`/debates?${params.toString()}`);
    },
    [router, searchParams],
  );

  const handleSearch = useCallback(
    (value: string) => {
      const params = new URLSearchParams(searchParams.toString());
      if (value) params.set("search", value);
      else params.delete("search");
      params.set("page", "1");
      router.push(`/debates?${params.toString()}`);
    },
    [router, searchParams],
  );

  const pageNumbers = useMemo(() => {
    const pages: number[] = [];
    const start = Math.max(1, page - 2);
    const end = Math.min(totalPages, page + 2);
    for (let i = start; i <= end; i++) pages.push(i);
    return pages;
  }, [page, totalPages]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Debates</h1>
          <p className="text-sm text-gray-500 mt-1">
            {data ? `${data.total} debate${data.total !== 1 ? "s" : ""} total` : "Loading..."}
          </p>
        </div>
        <Link href="/debates/new">
          <Button className="gap-1.5">
            <Plus className="h-4 w-4" />
            New Debate
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search debates..."
            defaultValue={search}
            onChange={(e) => {
              const timer = setTimeout(() => handleSearch(e.target.value), 300);
              return () => clearTimeout(timer);
            }}
            className="pl-9"
          />
        </div>
        <Select value={status} onValueChange={(v) => updateParam("status", v ?? "")}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((opt) => (
              <SelectItem key={opt.value} value={opt.value}>{opt.label}</SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select
          value={String(pageSize)}
          onValueChange={(v) => updateParam("page_size", v ?? "")}
        >
          <SelectTrigger className="w-[130px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PAGE_SIZES.map((s) => (
              <SelectItem key={s} value={String(s)}>{s} per page</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => <DebateCardSkeleton key={i} />)}
        </div>
      ) : isError ? (
        <Card className="p-8 text-center border-gray-200">
          <p className="text-red-600 mb-2">Failed to load debates.</p>
          <Button variant="outline" onClick={() => window.location.reload()}>
            Retry
          </Button>
        </Card>
      ) : data && data.debates.length === 0 ? (
        <Card className="p-8 text-center border-gray-200">
          <p className="text-gray-500 mb-1">No debates found.</p>
          {search || status ? (
            <p className="text-sm text-gray-400">Try adjusting your search or filters.</p>
          ) : (
            <Link href="/debates/new">
              <Button variant="outline" size="sm" className="mt-2 gap-1.5">
                <Plus className="h-4 w-4" />
                Create the first debate
              </Button>
            </Link>
          )}
        </Card>
      ) : (
        <div className="space-y-3">
          {data?.debates.map((d) => <DebateCard key={d.debate_id} debate={d} />)}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => updateParam("page", String(page - 1))}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          {pageNumbers.map((p) => (
            <Button
              key={p}
              variant={p === page ? "default" : "outline"}
              size="sm"
              onClick={() => updateParam("page", String(p))}
              className="min-w-[36px]"
            >
              {p}
            </Button>
          ))}
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => updateParam("page", String(page + 1))}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      )}
    </div>
  );
}

export default function DebatesPage() {
  return (
    <Suspense fallback={
      <div className="space-y-3">
        {Array.from({ length: 5 }).map((_, i) => <DebateCardSkeleton key={i} />)}
      </div>
    }>
      <DebatesContent />
    </Suspense>
  );
}
