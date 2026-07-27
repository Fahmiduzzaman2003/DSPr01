/** Thin API client.
 *
 * VITE_API_URL points at the deployed backend in production. Left empty in dev,
 * where vite proxies /api to localhost:8000.
 */
const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

async function request(path, options) {
  const response = await fetch(`${BASE}${path}`, options);
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`${response.status} ${response.statusText} ${detail}`.trim());
  }
  return response.json();
}

export const fetchConfig = () => request("/api/config");

export const fetchDiagnostics = (model) =>
  request(`/api/diagnostics/${encodeURIComponent(model)}`);

export const postPredict = (values) =>
  request("/api/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ values }),
  });
