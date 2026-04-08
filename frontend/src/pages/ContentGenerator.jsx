import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Sparkles, Clock, Copy, Trash2, ChevronDown, ChevronUp,
  FileText, Palette, Zap, Mail, Megaphone, Newspaper, PenTool
} from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  amber: "#f59e0b",
  violet: "#7c3aed",
  indigo: "#818cf8",
  green: "#34d399",
  red: "#ef4444",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const TYPE_ICONS = {
  marketing_copy: Megaphone, social_post: Zap, email_campaign: Mail,
  blog_article: Newspaper, ad_copy: Megaphone, press_release: FileText,
  brand_guidelines: Palette, custom: PenTool,
};

const ContentGenerator = () => {
  const { token } = useAuth();
  const [contentTypes, setContentTypes] = useState([]);
  const [blueprints, setBlueprints] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [expandedItem, setExpandedItem] = useState(null);

  const [selectedType, setSelectedType] = useState("marketing_copy");
  const [selectedBlueprint, setSelectedBlueprint] = useState("");
  const [prompt, setPrompt] = useState("");
  const [length, setLength] = useState("medium");
  const [toneOverride, setToneOverride] = useState("");

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchData = useCallback(async () => {
    try {
      const [typesRes, bpRes, histRes] = await Promise.all([
        fetch(`${API}/content/types`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/reference/history`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API}/content/history`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (typesRes.ok) setContentTypes((await typesRes.json()).types || []);
      if (bpRes.ok) setBlueprints((await bpRes.json()).items || []);
      if (histRes.ok) setHistory((await histRes.json()).items || []);
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const generate = async () => {
    if (!prompt.trim()) return toast.error("Enter a content prompt");
    setGenerating(true);
    try {
      const res = await fetch(`${API}/content/generate`, {
        method: "POST", headers,
        body: JSON.stringify({ content_type: selectedType, blueprint_id: selectedBlueprint, prompt, length, tone_override: toneOverride }),
      });
      if (res.ok) { const result = await res.json(); setHistory(prev => [result, ...prev]); toast.success("Content generated!"); }
      else { const err = await res.json().catch(() => ({})); toast.error(err.detail || "Generation failed"); }
    } catch { toast.error("Error generating content"); }
    finally { setGenerating(false); }
  };

  const copyContent = (text) => { navigator.clipboard.writeText(text); toast.success("Copied to clipboard"); };

  const deleteContent = async (contentId) => {
    try {
      await fetch(`${API}/content/${contentId}`, { method: "DELETE", headers });
      setHistory(prev => prev.filter(h => h.content_id !== contentId));
      toast.success("Content deleted");
    } catch {}
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 28, height: 28, border: `2px solid ${T.amber}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
      <style>{STYLES}</style>
    </div>
  );

  const glassCard = { background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "18px 20px" };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="content-generator">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(245,158,11,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <PenTool size={22} style={{ color: T.amber }} />
        </div>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 26, fontWeight: 700, color: "#fff", margin: 0, marginBottom: 3 }}>Content Generator</h1>
          <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>Generate on-brand content using Style Blueprints from Reference Intelligence</p>
        </div>
      </div>

      {/* Generator form */}
      <div style={{ ...glassCard, display: "flex", flexDirection: "column", gap: 18 }}>

        {/* Content type grid */}
        <div>
          <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Content Type</label>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8 }}>
            {contentTypes.map(t => {
              const Icon = TYPE_ICONS[t.id] || PenTool;
              const active = selectedType === t.id;
              return (
                <button key={t.id} onClick={() => setSelectedType(t.id)} data-testid={`content-type-${t.id}`}
                  style={{ padding: "10px 12px", borderRadius: 10, border: `1px solid ${active ? "rgba(245,158,11,.3)" : T.border}`, background: active ? "rgba(245,158,11,.08)" : T.glass, cursor: "pointer", textAlign: "left", transition: "all .2s" }}
                  onMouseEnter={e => !active && (e.currentTarget.style.borderColor = "rgba(255,255,255,.12)")}
                  onMouseLeave={e => !active && (e.currentTarget.style.borderColor = T.border)}>
                  <Icon size={14} style={{ color: active ? T.amber : T.zinc, marginBottom: 4, display: "block" }} />
                  <span style={{ fontSize: 11, fontWeight: 600, color: active ? T.amber : "#a1a1aa" }}>{t.label}</span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Blueprint selector */}
        <div>
          <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Style Blueprint (optional)</label>
          <select value={selectedBlueprint} onChange={e => setSelectedBlueprint(e.target.value)}
            data-testid="blueprint-select"
            style={{ ...formInput, cursor: "pointer" }}
            onFocus={e => e.target.style.borderColor = "rgba(245,158,11,.4)"}
            onBlur={e => e.target.style.borderColor = T.border}>
            <option value="" style={{ background: "#1a1a2e" }}>No blueprint — use default style</option>
            {blueprints.map(bp => (
              <option key={bp.ref_id} value={bp.ref_id} style={{ background: "#1a1a2e" }}>
                [{bp.type}] {bp.source?.substring(0, 80)}
              </option>
            ))}
          </select>
          {selectedBlueprint && <p style={{ fontSize: 10, color: T.amber, marginTop: 5 }}>Content will match the tone and style from this reference</p>}
        </div>

        {/* Prompt */}
        <div>
          <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>What content do you need?</label>
          <textarea value={prompt} onChange={e => setPrompt(e.target.value)}
            placeholder="Describe the content you want... e.g., 'Write a LinkedIn post announcing our new AI product launch targeting enterprise CTOs'"
            data-testid="content-prompt"
            style={{ ...formInput, minHeight: 96, resize: "vertical", lineHeight: 1.6 }}
            onFocus={e => e.target.style.borderColor = "rgba(245,158,11,.4)"}
            onBlur={e => e.target.style.borderColor = T.border} />
        </div>

        {/* Options row */}
        <div style={{ display: "flex", gap: 16, flexWrap: "wrap", alignItems: "flex-end" }}>
          <div>
            <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Length</label>
            <div style={{ display: "flex", gap: 6 }}>
              {["short", "medium", "long"].map(l => (
                <button key={l} onClick={() => setLength(l)} data-testid={`length-${l}`}
                  style={{ padding: "6px 14px", borderRadius: 8, border: `1px solid ${length === l ? "rgba(245,158,11,.3)" : T.border}`, background: length === l ? "rgba(245,158,11,.1)" : T.glass, color: length === l ? T.amber : T.zinc, fontSize: 11, fontWeight: 600, cursor: "pointer", transition: "all .2s" }}>
                  {l}
                </button>
              ))}
            </div>
          </div>
          <div style={{ flex: 1, minWidth: 200 }}>
            <label style={{ display: "block", fontSize: 10, color: T.zinc, marginBottom: 8, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Tone Override (optional)</label>
            <input type="text" value={toneOverride} onChange={e => setToneOverride(e.target.value)}
              placeholder="e.g., formal, playful, urgent..." style={formInput} data-testid="tone-input"
              onFocus={e => e.target.style.borderColor = "rgba(245,158,11,.4)"}
              onBlur={e => e.target.style.borderColor = T.border} />
          </div>
        </div>

        {/* Generate button */}
        <div>
          <button onClick={generate} disabled={generating} data-testid="generate-btn"
            style={{ display: "flex", alignItems: "center", gap: 8, padding: "10px 22px", borderRadius: 10, background: generating ? "rgba(245,158,11,.3)" : `linear-gradient(135deg, #d97706, ${T.amber})`, border: "none", color: "#fff", fontSize: 14, fontWeight: 700, cursor: generating ? "not-allowed" : "pointer", transition: "opacity .2s" }}>
            {generating
              ? <><div style={{ width: 15, height: 15, border: "2px solid rgba(255,255,255,.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin .8s linear infinite" }} /> Generating…</>
              : <><Sparkles size={15} /> Generate Content</>}
          </button>
          {generating && <p style={{ fontSize: 11, color: T.amber, marginTop: 8, animation: "pulse 1.5s ease infinite" }}>AI is crafting your content… This may take 10–20 seconds.</p>}
        </div>
      </div>

      {/* History */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
          <Clock size={13} style={{ color: T.zinc }} />
          <span style={{ fontSize: 11, color: T.zinc, textTransform: "uppercase", letterSpacing: ".06em", fontWeight: 600 }}>Generated Content</span>
          <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 5, background: "rgba(255,255,255,.05)", color: T.zinc, marginLeft: "auto" }}>{history.length} items</span>
        </div>

        {history.length === 0 ? (
          <div style={{ textAlign: "center", padding: "56px 20px", border: `1px dashed ${T.border}`, borderRadius: 16 }}>
            <PenTool size={44} style={{ color: "rgba(255,255,255,.06)", marginBottom: 12 }} />
            <p style={{ fontSize: 13, color: T.zinc, marginBottom: 4 }}>No content generated yet</p>
            <p style={{ fontSize: 11, color: "rgba(113,113,122,.6)" }}>Select a content type, optionally pick a Style Blueprint, and describe what you need</p>
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {history.map((item) => {
              const Icon = TYPE_ICONS[item.content_type] || PenTool;
              const expanded = expandedItem === item.content_id;
              return (
                <div key={item.content_id}
                  style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", transition: "border-color .2s" }}
                  onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.13)"}
                  onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
                  <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                    <div style={{ width: 34, height: 34, borderRadius: 9, background: "rgba(245,158,11,.12)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <Icon size={15} style={{ color: T.amber }} />
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 7, flexWrap: "wrap", marginBottom: 5 }}>
                        <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 5, border: `1px solid rgba(245,158,11,.3)`, color: T.amber, fontWeight: 700 }}>
                          {item.content_type?.replace("_", " ")}
                        </span>
                        {item.blueprint_id && (
                          <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 5, border: `1px solid rgba(124,58,237,.3)`, color: "#a78bfa", fontWeight: 700 }}>Blueprint Applied</span>
                        )}
                        <span style={{ fontSize: 10, color: T.zinc }}>{item.model_used}</span>
                        <span style={{ fontSize: 10, color: T.zinc }}>{item.created_at ? new Date(item.created_at).toLocaleString() : ""}</span>
                      </div>
                      <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8, fontStyle: "italic" }}>"{item.prompt?.substring(0, 120)}"</p>
                      <div style={{ fontSize: 13, color: "#d4d4d8", lineHeight: 1.6, whiteSpace: "pre-wrap", overflow: expanded ? "visible" : "hidden", display: "-webkit-box", WebkitLineClamp: expanded ? "unset" : 4, WebkitBoxOrient: "vertical" }}>
                        {item.content}
                      </div>
                      <div style={{ display: "flex", alignItems: "center", gap: 14, marginTop: 10 }}>
                        <button onClick={() => setExpandedItem(expanded ? null : item.content_id)} data-testid={`expand-content-${item.content_id}`}
                          style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: T.amber, background: "none", border: "none", cursor: "pointer", padding: 0 }}>
                          {expanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                          {expanded ? "Collapse" : "Expand"}
                        </button>
                        <button onClick={() => copyContent(item.content)} data-testid={`copy-content-${item.content_id}`}
                          style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: T.zinc, background: "none", border: "none", cursor: "pointer", padding: 0 }}
                          onMouseEnter={e => e.currentTarget.style.color = "#e4e4e7"}
                          onMouseLeave={e => e.currentTarget.style.color = T.zinc}>
                          <Copy size={11} /> Copy
                        </button>
                        <button onClick={() => deleteContent(item.content_id)} data-testid={`delete-content-${item.content_id}`}
                          style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "rgba(239,68,68,.6)", background: "none", border: "none", cursor: "pointer", padding: 0, marginLeft: "auto" }}
                          onMouseEnter={e => e.currentTarget.style.color = T.red}
                          onMouseLeave={e => e.currentTarget.style.color = "rgba(239,68,68,.6)"}>
                          <Trash2 size={11} /> Delete
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentGenerator;
