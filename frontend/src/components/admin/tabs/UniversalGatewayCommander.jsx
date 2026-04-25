import { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "../../ui/card";
import { Button } from "../../ui/button";
import { Badge } from "../../ui/badge";
import {
  Crown, Brain, CheckCircle2, XCircle, RefreshCw, Key, Copy,
  Clipboard, Trash2, GitBranch, Zap, BookOpen, ThumbsUp, ThumbsDown,
  GraduationCap, Route, Shield
} from "lucide-react";
import { toast } from "sonner";
import { API } from "../../../App";
import IntegrationAuthorityPanel from "../../IntegrationAuthorityPanel";

const SECTIONS = [
  { id: "authority", label: "Integration Authority", icon: Shield },
  { id: "memory",    label: "Memory Graph", icon: Brain },
  { id: "sme",       label: "SME Queue",    icon: GraduationCap },
  { id: "eval",      label: "Eval Harness", icon: CheckCircle2 },
  { id: "mcp",       label: "MCP Tokens",   icon: Key },
  { id: "router",    label: "Retrieval Router", icon: Route },
];

export const UniversalGatewayCommander = ({ token }) => {
  const [section, setSection] = useState("authority");

  const fetchJ = useCallback(async (path, opts = {}) => {
    const tk = token || localStorage.getItem("token") || "";
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: {
        Authorization: `Bearer ${tk}`,
        "Content-Type": "application/json",
        ...(opts.headers || {}),
      },
    });
    const body = r.status !== 204 ? await r.json().catch(() => ({})) : {};
    if (!r.ok) throw new Error(body?.detail || `${r.status} ${r.statusText}`);
    return body;
  }, [token]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-500/30 to-teal-500/30 flex items-center justify-center">
          <Crown className="w-5 h-5 text-violet-300" />
        </div>
        <div>
          <h3 className="text-lg font-bold text-white font-['Outfit']">Commander Intelligence</h3>
          <p className="text-xs text-zinc-500">Memory graph · SME corrections · LLM-judge eval · MCP tokens · retrieval router</p>
        </div>
      </div>

      <div className="flex gap-2 border-b border-white/10">
        {SECTIONS.map(s => (
          <button key={s.id} onClick={() => setSection(s.id)}
            className={`px-3 py-2 text-sm font-medium border-b-2 transition-colors ${
              section === s.id
                ? "text-violet-300 border-violet-400"
                : "text-zinc-500 border-transparent hover:text-zinc-300"
            }`}>
            <s.icon className="w-4 h-4 inline mr-1.5 -mt-0.5" /> {s.label}
          </button>
        ))}
      </div>

      {section === "authority" && <IntegrationAuthorityPanel token={token} />}
      {section === "memory" && <MemorySection fetchJ={fetchJ} />}
      {section === "sme" && <SmeSection fetchJ={fetchJ} />}
      {section === "eval" && <EvalSection fetchJ={fetchJ} />}
      {section === "mcp" && <McpSection fetchJ={fetchJ} />}
      {section === "router" && <RouterSection fetchJ={fetchJ} />}
    </div>
  );
};

// ── Memory ───────────────────────────────────────────────────────

