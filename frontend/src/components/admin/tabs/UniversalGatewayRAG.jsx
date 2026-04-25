import { useState, useEffect, useCallback } from "react";
import { Card, CardContent } from "../../ui/card";
import { Button } from "../../ui/button";
import { Badge } from "../../ui/badge";
import {
  FileText, Upload, Search, Trash2, RefreshCw, Database, BookOpen, Brain
} from "lucide-react";
import { toast } from "sonner";
import { API } from "../../../App";

export const UniversalGatewayRAG = ({ token }) => {
  const [docs, setDocs] = useState([]);
  const [query, setQuery] = useState("");
  const [queryResult, setQueryResult] = useState(null);
  const [pasteText, setPasteText] = useState("");
  const [pasteTitle, setPasteTitle] = useState("");
  const [loading, setLoading] = useState(false);
  const [querying, setQuerying] = useState(false);
  const [uploading, setUploading] = useState(false);

  const fetchJ = useCallback(async (path, opts = {}) => {
    const tk = token || localStorage.getItem("token") || "";
    const r = await fetch(`${API}${path}`, {
      ...opts,
      headers: {
        Authorization: `Bearer ${tk}`,
        ...(opts.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
        ...(opts.headers || {}),
      },
    });
    const body = r.status !== 204 ? await r.json().catch(() => ({})) : {};
    if (!r.ok) throw new Error(body?.detail || `${r.status} ${r.statusText}`);
    return body;
  }, [token]);

  const loadDocs = useCallback(async () => {
    setLoading(true);
    try {
      const r = await fetchJ("/rag/documents");
      setDocs(r.docs || []);
    } catch (e) { toast.error(e.message); } finally { setLoading(false); }
  }, [fetchJ]);

  useEffect(() => { loadDocs(); }, [loadDocs]);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("title", file.name);
      const r = await fetchJ("/rag/ingest", { method: "POST", body: fd });
      toast.success(`Ingested ${r.chunks} chunks`);
      await loadDocs();
    } catch (err) { toast.error(err.message); }
    finally { setUploading(false); e.target.value = ""; }
  };

  const handleTextIngest = async () => {
    if (!pasteText.trim()) return toast.error("Paste text first");
    setUploading(true);
    try {
      const r = await fetchJ("/rag/ingest-text", {
        method: "POST",
        body: JSON.stringify({ text: pasteText, title: pasteTitle || "pasted" }),
      });
      toast.success(`Ingested ${r.chunks} chunks`);
      setPasteText(""); setPasteTitle("");
      await loadDocs();
    } catch (err) { toast.error(err.message); }
    finally { setUploading(false); }
  };

  const runQuery = async () => {
    if (!query.trim()) return;
    setQuerying(true); setQueryResult(null);
    try {
      const r = await fetchJ("/rag/query", {
        method: "POST",
        body: JSON.stringify({ query, top_k: 8, enable_web_fallback: true }),
      });
      setQueryResult(r);
    } catch (err) { toast.error("Query failed: " + err.message); }
    finally { setQuerying(false); }
  };

  const deleteDoc = async (doc_id) => {
    if (!window.confirm("Delete this doc + chunks?")) return;
    try {
      await fetchJ(`/rag/documents/${doc_id}`, { method: "DELETE" });
      toast.success("Deleted");
      await loadDocs();
    } catch (e) { toast.error(e.message); }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500/30 to-violet-500/30 flex items-center justify-center">
          <Brain className="w-5 h-5 text-violet-300" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-bold text-white font-['Outfit']">Agentic RAG</h3>
          <p className="text-xs text-zinc-500">Corrective retrieval with web fallback + citations. Docling parser + cosine search over Mongo.</p>
        </div>
        <Button size="sm" variant="outline" onClick={loadDocs} disabled={loading}
          className="border-white/10 text-zinc-400 hover:text-white">
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </div>

      {/* Query */}
      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4 space-y-3">
          <div className="text-sm font-medium text-white flex items-center gap-2">
            <Search className="w-4 h-4" /> Query your documents
          </div>
          <div className="flex gap-2">
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === "Enter" && !querying && runQuery()}
              placeholder="What does the operator manual say about X?"
              className="flex-1 bg-zinc-950 border border-white/10 rounded-md p-2 text-sm text-white"
            />
            <Button onClick={runQuery} disabled={querying || !query.trim()}
              className="bg-violet-500/20 text-violet-300 border border-violet-500/40">
              {querying ? "Thinking..." : "Ask"}
            </Button>
          </div>
          {queryResult && (
            <div className="space-y-2 mt-3">
              <div className="text-xs text-zinc-500">
                Confidence: <span className="text-violet-300 font-mono">{queryResult.confidence?.toFixed(2) ?? "—"}</span>
                {" · "}Sources: <span className="text-teal-300">{(queryResult.sources_used || []).join(", ") || "—"}</span>
                {" · "}<span className="text-zinc-600">{queryResult.raw_kept}/{queryResult.raw_retrieved} chunks kept</span>
              </div>
              <div className="p-3 bg-zinc-950 rounded-md text-sm text-zinc-200 whitespace-pre-wrap">
                {queryResult.answer}
              </div>
              {(queryResult.citations || []).length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {queryResult.citations.map((c, i) => (
                    <Badge key={i} variant="outline" className="border-white/10 text-zinc-400 text-xs font-mono">
                      {c.ref} {c.page ? `p${c.page}` : ""} {c.title || c.doc_id || ""}
                    </Badge>
                  ))}
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Upload */}
      <div className="grid grid-cols-2 gap-3">
        <Card className="bg-zinc-900/30 border-white/10">
          <CardContent className="p-4 space-y-2">
            <div className="text-sm font-medium text-white flex items-center gap-2">
              <Upload className="w-4 h-4" /> Upload document
            </div>
            <p className="text-xs text-zinc-500">PDF / DOCX / XLSX / PPTX / TXT — Docling preserves table structure.</p>
            <label className="block">
              <input type="file" accept=".pdf,.docx,.xlsx,.pptx,.txt,.md" onChange={handleFileUpload}
                disabled={uploading}
                className="block w-full text-xs text-zinc-400 file:bg-violet-500/20 file:text-violet-300 file:border file:border-violet-500/40 file:rounded-md file:px-3 file:py-1.5 file:text-xs file:font-semibold file:cursor-pointer" />
            </label>
          </CardContent>
        </Card>
        <Card className="bg-zinc-900/30 border-white/10">
          <CardContent className="p-4 space-y-2">
            <div className="text-sm font-medium text-white flex items-center gap-2">
              <FileText className="w-4 h-4" /> Paste text
            </div>
            <input value={pasteTitle} onChange={e => setPasteTitle(e.target.value)}
              placeholder="title (optional)"
              className="w-full bg-zinc-950 border border-white/10 rounded-md p-1.5 text-xs text-white" />
            <textarea value={pasteText} onChange={e => setPasteText(e.target.value)}
              placeholder="Paste text to ingest…"
              rows={3}
              className="w-full bg-zinc-950 border border-white/10 rounded-md p-2 text-xs text-white" />
            <Button size="sm" onClick={handleTextIngest} disabled={uploading || !pasteText.trim()}
              className="w-full bg-violet-500/20 text-violet-300 border border-violet-500/40">
              Ingest text
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Doc list */}
      <Card className="bg-zinc-900/30 border-white/10">
        <CardContent className="p-4">
          <div className="text-sm font-medium text-white mb-2 flex items-center gap-2">
            <Database className="w-4 h-4" /> Your documents ({docs.length})
          </div>
          {docs.length === 0 && (
            <div className="text-xs text-zinc-500 p-4 text-center">No documents ingested yet.</div>
          )}
          {docs.map(d => (
            <div key={d.doc_id} className="flex items-center justify-between py-2 border-b border-white/5 text-xs">
              <div className="min-w-0 flex-1">
                <div className="text-white font-medium truncate">{d.title}</div>
                <div className="text-zinc-500 font-mono">{d.doc_id} · {d.chunk_count} chunks · {d.parser}</div>
              </div>
              <Button size="sm" variant="ghost" onClick={() => deleteDoc(d.doc_id)}
                className="text-rose-400 hover:bg-rose-500/10">
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
};

export default UniversalGatewayRAG;
