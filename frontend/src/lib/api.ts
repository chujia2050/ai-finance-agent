const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "Request failed");
  }

  return res.json();
}

export async function uploadFile(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "Upload failed");
  }

  return res.json();
}

export async function getDatasets() {
  return fetchApi<unknown[]>("/api/datasets");
}

export async function getDataset(id: number) {
  return fetchApi<unknown>(`/api/datasets/${id}`);
}

export async function getAnalysis(datasetId: number) {
  return fetchApi<unknown>(`/api/datasets/${datasetId}/analysis`);
}

export async function sendChatMessage(datasetId: number, message: string) {
  return fetchApi<{ response: string; tools_used: string[] }>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ dataset_id: datasetId, message }),
  });
}

export async function getChatHistory(datasetId: number) {
  return fetchApi<unknown[]>(`/api/datasets/${datasetId}/chat-history`);
}