const MemorySection = ({ fetchJ }) => {
  const [facts, setFacts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [extractText, setExtractText] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetchJ("/memory/recall?limit=50");
      setFacts(r.facts || []);
    } catch (e) { toast.error(e.message); } finally { setLoading(false); }
  }, [fetchJ]);

  useEffect(() => { load(); }, [load]);

  const extract = async () => {
    if (!extractText.trim()) return;
    try {
      const r = await fetchJ("/memory/extract", {
        method: "POST", body: JSON.stringify({ text: extractText }),
      });
      toast.success(`Extracted ${(r.recorded || []).length} facts`);
      setExtractText("");
      await load();
    } catch (e) { toast.error(e.message); }
  };

  return (
    <Card className="bg-zinc-900/30 border-white/10">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-white">Temporal facts ({facts.length} active)</div>
          <Button size="sm" variant="outline" onClick={load}
            className="border-white/10 text-zinc-400 hover:text-white">
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
        <div>
          <textarea value={extractText} onChange={e => setExtractText(e.target.value)}
            placeholder="Paste a user message — Commander extracts declarative facts (e.g. 'I prefer OpenAI for reasoning; my timezone is PST')"
            rows={2}
            className="w-full bg-zinc-950 border border-white/10 rounded-md p-2 text-xs text-white" />
          <Button size="sm" onClick={extract} disabled={!extractText.trim()} className="mt-2 bg-violet-500/20 text-violet-300 border border-violet-500/40">
            Extract + record
          </Button>
        </div>
        <div className="space-y-1 mt-3 max-h-96 overflow-y-auto">
          {facts.length === 0 && (
            <div className="text-xs text-zinc-500 p-4 text-center">No facts recorded yet.</div>
          )}
          {facts.map(f => (
            <div key={f.fact_id} className="p-2 bg-zinc-950 rounded text-xs border border-white/5">
              <div className="flex items-center gap-2">
                <Badge className="bg-violet-500/10 text-violet-300 border-violet-500/20 font-mono">{f.topic}</Badge>
                <span className="text-white font-medium">{f.subject}</span>
                <span className="text-zinc-500">{f.predicate}</span>
                <span className="text-teal-300">{JSON.stringify(f.object)}</span>
              </div>
              <div className="text-zinc-600 font-mono mt-1">since {f.valid_from?.slice(0,19)}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// ── SME ──────────────────────────────────────────────────────────

const SmeSection = ({ fetchJ }) => {
  const [items, setItems] = useState([]);
  const [status, setStatus] = useState("pending");
  const [loading, setLoading] = useState(false);
  const [correction, setCorrection] = useState({});

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetchJ(`/sme/queue?status=${status}&limit=50`);
      setItems(r.items || []);
    } catch (e) { toast.error(e.message); } finally { setLoading(false); }
  }, [fetchJ, status]);

  useEffect(() => { load(); }, [load]);

  const approve = async (cid) => {
    try {
      await fetchJ("/sme/approve", {
        method: "POST",
        body: JSON.stringify({ correction_id: cid, corrected_answer: correction[cid] || null }),
      });
      toast.success("Approved — future similar queries will hit this answer");
      await load();
    } catch (e) { toast.error(e.message); }
  };
  const reject = async (cid) => {
    try {
      await fetchJ("/sme/reject", { method: "POST", body: JSON.stringify({ correction_id: cid }) });
      await load();
    } catch (e) { toast.error(e.message); }
  };

  return (
    <Card className="bg-zinc-900/30 border-white/10">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div className="text-sm font-medium text-white">SME review queue</div>
          <div className="flex gap-2">
            <select value={status} onChange={e => setStatus(e.target.value)}
              className="bg-zinc-950 border border-white/10 rounded-md px-2 py-1 text-xs text-white">
              <option value="pending">Pending</option>
              <option value="validated">Validated</option>
              <option value="rejected">Rejected</option>
            </select>
            <Button size="sm" variant="outline" onClick={load}
              className="border-white/10 text-zinc-400">
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>
        {items.length === 0 && (
          <div className="text-xs text-zinc-500 p-4 text-center">Queue is empty.</div>
        )}
        {items.map(it => (
          <div key={it.correction_id} className="p-3 bg-zinc-950 rounded-md text-xs space-y-2 border border-white/5">
            <div className="text-zinc-500">Query</div>
            <div className="text-zinc-200">{it.query}</div>
            <div className="text-zinc-500">Original response (flagged: {it.reason})</div>
            <div className="text-zinc-400">{it.original_response?.slice(0, 400)}…</div>
            {status === "pending" && (
              <>
                <textarea value={correction[it.correction_id] || ""}
                  onChange={e => setCorrection({ ...correction, [it.correction_id]: e.target.value })}
                  placeholder="Optional: correct answer (leave blank to approve original)"
                  rows={2}
                  className="w-full bg-zinc-900 border border-white/10 rounded p-1.5 text-xs text-white" />
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => approve(it.correction_id)}
                    className="bg-teal-500/20 text-teal-300 border border-teal-500/40">
                    <ThumbsUp className="w-3 h-3 mr-1" /> Approve
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => reject(it.correction_id)}
                    className="border-rose-500/30 text-rose-300 hover:bg-rose-500/10">
                    <ThumbsDown className="w-3 h-3 mr-1" /> Reject
                  </Button>
                </div>
              </>
            )}
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

// ── Eval harness ─────────────────────────────────────────────────

const EvalSection = ({ fetchJ }) => {
  const [goldens, setGoldens] = useState([]);
  const [latest, setLatest] = useState({});
  const [promptIn, setPromptIn] = useState("");
  const [task, setTask] = useState("general");
  const [reference, setReference] = useState("");
  const [modelsIn, setModelsIn] = useState("openai/gpt-4o-mini,gemini/gemini-2.5-flash,groq/llama-3.3-70b-versatile");
  const [running, setRunning] = useState(false);
  const [lastRun, setLastRun] = useState(null);

  const load = useCallback(async () => {
    try {
      const [g, l] = await Promise.all([fetchJ("/eval/golden"), fetchJ("/eval/latest")]);
      setGoldens(g.items || []);
      setLatest(l.summary || {});
    } catch (e) { toast.error(e.message); }
  }, [fetchJ]);

  useEffect(() => { load(); }, [load]);

  const addGolden = async () => {
    if (!promptIn.trim()) return;
    try {
      await fetchJ("/eval/golden", {
        method: "POST",
        body: JSON.stringify({ prompt: promptIn, task, reference: reference || null }),
      });
      setPromptIn(""); setReference("");
      toast.success("Added to golden set");
      await load();
    } catch (e) { toast.error(e.message); }
  };

  const runEval = async () => {
    const models = modelsIn.split(",").map(m => m.trim()).filter(Boolean);
    if (!models.length || !goldens.length) return toast.error("Need models + golden set");
    setRunning(true);
    try {
      const r = await fetchJ("/eval/run", {
        method: "POST",
        body: JSON.stringify({ models, judge_model: "maars/auto", pass_threshold: 0.7, limit: Math.min(10, goldens.length) }),
      });
      setLastRun(r);
      toast.success(`Run ${r.run_id}: ${Object.keys(r.summary || {}).length} models judged`);
      await load();
    } catch (e) { toast.error("Eval failed: " + e.message); }
    finally { setRunning(false); }
  };

  return (
    <div className="space-y-3">
      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4 space-y-2">
          <div className="text-sm font-medium text-white">Add to golden set</div>
          <textarea value={promptIn} onChange={e => setPromptIn(e.target.value)}
            placeholder="Prompt"
            rows={2}
            className="w-full bg-zinc-950 border border-white/10 rounded p-2 text-xs text-white" />
          <div className="flex gap-2">
            <input value={task} onChange={e => setTask(e.target.value)}
              placeholder="task (general / code / reasoning / extraction)"
              className="flex-1 bg-zinc-950 border border-white/10 rounded p-1.5 text-xs text-white" />
            <input value={reference} onChange={e => setReference(e.target.value)}
              placeholder="reference answer (optional)"
              className="flex-1 bg-zinc-950 border border-white/10 rounded p-1.5 text-xs text-white" />
          </div>
          <Button size="sm" onClick={addGolden} className="bg-violet-500/20 text-violet-300 border border-violet-500/40">Add</Button>
          <div className="text-xs text-zinc-500">{goldens.length} items in golden set</div>
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4 space-y-2">
          <div className="text-sm font-medium text-white">Run regression</div>
          <input value={modelsIn} onChange={e => setModelsIn(e.target.value)}
            placeholder="comma-separated model IDs"
            className="w-full bg-zinc-950 border border-white/10 rounded p-1.5 text-xs text-white font-mono" />
          <Button size="sm" onClick={runEval} disabled={running || !goldens.length}
            className="bg-teal-500/20 text-teal-300 border border-teal-500/40">
            {running ? "Running…" : "Run eval"}
          </Button>
          {lastRun && (
            <div className="text-xs mt-2">
              <div className="text-zinc-500">Run {lastRun.run_id} · {lastRun.sample_size} items</div>
              <div className="mt-1 space-y-1">
                {Object.entries(lastRun.summary || {}).map(([model, s]) => (
                  <div key={model} className="flex items-center gap-2 font-mono">
                    <span className={s.benched ? "text-rose-300" : "text-teal-300"}>
                      {s.benched ? "↓" : "✓"}
                    </span>
                    <span className="text-white">{model}</span>
                    <span className="text-zinc-400">mean {s.mean.toFixed(2)}</span>
                    <span className="text-zinc-500">pass {Math.round(s.pass_rate*100)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4">
          <div className="text-sm font-medium text-white mb-2">Latest summary per model</div>
          {Object.keys(latest).length === 0 ? (
            <div className="text-xs text-zinc-500 p-3 text-center">No eval runs yet.</div>
          ) : (
            <div className="space-y-1">
              {Object.entries(latest).map(([model, s]) => (
                <div key={model} className="flex items-center gap-2 text-xs font-mono">
                  <span className={s.benched ? "text-rose-300" : "text-teal-300"}>
                    {s.benched ? "BENCHED" : "OK"}
                  </span>
                  <span className="text-white">{model}</span>
                  <span className="text-zinc-400">{s.mean.toFixed(2)}</span>
                  <span className="text-zinc-500">n={s.sample_size}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

// ── MCP Tokens ───────────────────────────────────────────────────

const McpSection = ({ fetchJ }) => {
  const [tokens, setTokens] = useState([]);
  const [label, setLabel] = useState("claude-desktop");
  const [issued, setIssued] = useState(null);

  const load = useCallback(async () => {
    try {
      const r = await fetchJ("/mcp/tokens");
      setTokens(r.tokens || []);
    } catch (e) { toast.error(e.message); }
  }, [fetchJ]);

  useEffect(() => { load(); }, [load]);

  const issue = async () => {
    try {
      const r = await fetchJ("/mcp/tokens/issue", { method: "POST", body: JSON.stringify({ label }) });
      setIssued(r.token);
      toast.success("Token issued — copy it now, you won't see it again");
      await load();
    } catch (e) { toast.error(e.message); }
  };
  const revoke = async (prefix) => {
    if (!window.confirm("Revoke this token?")) return;
    try {
      await fetchJ(`/mcp/tokens/${prefix.replace("…","")}`, { method: "DELETE" });
      await load();
    } catch (e) { toast.error(e.message); }
  };

  return (
    <Card className="bg-zinc-900/30 border-white/10">
      <CardContent className="p-4 space-y-3">
        <div className="text-sm font-medium text-white">Issue MCP token</div>
        <p className="text-xs text-zinc-500">
          Paste the token as <code className="bg-zinc-950 px-1.5 py-0.5 rounded">MAARS_MCP_TOKEN</code> env var in Claude Desktop or Cursor's MCP config. The <code>mcp_server</code> process reads it to route calls under your MAARS wallet.
        </p>
        <div className="flex gap-2">
          <input value={label} onChange={e => setLabel(e.target.value)}
            placeholder="label"
            className="flex-1 bg-zinc-950 border border-white/10 rounded p-1.5 text-xs text-white" />
          <Button size="sm" onClick={issue} className="bg-violet-500/20 text-violet-300 border border-violet-500/40">
            Issue
          </Button>
        </div>
        {issued && (
          <div className="p-2 bg-teal-500/10 border border-teal-500/30 rounded font-mono text-xs text-teal-200 flex items-center gap-2">
            <span className="flex-1 break-all">{issued}</span>
            <Button size="sm" variant="ghost"
              onClick={() => { navigator.clipboard.writeText(issued); toast.success("Copied"); }}
              className="text-teal-300">
              <Copy className="w-3 h-3" />
            </Button>
          </div>
        )}
        <div className="mt-3">
          <div className="text-sm font-medium text-white mb-2">Active tokens ({tokens.length})</div>
          {tokens.map(t => (
            <div key={t.token_preview} className="flex items-center justify-between py-1 text-xs">
              <span className="font-mono text-zinc-300">{t.token_preview}</span>
              <span className="text-zinc-500">{t.label}</span>
              <span className="text-zinc-600">{t.created_at?.slice(0,19)}</span>
              <Button size="sm" variant="ghost" onClick={() => revoke(t.token_preview.split("…")[0])}
                className="text-rose-400 hover:bg-rose-500/10">
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// ── Retrieval Router ─────────────────────────────────────────────

const RouterSection = ({ fetchJ }) => {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);

  const route = async () => {
    if (!query.trim()) return;
    setBusy(true);
    try {
      const r = await fetchJ("/retrieval/route", {
        method: "POST", body: JSON.stringify({ query }),
      });
      setResult(r);
    } catch (e) { toast.error(e.message); } finally { setBusy(false); }
  };

  return (
    <Card className="bg-zinc-900/30 border-white/10">
      <CardContent className="p-4 space-y-3">
        <div className="text-sm font-medium text-white">Classify a query</div>
        <p className="text-xs text-zinc-500">
          Cheap classifier picks <code>rag</code> / <code>web</code> / <code>sql</code> / <code>direct</code> before the model router runs. Auto-upgrades to RAG when you have indexed docs.
        </p>
        <div className="flex gap-2">
          <input value={query} onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !busy && route()}
            placeholder="Paste a query"
            className="flex-1 bg-zinc-950 border border-white/10 rounded p-1.5 text-xs text-white" />
          <Button size="sm" onClick={route} disabled={busy || !query.trim()}
            className="bg-violet-500/20 text-violet-300 border border-violet-500/40">
            {busy ? "…" : "Route"}
          </Button>
        </div>
        {result && (
          <div className="p-3 bg-zinc-950 rounded text-xs space-y-1">
            <div>
              <Badge className="bg-violet-500/20 text-violet-300 border-violet-500/40 uppercase">{result.mode}</Badge>
            </div>
            <div className="text-zinc-300">{result.reasoning}</div>
            {result.context && (
              <>
                <div className="text-zinc-500 mt-1">Pre-retrieved context ({result.citations?.length || 0} sources):</div>
                <pre className="text-zinc-400 whitespace-pre-wrap">{result.context.slice(0, 600)}</pre>
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UniversalGatewayCommander;
