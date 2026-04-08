import { useState, useCallback } from "react";
import { Search, X, MessageSquare, Loader2 } from "lucide-react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import { API, useAuth } from "../../App";

export const ChatSearch = ({ onSelectChat, onClose }) => {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const handleSearch = useCallback(async () => {
    if (!query || query.length < 2) return;
    setSearching(true);
    try {
      const resp = await fetch(`${API}/chats/search?q=${encodeURIComponent(query)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await resp.json();
      setResults(data);
    } catch {
      setResults({ results: [], total_matches: 0 });
    } finally {
      setSearching(false);
    }
  }, [query, token]);

  return (
    <div className="absolute inset-0 z-50 bg-zinc-950/95 backdrop-blur-sm flex flex-col" data-testid="chat-search-panel">
      <div className="p-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <Search className="w-4 h-4 text-zinc-400 shrink-0" />
          <Input
            value={query}
            onChange={e => setQuery(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleSearch()}
            placeholder="Search messages..."
            className="bg-zinc-900/50 border-white/10 text-sm h-8"
            autoFocus
            data-testid="chat-search-input"
          />
          <Button variant="ghost" size="sm" onClick={onClose} className="h-8 w-8 p-0 text-zinc-400">
            <X className="w-4 h-4" />
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {searching && (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="w-5 h-5 text-indigo-400 animate-spin" />
          </div>
        )}

        {results && !searching && results.results?.length === 0 && (
          <p className="text-zinc-500 text-sm text-center py-8">No results found</p>
        )}

        {results && !searching && results.results?.map(r => (
          <button
            key={r.chat_id}
            onClick={() => { onSelectChat(r.chat_id, r.agent_id); onClose(); }}
            className="w-full text-left p-3 rounded-lg bg-zinc-900/50 border border-white/5 hover:border-red-500/30 transition-all"
            data-testid={`search-result-${r.chat_id}`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-white truncate">{r.title}</span>
              <span className="text-xs text-zinc-500">{r.match_count} match{r.match_count > 1 ? "es" : ""}</span>
            </div>
            {r.matches?.slice(0, 2).map((m, i) => (
              <p key={i} className="text-xs text-zinc-400 mt-1 line-clamp-2">
                <span className="text-zinc-500">{m.role === "user" ? "You" : "Agent"}:</span> {m.snippet}
              </p>
            ))}
          </button>
        ))}

        {!results && !searching && (
          <div className="flex flex-col items-center py-8 text-zinc-500">
            <MessageSquare className="w-8 h-8 mb-2 opacity-30" />
            <p className="text-sm">Search across all your conversations</p>
          </div>
        )}
      </div>

      {results && results.total_matches > 0 && (
        <div className="p-2 border-t border-white/10 text-center">
          <span className="text-xs text-zinc-500">{results.total_matches} matches in {results.results?.length} conversations</span>
        </div>
      )}
    </div>
  );
};
