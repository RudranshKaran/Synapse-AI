"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./client";
import type {
  CreateDebateRequest,
  DebateListParams,
  DebateListResponse,
  DebateResponse,
  MetricsResponse,
  RunDebateRequest,
  RunDebateResponse,
  Transcript,
} from "./types";

// ── Keys ──────────────────────────────────────────────────

export const debateKeys = {
  all: ["debates"] as const,
  list: (params: DebateListParams) => ["debates", "list", params] as const,
  detail: (id: string) => ["debates", "detail", id] as const,
  transcript: (id: string) => ["transcript", id] as const,
  metrics: (id: string) => ["metrics", id] as const,
};

// ── Hooks ─────────────────────────────────────────────────

export function useDebateList(params: DebateListParams) {
  return useQuery({
    queryKey: debateKeys.list(params),
    queryFn: () =>
      api.listDebates<DebateListResponse>({
        page: params.page,
        page_size: params.page_size,
        status: params.status,
        search: params.search,
      }),
    staleTime: 30_000,
  });
}

export function useDebate(id: string) {
  return useQuery({
    queryKey: debateKeys.detail(id),
    queryFn: () => api.getDebate<DebateResponse>(id),
    staleTime: 30_000,
    enabled: !!id,
  });
}

export function useTranscript(id: string) {
  return useQuery({
    queryKey: debateKeys.transcript(id),
    queryFn: () => api.getTranscript<Transcript>(id),
    staleTime: Infinity,
    enabled: !!id,
  });
}

export function useMetrics(id: string) {
  return useQuery({
    queryKey: debateKeys.metrics(id),
    queryFn: () => api.getMetrics<MetricsResponse>(id),
    staleTime: Infinity,
    enabled: !!id,
  });
}

export function useCreateDebate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateDebateRequest) =>
      api.createDebate<DebateResponse>(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: debateKeys.all });
    },
  });
}

export function useRunDebate() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: RunDebateRequest }) =>
      api.runDebate<RunDebateResponse>(id, data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: debateKeys.all });
      queryClient.invalidateQueries({ queryKey: debateKeys.detail(result.debate_id) });
      queryClient.invalidateQueries({ queryKey: debateKeys.transcript(result.debate_id) });
      queryClient.invalidateQueries({ queryKey: debateKeys.metrics(result.debate_id) });
    },
  });
}
