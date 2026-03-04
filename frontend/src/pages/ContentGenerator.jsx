import { useState, useEffect, useCallback } from "react";
import { useAuth, API } from "../App";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import {
  Sparkles, Loader2, Clock, Copy, Trash2, ChevronDown, ChevronUp,
  FileText, Palette, Zap, Mail, Megaphone, Newspaper, PenTool
} from "lucide-react";
import { toast } from "sonner";

const TYPE_ICONS = {
  marketing_copy: Megaphone,
  social_post: Zap,
  email_campaign: Mail,
  blog_article: Newspaper,
  ad_copy: Megaphone,
  press_release: FileText,
  brand_guidelines: Palette,
  custom: PenTool,
};

const ContentGenerator = () => {
  const { token } = useAuth();
  const [contentTypes, setContentTypes] = useState([]);
  const [blueprints, setBlueprints] = useState([]);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [expandedItem, setExpandedItem] = useState(null);

  // Form state
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
        method: "POST",
        headers,
        body: JSON.stringify({
          content_type: selectedType,
          blueprint_id: selectedBlueprint,
          prompt,
          length,
          tone_override: toneOverride,
        }),
      });
      if (res.ok) {
        const result = await res.json();
        setHistory(prev => [result, ...prev]);
        toast.success("Content generated!");
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Generation failed");
      }
    } catch { toast.error("Error generating content"); }
    finally { setGenerating(false); }
  };

  const copyContent = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  const deleteContent = async (contentId) => {
    try {
      await fetch(`${API}/content/${contentId}`, { method: "DELETE", headers });
      setHistory(prev => prev.filter(h => h.content_id !== contentId));
      toast.success("Content deleted");
    } catch {}
  };

  if (loading) return (
    <div className="flex items-center justify-center py-20">
      <div className="w-6 h-6 border-2 border-violet-400 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="space-y-6" data-testid="content-generator">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-amber-500/15 flex items-center justify-center">
          <PenTool className="w-5 h-5 text-amber-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white font-['Outfit']">Content Generator</h1>
          <p className="text-xs text-zinc-500">Generate on-brand content using Style Blueprints from Reference Intelligence</p>
        </div>
      </div>

      {/* Generator Form */}
      <Card className="bg-zinc-900/50 border-white/10">
        <CardContent className="p-5 space-y-4">
          {/* Content Type */}
          <div>
            <label className="text-xs text-zinc-400 mb-2 block">Content Type</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {contentTypes.map(t => {
                const Icon = TYPE_ICONS[t.id] || PenTool;
                return (
                  <button
                    key={t.id}
                    onClick={() => setSelectedType(t.id)}
                    className={`p-2.5 rounded-lg text-left transition-all ${
                      selectedType === t.id
                        ? "bg-amber-500/10 border border-amber-500/30 text-amber-400"
                        : "bg-zinc-800/50 border border-white/5 text-zinc-400 hover:border-white/10"
                    }`}
                    data-testid={`content-type-${t.id}`}
                  >
                    <Icon className="w-4 h-4 mb-1" />
                    <p className="text-xs font-medium">{t.label}</p>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Style Blueprint Selector */}
          <div>
            <label className="text-xs text-zinc-400 mb-2 block">Style Blueprint (optional)</label>
            <select
              value={selectedBlueprint}
              onChange={e => setSelectedBlueprint(e.target.value)}
              className="w-full bg-zinc-800/50 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-amber-500/40"
              data-testid="blueprint-select"
            >
              <option value="">No blueprint — use default style</option>
              {blueprints.map(bp => (
                <option key={bp.ref_id} value={bp.ref_id}>
                  [{bp.type}] {bp.source?.substring(0, 80)}
                </option>
              ))}
            </select>
            {selectedBlueprint && (
              <p className="text-[10px] text-amber-400 mt-1">
                Content will match the tone and style from this reference
              </p>
            )}
          </div>

          {/* Prompt */}
          <div>
            <label className="text-xs text-zinc-400 mb-2 block">What content do you need?</label>
            <textarea
              value={prompt}
              onChange={e => setPrompt(e.target.value)}
              placeholder="Describe the content you want... e.g., 'Write a LinkedIn post announcing our new AI product launch targeting enterprise CTOs'"
              className="w-full h-28 bg-zinc-800/50 border border-white/10 rounded-lg p-3 text-sm text-white placeholder-zinc-600 resize-none focus:outline-none focus:border-amber-500/40"
              data-testid="content-prompt"
            />
          </div>

          {/* Options Row */}
          <div className="flex gap-3 flex-wrap">
            {/* Length */}
            <div>
              <label className="text-xs text-zinc-400 mb-1.5 block">Length</label>
              <div className="flex gap-1.5">
                {["short", "medium", "long"].map(l => (
                  <button
                    key={l}
                    onClick={() => setLength(l)}
                    className={`px-3 py-1.5 rounded-md text-xs transition-colors ${
                      length === l
                        ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                        : "bg-zinc-800/50 text-zinc-500 border border-white/5"
                    }`}
                    data-testid={`length-${l}`}
                  >
                    {l}
                  </button>
                ))}
              </div>
            </div>

            {/* Tone Override */}
            <div className="flex-1 min-w-[200px]">
              <label className="text-xs text-zinc-400 mb-1.5 block">Tone Override (optional)</label>
              <Input
                value={toneOverride}
                onChange={e => setToneOverride(e.target.value)}
                placeholder="e.g., formal, playful, urgent..."
                className="bg-zinc-800/50 border-white/10 text-white text-xs"
                data-testid="tone-input"
              />
            </div>
          </div>

          {/* Generate Button */}
          <Button
            onClick={generate}
            disabled={generating}
            className="bg-amber-600 hover:bg-amber-500 text-white"
            data-testid="generate-btn"
          >
            {generating ? (
              <><Loader2 className="w-4 h-4 animate-spin mr-2" />Generating...</>
            ) : (
              <><Sparkles className="w-4 h-4 mr-2" />Generate Content</>
            )}
          </Button>
          {generating && <p className="text-xs text-amber-400 animate-pulse">AI is crafting your content... This may take 10-20 seconds.</p>}
        </CardContent>
      </Card>

      {/* Generated Content History */}
      <div>
        <h2 className="text-sm font-medium text-zinc-400 mb-3 uppercase tracking-wider flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-zinc-500" />Generated Content
          <Badge variant="outline" className="border-white/10 text-zinc-500 text-[9px] ml-auto">{history.length} items</Badge>
        </h2>

        {history.length > 0 ? (
          <div className="space-y-3">
            {history.map((item) => {
              const Icon = TYPE_ICONS[item.content_type] || PenTool;
              return (
                <Card key={item.content_id} className="bg-zinc-900/50 border-white/5 hover:border-white/10 transition-all">
                  <CardContent className="p-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-500/15 flex items-center justify-center shrink-0">
                        <Icon className="w-4 h-4 text-amber-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1 flex-wrap">
                          <Badge variant="outline" className="text-[9px] border-amber-500/30 text-amber-400">
                            {item.content_type?.replace("_", " ")}
                          </Badge>
                          {item.blueprint_id && (
                            <Badge variant="outline" className="text-[9px] border-violet-500/30 text-violet-400">
                              Blueprint Applied
                            </Badge>
                          )}
                          <span className="text-[10px] text-zinc-600">{item.model_used}</span>
                          <span className="text-[10px] text-zinc-600">{item.created_at ? new Date(item.created_at).toLocaleString() : ""}</span>
                        </div>
                        <p className="text-xs text-zinc-400 mb-2 italic">"{item.prompt?.substring(0, 120)}"</p>

                        {/* Expand/collapse content */}
                        <div className={`text-sm text-zinc-200 whitespace-pre-wrap leading-relaxed ${expandedItem === item.content_id ? "" : "line-clamp-4"}`}>
                          {item.content}
                        </div>

                        <div className="flex items-center gap-2 mt-3">
                          <button
                            onClick={() => setExpandedItem(expandedItem === item.content_id ? null : item.content_id)}
                            className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300"
                            data-testid={`expand-content-${item.content_id}`}
                          >
                            {expandedItem === item.content_id ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                            {expandedItem === item.content_id ? "Collapse" : "Expand"}
                          </button>
                          <button
                            onClick={() => copyContent(item.content)}
                            className="flex items-center gap-1 text-xs text-zinc-500 hover:text-zinc-300"
                            data-testid={`copy-content-${item.content_id}`}
                          >
                            <Copy className="w-3 h-3" />Copy
                          </button>
                          <button
                            onClick={() => deleteContent(item.content_id)}
                            className="flex items-center gap-1 text-xs text-red-500/70 hover:text-red-400 ml-auto"
                            data-testid={`delete-content-${item.content_id}`}
                          >
                            <Trash2 className="w-3 h-3" />Delete
                          </button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        ) : (
          <div className="text-center py-16 border border-dashed border-white/10 rounded-xl">
            <PenTool className="w-12 h-12 text-zinc-600 mx-auto mb-3" />
            <p className="text-sm text-zinc-400">No content generated yet</p>
            <p className="text-xs text-zinc-600 mt-1">Select a content type, optionally pick a Style Blueprint, and describe what you need</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ContentGenerator;
