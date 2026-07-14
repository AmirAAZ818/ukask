// Thin wrapper around the FastAPI backend. Everything the UI knows about the
// server lives here, so swapping the base URL for the deployed build is a
// one-line change.

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

async function request(path, options) {
  const res = await fetch(`${API_BASE}${path}`, options);

  if (!res.ok) {
    // the backend always sends {detail} on failure, fall back if it somehow doesn't
    let detail = "ارتباط با سرور برقرار نشد.";
    try {
      const body = await res.json();
      if (body.detail) detail = body.detail;
    } catch {
      // response wasn't json, keep the fallback message
    }
    throw new Error(detail);
  }

  return res.json();
}

export function askQuestion(question, k = 5) {
  return request("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, k }),
  });
}

export function fetchHealth() {
  return request("/api/health");
}