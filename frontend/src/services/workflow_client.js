/**
 * workflow_client — thin browser-side wrapper around the
 * /api/workflows/* endpoints that the new executor exposes.
 *
 * Canvas already uses /api/kernel/workflows/* for CRUD (don't touch).
 * This client adds:
 *   - Tools catalog (fetches the 75+ tools the executor can run)
 *   - Runs history + run detail + SSE progress stream
 *   - Test single node
 *   - Pin / unpin node output for design-mode runs
 *   - Versioning (list, publish, get, rollback)
 *   - Environment variables (list, put, delete)
 *
 * Used from any React component via `import client from
 * "./services/workflow_client"`.
 */
const BASE = (
  typeof process !== "undefined" && process.env && process.env.REACT_APP_BACKEND_URL
    ? process.env.REACT_APP_BACKEND_URL
    : ""
).trim();

const API = `${BASE}/api`;

function authHeaders() {
  const t = localStorage.getItem("token");
  return t ? { Authorization: `Bearer ${t}` } : {};
}
function jsonHeaders() {
  return { "Content-Type": "application/json", ...authHeaders() };
}

async function j(url, opts = {}) {
  const r = await fetch(url, {
    ...opts,
    headers: { ...(opts.headers || {}), ...authHeaders() },
  });
  if (!r.ok) {
    const body = await r.text().catch(() => "");
    throw new Error(`${r.status} ${r.statusText}: ${body.slice(0, 300)}`);
  }
  const ct = r.headers.get("content-type") || "";
  return ct.includes("application/json") ? r.json() : r.text();
}

const client = {
  // ── Tools catalog — for the node palette ─────────────────────────
  async tools() {
    return j(`${API}/workflows/tools/catalog`);
  },

  // ── Runs ─────────────────────────────────────────────────────────
  async listRuns(workflowId, opts = {}) {
    const q = new URLSearchParams(opts).toString();
    return j(`${API}/workflows/${workflowId}/runs${q ? `?${q}` : ""}`);
  },
  async getRun(runId) {
    return j(`${API}/workflows/runs/${runId}`);
  },

  /**
   * Subscribe to SSE events for a run. Returns a cleanup function.
   *   const stop = client.streamRunEvents(runId, ev => console.log(ev));
   *   // later
   *   stop();
   */
  streamRunEvents(runId, onEvent, onError) {
    const url = `${API}/workflows/runs/${runId}/events`;
    const token = localStorage.getItem("token");
    // Native EventSource can't send auth headers — so we open with a
    // query param fallback IF the server accepts it; else the
    // endpoint is already behind cookie session. Assume the latter.
    const es = new EventSource(`${url}${token ? `?t=${encodeURIComponent(token)}` : ""}`);
    es.onmessage = (ev) => {
      try {
        onEvent(JSON.parse(ev.data));
      } catch {
        onEvent({ raw: ev.data });
      }
    };
    if (onError) es.onerror = onError;
    return () => es.close();
  },

  // ── Node ops ─────────────────────────────────────────────────────
  async testNode(workflowId, nodeId, input = {}, overridesParams = null) {
    return j(`${API}/workflows/${workflowId}/nodes/${nodeId}/test`, {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify({ input, overrides_params: overridesParams }),
    });
  },
  async pinNode(workflowId, nodeId, output) {
    return j(`${API}/workflows/${workflowId}/nodes/${nodeId}/pin`, {
      method: "PUT",
      headers: jsonHeaders(),
      body: JSON.stringify({ output }),
    });
  },
  async unpinNode(workflowId, nodeId) {
    return j(`${API}/workflows/${workflowId}/nodes/${nodeId}/pin`, {
      method: "DELETE",
      headers: authHeaders(),
    });
  },

  // ── Versioning ───────────────────────────────────────────────────
  async listVersions(workflowId) {
    return j(`${API}/workflows/${workflowId}/versions`);
  },
  async getVersion(workflowId, version) {
    return j(`${API}/workflows/${workflowId}/versions/${version}`);
  },
  async publishVersion(workflowId, note = "") {
    const q = note ? `?note=${encodeURIComponent(note)}` : "";
    return j(`${API}/workflows/${workflowId}/versions${q}`, { method: "POST" });
  },
  async rollbackTo(workflowId, version) {
    return j(`${API}/workflows/${workflowId}/versions/${version}/rollback`, {
      method: "POST",
    });
  },

  // ── Environment variables ────────────────────────────────────────
  async listEnv(orgId = null) {
    const q = orgId ? `?org_id=${encodeURIComponent(orgId)}` : "";
    return j(`${API}/workflows/env${q}`);
  },
  async putEnv({ key, value, secret = false, scope = "user", scopeId = null }) {
    return j(`${API}/workflows/env`, {
      method: "PUT",
      headers: jsonHeaders(),
      body: JSON.stringify({
        key, value, secret,
        scope, scope_id: scopeId,
      }),
    });
  },
  async deleteEnv({ key, scope = "user", scopeId = null }) {
    const q = scopeId ? `?scope_id=${encodeURIComponent(scopeId)}` : "";
    return j(`${API}/workflows/env/${scope}/${key}${q}`, { method: "DELETE" });
  },

  // ── OAuth / inbound webhook meta ─────────────────────────────────
  async webhookInfo(workflowId) {
    return j(`${API}/webhooks/workflow/${workflowId}`);
  },
  async resumeWait(token, payload = {}) {
    return j(`${API}/webhooks/resume/${token}`, {
      method: "POST",
      headers: jsonHeaders(),
      body: JSON.stringify(payload),
    });
  },
};

// Expose on window for devtools-driven testing while the canvas
// UI integration catches up.
if (typeof window !== "undefined") {
  window.MaarsWorkflowClient = client;
}

export default client;
