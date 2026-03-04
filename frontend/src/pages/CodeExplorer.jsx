import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth, API } from "../App";
import {
  Folder, FolderOpen, FileCode, FileText, FileJson, Search,
  ChevronRight, ChevronDown, Copy, Check, Download, Hash,
  Terminal, Code, File as FileIcon, Loader2
} from "lucide-react";

const LANG_COLORS = {
  python: "#3572A5",
  javascript: "#f1e05a",
  typescript: "#3178c6",
  json: "#292929",
  html: "#e34c26",
  css: "#563d7c",
  markdown: "#083fa1",
  yaml: "#cb171e",
  shell: "#89e051",
  text: "#6e7781",
  sql: "#e38c00",
  toml: "#9c4121",
  ini: "#d1dbe0",
};

const LANG_ICONS = {
  python: Terminal,
  javascript: Code,
  typescript: Code,
  json: FileJson,
  html: FileCode,
  css: FileCode,
  markdown: FileText,
  shell: Terminal,
};

const TreeNode = ({ node, depth, onSelect, selectedPath }) => {
  const [expanded, setExpanded] = useState(depth < 1);
  const isDir = node.type === "directory";
  const isSelected = selectedPath === node.path;

  if (isDir) {
    return (
      <div>
        <button
          onClick={() => setExpanded(e => !e)}
          className={`w-full flex items-center gap-1.5 py-1 px-2 text-left text-[13px] rounded-md transition-colors hover:bg-white/5 ${
            isSelected ? "bg-indigo-500/10 text-indigo-400" : "text-zinc-400"
          }`}
          style={{ paddingLeft: `${depth * 16 + 8}px` }}
          data-testid={`tree-dir-${node.path}`}
        >
          {expanded ? (
            <ChevronDown className="w-3.5 h-3.5 shrink-0 text-zinc-600" />
          ) : (
            <ChevronRight className="w-3.5 h-3.5 shrink-0 text-zinc-600" />
          )}
          {expanded ? (
            <FolderOpen className="w-4 h-4 shrink-0 text-amber-500" />
          ) : (
            <Folder className="w-4 h-4 shrink-0 text-amber-600" />
          )}
          <span className="truncate">{node.name}</span>
          <span className="ml-auto text-[10px] text-zinc-700">{node.count}</span>
        </button>
        {expanded && node.children?.map(child => (
          <TreeNode
            key={child.path}
            node={child}
            depth={depth + 1}
            onSelect={onSelect}
            selectedPath={selectedPath}
          />
        ))}
      </div>
    );
  }

  const LangIcon = LANG_ICONS[node.language] || FileIcon;
  const langColor = LANG_COLORS[node.language] || "#6e7781";

  return (
    <button
      onClick={() => onSelect(node)}
      className={`w-full flex items-center gap-1.5 py-1 px-2 text-left text-[13px] rounded-md transition-colors hover:bg-white/5 ${
        isSelected ? "bg-indigo-500/10 text-indigo-300" : "text-zinc-400"
      }`}
      style={{ paddingLeft: `${depth * 16 + 8}px` }}
      data-testid={`tree-file-${node.path}`}
    >
      <span className="w-3.5" />
      <LangIcon className="w-4 h-4 shrink-0" style={{ color: langColor }} />
      <span className="truncate">{node.name}</span>
      <span className="ml-auto text-[10px] text-zinc-700">
        {node.size > 1024 ? `${(node.size / 1024).toFixed(1)}KB` : `${node.size}B`}
      </span>
    </button>
  );
};

