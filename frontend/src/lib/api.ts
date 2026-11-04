/**
 * Reusable API client for DocuMind AI backend.
 *
 * All backend calls go through this module so the base URL
 * and error handling live in one place.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

/**
 * Thin wrapper around fetch that prefixes the backend URL
 * and converts non-OK responses into thrown errors.
 */
export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

// ─── Document types ──────────────────────────────────────

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  status: string;
  page_count: number | null;
  created_at: string;
}

// TODO: Wire up when backend document endpoints exist
export async function fetchDocuments(): Promise<Document[]> {
  // return apiFetch<Document[]>("/documents");
  throw new Error("NOT_IMPLEMENTED: GET /documents endpoint not available yet");
}

export async function uploadDocument(_file: File): Promise<Document> {
  // const form = new FormData();
  // form.append("file", file);
  // const url = `${API_BASE_URL}/documents/upload`;
  // const res = await fetch(url, { method: "POST", body: form });
  // if (!res.ok) throw new Error(await res.text());
  // return res.json();
  throw new Error("NOT_IMPLEMENTED: POST /documents/upload endpoint not available yet");
}

// ─── Chat types ──────────────────────────────────────────

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  sources?: { document: string; chunk: string }[];
}

// TODO: Wire up when backend chat endpoint exists
export async function sendChatMessage(_message: string): Promise<ChatMessage> {
  // return apiFetch<ChatMessage>("/chat", {
  //   method: "POST",
  //   body: JSON.stringify({ message }),
  // });
  throw new Error("NOT_IMPLEMENTED: POST /chat endpoint not available yet");
}

