import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Palette, Image, FileText, Sparkles, Loader2, Clock,
  Eye, Trash2, ChevronDown, ChevronUp, Upload, Link2
} from "lucide-react";
import { toast } from "sonner";

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
    <div className="space-y-6" data-testid="reference-intelligence">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-violet-500/15 flex items-center justify-center">
          <Palette className="w-5 h-5 text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white font-['Outfit']">Universal Reference Intelligence</h1>
          <p className="text-xs text-zinc-500">Analyze images, text, & brands to extract Style Blueprints for content generation</p>
        </div>
      </div>

      {/* Input Area */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-5">
          {/* Type Toggle */}
          <div className="flex gap-2 mb-4">
            {[
              { id: "text", icon: FileText, label: "Text Reference" },
              { id: "image", icon: Image, label: "Image Reference" },
            ].map(t => (
              <button
                key={t.id}
                onClick={() => setRefType(t.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs transition-colors ${
                  refType === t.id ? "bg-violet-500/15 text-violet-400 border border-violet-500/30" : "bg-zinc-800/50 text-zinc-500 border border-white/5 hover:border-white/10"
                }`}
                data-testid={`ref-type-${t.id}`}
              >
                <t.icon className="w-3.5 h-3.5" />
                {t.label}
              </button>
            ))}
          </div>

          {/* Text Input */}
          {refType === "text" && (
            <div>
              <p className="text-sm text-zinc-400 mb-2">Paste reference text (marketing copy, brand voice, article, etc.)</p>
              <textarea
                value={textContent}
                onChange={e => setTextContent(e.target.value)}
                placeholder="Paste the reference text you want to analyze for style, tone, and brand elements..."
                className="w-full h-40 bg-zinc-800/50 border border-white/10 rounded-lg p-3 text-sm text-white placeholder-zinc-600 resize-none focus:outline-none focus:border-violet-500/40"
                data-testid="ref-text-input"
              />
            </div>
          )}

          {/* Image URL Input */}
          {refType === "image" && (
            <div>
              <p className="text-sm text-zinc-400 mb-2">Enter an image URL for visual analysis</p>
              <div className="flex gap-2">
                <div className="flex-1 relative">
                  <Link2 className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-zinc-600" />
                  <Input
                    value={imageUrl}
                    onChange={e => setImageUrl(e.target.value)}
                    placeholder="https://example.com/image.jpg"
                    className="bg-zinc-800/50 border-white/10 text-white text-sm pl-10"
                    data-testid="ref-image-input"
                  />
                </div>
              </div>
              {imageUrl && (
                <div className="mt-3 rounded-lg overflow-hidden border border-white/10 max-h-48">
                  <img src={imageUrl} alt="Preview" className="w-full h-full object-contain" onError={e => e.target.style.display = 'none'} />
                </div>
              )}
            </div>
          )}

          <Button
            onClick={analyzeReference}
            disabled={analyzing}
            className="mt-4 bg-violet-600 hover:bg-violet-500 text-white"
            data-testid="analyze-btn"
          >
            {analyzing ? (
              <><Loader2 className="w-4 h-4 animate-spin mr-2" />Analyzing...</>
            ) : (
              <><Sparkles className="w-4 h-4 mr-2" />Extract Style Blueprint</>
            )}
          </Button>
          {analyzing && <p className="text-xs text-violet-400 mt-2 animate-pulse">AI is analyzing the reference material... This may take 10-20 seconds.</p>}
        </CardContent>
      </Card>

      {/* Analysis History */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-zinc-500" />Analysis History
          <Badge variant="outline" className="border-white/10 text-zinc-500 text-[9px] ml-auto">{history.length} analyses</Badge>
        </h2>

        {loading ? (
          <div className="flex items-center justify-center py-12"><div className="w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" /></div>
        ) : history.length > 0 ? (
          <div className="space-y-3">
            {history.map((ref, i) => (
              <Card key={ref.ref_id || i} className="bg-zinc-900/50 border-white/5 hover:border-white/10 transition-all">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${
                      ref.type === "image" ? "bg-pink-500/15" : "bg-cyan-500/15"
                    }`}>
                      {ref.type === "image" ? <Image className="w-4 h-4 text-pink-400" /> : <FileText className="w-4 h-4 text-cyan-400" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="outline" className={`text-[9px] ${ref.type === "image" ? "border-pink-500/30 text-pink-400" : "border-cyan-500/30 text-cyan-400"}`}>
                          {ref.type}
                        </Badge>
                        <span className="text-[10px] text-zinc-600">{ref.created_at ? new Date(ref.created_at).toLocaleString() : ""}</span>
                      </div>
                      <p className="text-xs text-zinc-400 truncate mb-2">{ref.source?.substring(0, 150)}</p>

                      {/* Expandable Analysis */}
                      <button
                        onClick={() => setExpandedRef(expandedRef === ref.ref_id ? null : ref.ref_id)}
                        className="flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300"
                        data-testid={`expand-ref-${ref.ref_id}`}
                      >
                        <Eye className="w-3 h-3" />
                        {expandedRef === ref.ref_id ? "Hide" : "View"} Style Blueprint
                        {expandedRef === ref.ref_id ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                      </button>

                      {expandedRef === ref.ref_id && (
                        <div className="mt-3 p-3 bg-zinc-800/50 rounded-lg border border-white/5">
                          <pre className="text-xs text-zinc-300 whitespace-pre-wrap font-mono leading-relaxed overflow-auto max-h-96">
                            {typeof ref.analysis === "string" ? ref.analysis : JSON.stringify(ref.analysis, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-16 border border-dashed border-white/10 rounded-xl">
            <Palette className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
            <p className="text-sm text-zinc-400">No analyses yet. Upload a reference to get started.</p>
            <p className="text-xs text-zinc-600 mt-1">Analyze images, brand materials, or text samples to extract Style Blueprints</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReferenceIntelligence;
