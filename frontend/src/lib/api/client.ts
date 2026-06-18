const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export class ApiClientError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const body = await res.json();
      if (body?.detail) detail = body.detail;
      else if (body?.error?.message) detail = body.error.message;
    } catch {}
    throw new ApiClientError(res.status, `HTTP_${res.status}`, detail);
  }
  return res.json() as Promise<T>;
}

function buildUrl(path: string, params?: Record<string, string | number | undefined>): string {
  const url = new URL(`${API_BASE}${path}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        url.searchParams.set(key, String(value));
      }
    });
  }
  return url.toString();
}

export const api = {
  // ── Debates ─────────────────────────────────────────────
  listDebates: <T>(params?: Record<string, string | number | undefined>) =>
    fetch(buildUrl("/debates", params)).then(handleResponse<T>),

  getDebate: <T>(id: string) =>
    fetch(buildUrl(`/debates/${id}`)).then(handleResponse<T>),

  createDebate: <T>(body: unknown) =>
    fetch(`${API_BASE}/debates`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse<T>),

  runDebate: <T>(id: string, body: unknown) =>
    fetch(`${API_BASE}/debates/${id}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }).then(handleResponse<T>),

  getTranscript: <T>(id: string) =>
    fetch(buildUrl(`/debates/${id}/transcript`)).then(handleResponse<T>),

  getMetrics: <T>(id: string) =>
    fetch(buildUrl(`/debates/${id}/metrics`)).then(handleResponse<T>),
};
