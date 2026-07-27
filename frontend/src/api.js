/** Thin API client.
 *
 * VITE_API_URL points at the deployed backend in production. Left empty in dev,
 * where vite proxies /api to localhost:8000.
 *
 * Note it is inlined at BUILD time, not read at runtime — changing it in the
 * Vercel dashboard does nothing until you redeploy.
 */
const BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

// Empty BASE only works in dev, where vite proxies /api. In a deployed build it
// means the variable was never set, so say so instead of failing obscurely.
const MISCONFIGURED =
  !BASE && !["localhost", "127.0.0.1"].includes(window.location.hostname);

async function request(path, options) {
  if (MISCONFIGURED) {
    throw new Error(
      "VITE_API_URL is not set in this build. Add it in Vercel " +
        "(Settings -> Environment Variables), pointing at your Render backend, " +
        "then redeploy — the value is baked in at build time."
    );
  }

  const response = await fetch(`${BASE}${path}`, options);
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(`${response.status} ${response.statusText} ${detail}`.trim());
  }

  // A stray HTML response means the request hit a static host, not the API.
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    throw new Error(
      `Expected JSON from ${BASE || window.location.origin}${path} but got ` +
        `"${contentType}". The request is not reaching the backend.`
    );
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
