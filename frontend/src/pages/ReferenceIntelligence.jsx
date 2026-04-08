import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import {
  Palette, Image, FileText, Sparkles, Clock,
  Eye, ChevronDown, ChevronUp, Link2
} from "lucide-react";
import { toast } from "sonner";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  violet: "#a78bfa",
  cyan: "#22d3ee",
  pink: "#f472b6",
  zinc: "#71717a",
};

const STYLES = `
@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} }
@keyframes spin { to{transform:rotate(360deg)} }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
`;

const formInput = {
  background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}`,
  borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13,
  outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box",
  transition: "border-color .2s",
};

const ReferenceIntelligence = () => {
  const { token } = useAuth();
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [refType, setRefType] = useState("text");
  const [textContent, setTextContent] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [expandedRef, setExpandedRef] = useState(null);

  const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API}/reference/history`, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) setHistory((await res.json()).items || []);
    } catch {} finally { setLoading(false); }
  }, [token]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const analyzeReference = async () => {
    if (refType === "text" && !textContent.trim()) return toast.error("Enter text content to analyze");
    if (refType === "image" && !imageUrl.trim()) return toast.error("Enter an image URL to analyze");

    setAnalyzing(true);
    try {
      const body = refType === "text"
        ? { type: "text", content: textContent }
        : { type: "image", image_url: imageUrl };

      const res = await fetch(`${API}/reference/analyze`, {
        method: "POST", headers, body: JSON.stringify(body),
      });

      if (res.ok) {
        const result = await res.json();
        setHistory(prev => [result, ...prev]);
        setTextContent("");
        setImageUrl("");
        toast.success("Reference analyzed! Style Blueprint created.");
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Analysis failed");
      }
    } catch { toast.error("Error analyzing reference"); }
    finally { setAnalyzing(false); }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 22, animation: "fadeUp .4s ease" }} data-testid="reference-intelligence">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{ width: 40, height: 40, borderRadius: 12, background: "rgba(167,139,250,.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
          <Palette size={20} style={{ color: T.violet }} />
        </div>
        <div>
          <h1 style={{ fontFamily: "'Outfit',sans-serif", fontSize: 20, fontWeight: 700, color: "#fff", margin: 0 }}>Universal Reference Intelligence</h1>
          <p style={{ fontSize: 11, color: T.zinc, margin: 0 }}>Analyze images, text, & brands to extract Style Blueprints for content generation</p>
        </div>
      </div>

      {/* Input Area */}
      <div style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 14, padding: "18px 20px" }}>
        {/* Type Toggle */}
        <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
          {[
            { id: "text", icon: FileText, label: "Text Reference" },
            { id: "image", icon: Image, label: "Image Reference" },
          ].map(t => (
            <button key={t.id} onClick={() => setRefType(t.id)} data-testid={`ref-type-${t.id}`}
              style={{ display: "flex", alignItems: "center", gap: 7, padding: "7px 14px", borderRadius: 9, border: `1px solid ${refType === t.id ? "rgba(167,139,250,.4)" : T.border}`, background: refType === t.id ? "rgba(167,139,250,.12)" : "transparent", color: refType === t.id ? T.violet : T.zinc, fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all .2s" }}>
              <t.icon size={13} /> {t.label}
            </button>
          ))}
        </div>

        {refType === "text" && (
          <div>
            <p style={{ fontSize: 12, color: T.zinc, marginBottom: 8 }}>Paste reference text (marketing copy, brand voice, article, etc.)</p>
            <textarea
              value={textContent} onChange={e => setTextContent(e.target.value)}
              placeholder="Paste the reference text you want to analyze for style, tone, and brand elements..."
              style={{ ...formInput, height: 160, resize: "vertical", padding: "10px 12px" }}
              data-testid="ref-text-input"
              onFocus={e => e.target.style.borderColor = "rgba(167,139,250,.5)"}
              onBlur={e => e.target.style.borderColor = T.border}
            />
          </div>
        )}

        {refType === "image" && (
          <div>
            <p style={{ fontSize: 12, color: T.zinc, marginBottom: 8 }}>Enter an image URL for visual analysis</p>
            <div style={{ position: "relative" }}>
              <Link2 size={14} style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: T.zinc }} />
              <input
                value={imageUrl} onChange={e => setImageUrl(e.target.value)}
                placeholder="https://example.com/image.jpg"
                style={{ ...formInput, paddingLeft: 34 }} data-testid="ref-image-input"
                onFocus={e => e.target.style.borderColor = "rgba(167,139,250,.5)"}
                onBlur={e => e.target.style.borderColor = T.border}
              />
            </div>
            {imageUrl && (
              <div style={{ marginTop: 12, borderRadius: 10, overflow: "hidden", border: `1px solid ${T.border}`, maxHeight: 192 }}>
                <img src={imageUrl} alt="Preview" style={{ width: "100%", height: "100%", objectFit: "contain" }} onError={e => e.target.style.display = "none"} />
              </div>
            )}
          </div>
        )}

        <button onClick={analyzeReference} disabled={analyzing} data-testid="analyze-btn"
          style={{ display: "inline-flex", alignItems: "center", gap: 8, marginTop: 14, padding: "9px 18px", borderRadius: 10, border: "none", background: analyzing ? "rgba(167,139,250,.25)" : "rgba(167,139,250,.85)", color: analyzing ? T.violet : "#030712", fontSize: 13, fontWeight: 700, cursor: analyzing ? "not-allowed" : "pointer" }}>
          {analyzing
            ? <div style={{ width: 14, height: 14, border: "2px solid rgba(167,139,250,.4)", borderTopColor: T.violet, borderRadius: "50%", animation: "spin .8s linear infinite" }} />
            : <Sparkles size={14} />}
          {analyzing ? "Analyzing..." : "Extract Style Blueprint"}
        </button>
        {analyzing && <p style={{ fontSize: 11, color: T.violet, marginTop: 8, animation: "pulse 1.5s ease infinite" }}>AI is analyzing the reference material... This may take 10–20 seconds.</p>}
      </div>

      {/* Analysis History */}
      <div>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
          <Clock size={12} style={{ color: T.zinc }} />
          <span style={{ fontSize: 10, fontWeight: 700, color: T.zinc, textTransform: "uppercase", letterSpacing: "0.1em" }}>Analysis History</span>
          <span style={{ fontSize: 10, padding: "1px 8px", borderRadius: 20, border: `1px solid ${T.border}`, color: T.zinc, marginLeft: "auto" }}>{history.length} analyses</span>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "48px 0" }}>
            <div style={{ width: 22, height: 22, border: `2px solid ${T.violet}`, borderTopColor: "transparent", borderRadius: "50%", animation: "spin .8s linear infinite" }} />
          </div>
        ) : history.length > 0 ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {history.map((ref, i) => (
              <div key={ref.ref_id || i} style={{ background: T.glass, border: `1px solid ${T.border}`, borderRadius: 12, padding: "14px 16px", transition: "border-color .2s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,.13)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>
                <div style={{ display: "flex", alignItems: "flex-start", gap: 12 }}>
                  <div style={{ width: 32, height: 32, borderRadius: 9, background: ref.type === "image" ? "rgba(244,114,182,.12)" : "rgba(34,211,238,.12)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    {ref.type === "image" ? <Image size={14} style={{ color: T.pink }} /> : <FileText size={14} style={{ color: T.cyan }} />}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
                      <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 8px", borderRadius: 20, border: `1px solid ${ref.type === "image" ? "rgba(244,114,182,.3)" : "rgba(34,211,238,.3)"}`, color: ref.type === "image" ? T.pink : T.cyan }}>{ref.type}</span>
                      <span style={{ fontSize: 10, color: "rgba(113,113,122,.7)" }}>{ref.created_at ? new Date(ref.created_at).toLocaleString() : ""}</span>
                    </div>
                    <p style={{ fontSize: 11, color: T.zinc, marginBottom: 8, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{ref.source?.substring(0, 150)}</p>

                    <button onClick={() => setExpandedRef(expandedRef === ref.ref_id ? null : ref.ref_id)} data-testid={`expand-ref-${ref.ref_id}`}
                      style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 11, color: T.violet, background: "none", border: "none", cursor: "pointer", padding: 0 }}>
                      <Eye size={11} />
                      {expandedRef === ref.ref_id ? "Hide" : "View"} Style Blueprint
                      {expandedRef === ref.ref_id ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
                    </button>

                    {expandedRef === ref.ref_id && (
                      <div style={{ marginTop: 10, padding: "12px 14px", borderRadius: 9, background: "rgba(255,255,255,.04)", border: `1px solid ${T.border}` }}>
                        <pre style={{ fontSize: 11, color: "#d4d4d8", whiteSpace: "pre-wrap", fontFamily: "monospace", lineHeight: 1.6, overflow: "auto", maxHeight: 384, margin: 0 }}>
                          {typeof ref.analysis === "string" ? ref.analysis : JSON.stringify(ref.analysis, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ textAlign: "center", padding: "64px 20px", border: `1px dashed ${T.border}`, borderRadius: 14 }}>
            <Palette size={48} style={{ color: "rgba(255,255,255,.07)", margin: "0 auto 12px" }} />
            <p style={{ fontSize: 13, color: T.zinc, margin: 0 }}>No analyses yet. Upload a reference to get started.</p>
            <p style={{ fontSize: 11, color: "rgba(113,113,122,.5)", marginTop: 5 }}>Analyze images, brand materials, or text samples to extract Style Blueprints</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReferenceIntelligence;
