const API_BASE =
  ((import.meta as unknown as { env: Record<string, string> }).env?.VITE_API_URL as string) ||
  'http://127.0.0.1:8000/api';

export async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'API request failed');
    }
    return await res.json();
  } catch (error) {
    console.warn(`[ProofAI API] Request to ${endpoint} failed.`, error);
    throw error;
  }
}
