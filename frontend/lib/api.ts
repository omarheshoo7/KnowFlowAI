import {
  ChatResponse,
  HealthResponse,
  SearchResponse,
  UploadResponse,
} from "@/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function checkHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json() as Promise<HealthResponse>;
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/documents/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const error = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(error.detail ?? `Upload failed: ${res.status}`);
  }
  return res.json() as Promise<UploadResponse>;
}

export async function searchDocuments(
  query: string,
  topK: number = 5
): Promise<SearchResponse> {
  const res = await fetch(`${API_BASE}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, top_k: topK }),
  });
  if (!res.ok) {
    const error = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(error.detail ?? `Search failed: ${res.status}`);
  }
  return res.json() as Promise<SearchResponse>;
}

export async function chatWithDocuments(
  question: string,
  topK: number = 5
): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  });
  if (!res.ok) {
    const error = (await res.json().catch(() => ({}))) as { detail?: string };
    throw new Error(error.detail ?? `Chat failed: ${res.status}`);
  }
  return res.json() as Promise<ChatResponse>;
}
