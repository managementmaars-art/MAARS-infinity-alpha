import { useState, useEffect, useCallback } from "react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import {
  BookOpen, Upload, Trash2, FileText, Loader2, Search, CheckCircle, XCircle, Clock, File
} from "lucide-react";
import { useAuth, API } from "../App";
import { toast } from "sonner";

const KnowledgeBaseTab = () => {
  const { token } = useAuth();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};

  const [agents, setAgents] = useState([]);
  const [selectedAgent, setSelectedAgent] = useState("");
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    fetchAgents();
  }, []);

  useEffect(() => {
    if (selectedAgent) fetchDocs();
  }, [selectedAgent]);

  const fetchAgents = async () => {
    try {
      const res = await fetch(`${API}/agents`, { headers });
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
        if (data.length > 0) setSelectedAgent(data[0].agent_id);
      }
    } catch { toast.error("Failed to load agents"); }
  };

  const fetchDocs = useCallback(async () => {
    if (!selectedAgent) return;
    setLoading(true);
    try {
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge`, { headers });
      if (res.ok) setDocs(await res.json());
    } catch { toast.error("Failed to load documents"); }
    finally { setLoading(false); }
  }, [selectedAgent]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !selectedAgent) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (res.ok) {
        const data = await res.json();
        toast.success(`"${data.title}" uploaded. Processing...`);
        // Poll for status
        setTimeout(() => fetchDocs(), 3000);
        setTimeout(() => fetchDocs(), 8000);
        setTimeout(() => fetchDocs(), 15000);
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Upload failed");
      }
    } catch { toast.error("Upload failed"); }
    finally { setUploading(false); e.target.value = ""; }
  };

  const handleDelete = async (docId, title) => {
    if (!confirm(`Delete "${title}" and all its data?`)) return;
    try {
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge/${docId}`, {
        method: "DELETE", headers
      });
      if (res.ok) {
        toast.success("Document deleted");
        fetchDocs();
      }
    } catch { toast.error("Delete failed"); }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim() || !selectedAgent) return;
    setSearching(true);
    try {
      const res = await fetch(`${API}/agents/${selectedAgent}/knowledge/search`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery }),
      });
      if (res.ok) {
        const data = await res.json();
        setSearchResults(data.results);
      }
    } catch { toast.error("Search failed"); }
    finally { setSearching(false); }
  };

  const statusIcon = (status) => {
    if (status === "ready") return <CheckCircle className="w-4 h-4 text-emerald-400" />;
    if (status === "processing" || status === "queued") return <Clock className="w-4 h-4 text-amber-400 animate-pulse" />;
    return <XCircle className="w-4 h-4 text-red-400" />;
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const currentAgent = agents.find(a => a.agent_id === selectedAgent);

  return (
    <div className="space-y-6" data-testid="knowledge-base-tab">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white font-['Outfit']">Knowledge Base (RAG)</h2>
          <p className="text-sm text-zinc-400 mt-1">
            Upload documents to give agents access to specific knowledge. They'll cite sources in responses.
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-sm text-zinc-400">Agent:</span>
          <Select value={selectedAgent} onValueChange={setSelectedAgent}>
            <SelectTrigger className="w-[250px] bg-zinc-900/50 border-white/10" data-testid="kb-agent-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {agents.map((a) => (
                <SelectItem key={a.agent_id} value={a.agent_id}>
                  {a.name} — {a.role}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <label className="cursor-pointer">
          <input
            type="file"
            className="hidden"
            accept=".pdf,.txt,.md,.csv,.docx"
            onChange={handleUpload}
            disabled={uploading || !selectedAgent}
          />
          <Button
            asChild
            disabled={uploading}
            className="bg-gradient-to-r from-indigo-500 to-violet-500 hover:from-indigo-600 hover:to-violet-600"
            data-testid="kb-upload-btn"
          >
            <span>
              {uploading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Upload className="w-4 h-4 mr-2" />}
              Upload Document
            </span>
          </Button>
        </label>
      </div>

      {currentAgent && (
        <div className="flex items-center gap-3 p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20">
          <img src={currentAgent.avatar} alt="" className="w-8 h-8 rounded-lg object-cover" />
          <div>
            <span className="text-sm font-medium text-white">{currentAgent.name}</span>
            <span className="text-xs text-zinc-400 ml-2">{docs.filter(d => d.status === "ready").length} documents ready</span>
          </div>
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 text-indigo-400 animate-spin" />
        </div>
      ) : docs.length === 0 ? (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardContent className="flex flex-col items-center py-12">
            <BookOpen className="w-12 h-12 text-zinc-600 mb-3" />
            <p className="text-zinc-400 text-sm">No documents uploaded for this agent yet.</p>
            <p className="text-zinc-500 text-xs mt-1">Upload PDFs, text files, or documents to build the knowledge base.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {docs.map((doc) => (
            <div
              key={doc.doc_id}
              className="flex items-center gap-3 p-3 rounded-lg bg-zinc-800/50 border border-white/5 hover:border-white/10 transition-colors"
              data-testid={`kb-doc-${doc.doc_id}`}
            >
              <div className="flex-shrink-0">
                {doc.file_type === ".pdf" ? (
                  <FileText className="w-8 h-8 text-red-400" />
                ) : (
                  <File className="w-8 h-8 text-zinc-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white truncate">{doc.title}</span>
                  {statusIcon(doc.status)}
                </div>
                <div className="flex items-center gap-3 text-xs text-zinc-500 mt-0.5">
                  <span>{doc.filename}</span>
                  <span>{formatSize(doc.file_size || 0)}</span>
                  {doc.chunk_count > 0 && <span>{doc.chunk_count} chunks</span>}
                  {doc.status === "error" && <span className="text-red-400">{doc.error?.slice(0, 80)}</span>}
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => handleDelete(doc.doc_id, doc.title)}
                className="text-zinc-500 hover:text-red-400"
                data-testid={`kb-delete-${doc.doc_id}`}
              >
                <Trash2 className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      )}

      {docs.length > 0 && (
        <Card className="bg-zinc-900/50 border-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-zinc-300 flex items-center gap-2">
              <Search className="w-4 h-4" /> Test Knowledge Search
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Ask a question to test retrieval..."
                className="bg-zinc-800/50 border-white/10"
                data-testid="kb-search-input"
              />
              <Button
                onClick={handleSearch}
                disabled={searching || !searchQuery.trim()}
                className="bg-indigo-500 hover:bg-indigo-600"
                data-testid="kb-search-btn"
              >
                {searching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              </Button>
            </div>
            {searchResults !== null && (
              <div className="mt-3 space-y-2">
                {searchResults.length === 0 ? (
                  <p className="text-xs text-zinc-500">No relevant results found.</p>
                ) : (
                  searchResults.map((r, i) => (
                    <div key={i} className="p-3 rounded-lg bg-zinc-800/80 border border-white/5">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-medium text-indigo-400">
                          {r.doc_title} {r.pages?.length > 0 && `(Page${r.pages.length > 1 ? 's' : ''} ${r.pages.join(', ')})`}
                        </span>
                        <span className="text-xs text-zinc-500">Score: {r.score}</span>
                      </div>
                      <p className="text-xs text-zinc-300 line-clamp-3">{r.text}</p>
                    </div>
                  ))
                )}
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default KnowledgeBaseTab;