export default function CodeExplorer() {
  const { token } = useAuth();
  const [tree, setTree] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileLoading, setFileLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const searchTimeout = useRef(null);
  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    fetch(`${API}/admin/code/tree`, { headers })
      .then(r => r.json())
      .then(data => setTree(data.tree || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [token]);

  const handleFileSelect = useCallback(async (node) => {
    setSelectedFile(node);
    setFileLoading(true);
    try {
      const res = await fetch(`${API}/admin/code/file?path=${encodeURIComponent(node.path)}`, { headers });
      if (res.ok) {
        const data = await res.json();
        setFileContent(data);
      }
    } catch {}
    setFileLoading(false);
  }, [token]);

  const handleSearch = useCallback((q) => {
    setSearchQuery(q);
    if (searchTimeout.current) clearTimeout(searchTimeout.current);
    if (!q.trim()) {
      setSearchResults(null);
      return;
    }
    searchTimeout.current = setTimeout(async () => {
      try {
        const res = await fetch(`${API}/admin/code/search?q=${encodeURIComponent(q)}`, { headers });
        if (res.ok) {
          const data = await res.json();
          setSearchResults(data.results || []);
        }
      } catch {}
    }, 300);
  }, [token]);

  const handleCopy = () => {
    if (fileContent?.content) {
      navigator.clipboard.writeText(fileContent.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const totalFiles = tree.reduce((sum, node) =>
    node.type === "file" ? sum + 1 : sum + (node.count || 0), 0
  );

  return (
    <div className="space-y-4" data-testid="code-explorer-page">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit']" data-testid="code-explorer-title">
            Code Explorer
          </h1>
          <p className="text-sm text-zinc-500 mt-0.5">
            Browse the entire MAARS Command codebase ({totalFiles} files)
          </p>
        </div>
      </div>

      <div className="flex gap-4 h-[calc(100vh-180px)]">
        {/* File Tree Panel */}
        <div className="w-72 shrink-0 bg-zinc-900/50 border border-white/5 rounded-xl flex flex-col overflow-hidden" data-testid="file-tree-panel">
          {/* Search */}
          <div className="p-2 border-b border-white/5">
            <div className="flex items-center gap-2 px-2.5 py-1.5 bg-zinc-800/50 rounded-lg border border-white/5">
              <Search className="w-3.5 h-3.5 text-zinc-500" />
              <input
                value={searchQuery}
                onChange={e => handleSearch(e.target.value)}
                placeholder="Search files..."
                className="flex-1 bg-transparent text-xs text-white placeholder-zinc-600 outline-none"
                data-testid="code-search-input"
              />
            </div>
          </div>

          {/* Tree / Search Results */}
          <div className="flex-1 overflow-y-auto py-1 scrollbar-thin scrollbar-thumb-zinc-700 scrollbar-track-transparent">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
              </div>
            ) : searchResults ? (
              searchResults.length === 0 ? (
                <p className="text-xs text-zinc-600 text-center py-8">No files matching "{searchQuery}"</p>
              ) : (
                searchResults.map(r => {
                  const LIcon = LANG_ICONS[r.language] || FileIcon;
                  const lc = LANG_COLORS[r.language] || "#6e7781";
                  return (
                    <button
                      key={r.path}
                      onClick={() => handleFileSelect(r)}
                      className={`w-full flex items-center gap-2 px-3 py-1.5 text-left text-[12px] hover:bg-white/5 ${
                        selectedFile?.path === r.path ? "bg-indigo-500/10 text-indigo-300" : "text-zinc-400"
                      }`}
                      data-testid={`search-result-${r.name}`}
                    >
                      <LIcon className="w-3.5 h-3.5 shrink-0" style={{ color: lc }} />
                      <div className="min-w-0">
                        <p className="truncate">{r.name}</p>
                        <p className="text-[10px] text-zinc-600 truncate">{r.path}</p>
                      </div>
                    </button>
                  );
                })
              )
            ) : (
              tree.map(node => (
                <TreeNode
                  key={node.path}
                  node={node}
                  depth={0}
                  onSelect={handleFileSelect}
                  selectedPath={selectedFile?.path}
                />
              ))
            )}
          </div>
        </div>

        {/* Code Viewer Panel */}
        <div className="flex-1 bg-zinc-900/50 border border-white/5 rounded-xl flex flex-col overflow-hidden" data-testid="code-viewer-panel">
          {fileContent ? (
            <>
              {/* File header */}
              <div className="flex items-center gap-3 px-4 py-2.5 border-b border-white/5 bg-zinc-900/80">
                <div className="flex items-center gap-2 min-w-0">
                  <div
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: LANG_COLORS[fileContent.language] || "#6e7781" }}
                  />
                  <span className="text-sm text-white font-medium truncate">{fileContent.name}</span>
                  <span className="text-[11px] text-zinc-600">{fileContent.path}</span>
                </div>
                <div className="ml-auto flex items-center gap-2 shrink-0">
                  <span className="text-[10px] text-zinc-600">
                    {fileContent.lines} lines | {fileContent.size > 1024 ? `${(fileContent.size / 1024).toFixed(1)} KB` : `${fileContent.size} B`}
                  </span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-zinc-800 text-zinc-500 border border-white/5">
                    {fileContent.language}
                  </span>
                  <button
                    onClick={handleCopy}
                    className="p-1.5 rounded-md hover:bg-white/10 text-zinc-500 hover:text-white transition-colors"
                    title="Copy file content"
                    data-testid="copy-file-btn"
                  >
                    {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Code content */}
              <div className="flex-1 overflow-auto" data-testid="code-content">
                {fileLoading ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-5 h-5 text-zinc-500 animate-spin" />
                  </div>
                ) : (
                  <pre className="text-[12px] leading-5 font-mono">
                    <table className="w-full">
                      <tbody>
                        {fileContent.content.split("\n").map((line, i) => (
                          <tr key={i} className="hover:bg-white/[0.02]">
                            <td className="px-3 py-0 text-right text-zinc-700 select-none w-12 align-top sticky left-0 bg-zinc-900/90">
                              {i + 1}
                            </td>
                            <td className="px-3 py-0 text-zinc-300 whitespace-pre overflow-x-auto">
                              {line || " "}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </pre>
                )}
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-zinc-600">
              <FileCode className="w-12 h-12 mb-3 text-zinc-700" />
              <p className="text-sm">Select a file to view its contents</p>
              <p className="text-xs text-zinc-700 mt-1">Browse the tree or search for files</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
