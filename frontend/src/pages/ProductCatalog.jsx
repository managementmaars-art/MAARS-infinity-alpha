import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Card, CardContent } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Badge } from "../components/ui/badge";
import {
  Package, Search, Plus, RefreshCw, Trash2, Video, FileText, Share2,
  Megaphone, ChevronLeft, Loader2, ExternalLink, Clock, Scan, Bot,
  LayoutDashboard, MessageSquare, Users, ListTodo, BarChart3, Settings,
  Shield, LogOut, Menu, X
} from "lucide-react";

export default function ProductCatalog() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [generating, setGenerating] = useState(null);
  const [generatedContent, setGeneratedContent] = useState(null);
  const [rescanning, setRescanning] = useState(null);
    const [showImport, setShowImport] = useState(false);
  const [importFile, setImportFile] = useState(null);
  const [importing, setImporting] = useState(false);
  const [batchProgress, setBatchProgress] = useState(null);

  const fetchProducts = useCallback(async () => {
    try {
      const res = await fetch(`${API}/products`, { headers });
      if (res.ok) {
        const data = await res.json();
        setProducts(data.products || []);
      }
    } catch {}
    setLoading(false);
  }, [token]);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const deleteProduct = async (productId) => {
    try {
      const res = await fetch(`${API}/products/${productId}`, { method: "DELETE", headers });
      if (res.ok) {
        setProducts(prev => prev.filter(p => p.product_id !== productId));
        if (selectedProduct?.product_id === productId) setSelectedProduct(null);
        toast.success("Product removed");
      }
    } catch { toast.error("Failed to delete"); }
  };

  const rescanProduct = async (productId) => {
    setRescanning(productId);
    try {
      const res = await fetch(`${API}/products/${productId}/rescan`, { method: "POST", headers });
      if (res.ok) {
        const updated = await res.json();
        setProducts(prev => prev.map(p => p.product_id === productId ? updated : p));
        if (selectedProduct?.product_id === productId) setSelectedProduct(updated);
        toast.success("Product re-scanned with latest data");
      } else toast.error("Re-scan failed");
    } catch { toast.error("Re-scan failed"); }
    setRescanning(null);
  };

  const generateContent = async (productId, contentType) => {
    setGenerating(contentType);
    setGeneratedContent(null);
    try {
      const res = await fetch(`${API}/products/${productId}/generate`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ content_type: contentType })
      });
      if (res.ok) {
        const data = await res.json();
        setGeneratedContent({ type: contentType, content: data.content });
        toast.success("Content generated!");
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Generation failed");
      }
    } catch { toast.error("Generation failed"); }
    setGenerating(null);
  };

  const handleBatchImport = async () => {
    if (!importFile) return;
    setImporting(true);
    try {
      const formData = new FormData();
      formData.append("file", importFile);
      const res = await fetch(`${API}/products/batch-import`, {
        method: "POST",
        headers,
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        toast.success(`Batch import started: ${data.total} products`);
        setBatchProgress({ batch_id: data.batch_id, total: data.total, status: "processing", items: [] });
        setShowImport(false);
        setImportFile(null);
        pollBatch(data.batch_id);
      } else {
        const err = await res.json().catch(() => ({}));
        toast.error(err.detail || "Import failed");
      }
    } catch { toast.error("Import failed"); }
    setImporting(false);
  };

  const pollBatch = (batchId) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API}/products/batch/${batchId}`, { headers });
        if (res.ok) {
          const data = await res.json();
          setBatchProgress(data);
          if (data.status === "complete") {
            clearInterval(interval);
            fetchProducts();
            toast.success(`Import complete: ${data.completed} products scanned`);
          }
        }
      } catch {}
    }, 3000);
  };

  const filtered = products.filter(p =>
    !searchQuery || p.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    p.brand?.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const contentTypes = [
    { key: "video", label: "Video Prompt", icon: Video, color: "from-red-500 to-rose-500" },
    { key: "ad_copy", label: "Ad Copy", icon: FileText, color: "from-blue-500 to-indigo-500" },
    { key: "social_post", label: "Social Posts", icon: Share2, color: "from-purple-500 to-violet-500" },
    { key: "full_campaign", label: "Full Campaign", icon: Megaphone, color: "from-amber-500 to-orange-500" },
  ];

  return (
    <div data-testid="products-page">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h1 className="text-2xl font-bold text-white font-['Outfit']" data-testid="products-title">Product Catalog</h1>
              <p className="text-zinc-400 text-sm mt-1">{products.length} product{products.length !== 1 ? "s" : ""} saved</p>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setShowImport(true)} variant="outline" className="border-white/10 text-zinc-300" data-testid="import-btn">
                <Plus className="w-4 h-4 mr-2" />Import CSV
              </Button>
              <Button onClick={() => navigate("/chat")} className="bg-gradient-to-r from-indigo-500 to-violet-500" data-testid="scan-new-btn">
                <Scan className="w-4 h-4 mr-2" />Scan New Product
              </Button>
            </div>
          </div>

          {/* Search */}
          <div className="relative mb-6">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <Input
              placeholder="Search products..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              className="pl-10 bg-zinc-900/50 border-white/10"
              data-testid="product-search"
            />
          </div>

          <div className="flex gap-6">
            {/* Product Grid */}
            <div className={`flex-1 ${selectedProduct ? 'hidden lg:block lg:w-1/2' : 'w-full'}`}>
              {loading ? (
                <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-indigo-400" /></div>
              ) : filtered.length === 0 ? (
                <Card className="bg-zinc-900/50 border-white/10">
                  <CardContent className="flex flex-col items-center justify-center py-16">
                    <Package className="w-12 h-12 text-zinc-600 mb-4" />
                    <h3 className="text-white font-medium mb-2">{searchQuery ? "No products match" : "No products yet"}</h3>
                    <p className="text-zinc-500 text-sm text-center mb-4">Upload a product image in any chat and ask the agent to scan it. Then save it here!</p>
                    <Button onClick={() => navigate("/chat")} variant="outline" className="border-white/10"><MessageSquare className="w-4 h-4 mr-2" />Go to Chat</Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filtered.map(product => (
                    <Card
                      key={product.product_id}
                      className={`bg-zinc-900/50 border-white/10 cursor-pointer hover:border-indigo-500/30 transition-all group ${selectedProduct?.product_id === product.product_id ? 'border-indigo-500/50 ring-1 ring-indigo-500/20' : ''}`}
                      onClick={() => { setSelectedProduct(product); setGeneratedContent(null); }}
                      data-testid={`product-card-${product.product_id}`}
                    >
                      <CardContent className="p-4">
                        {/* Image */}
                        <div className="aspect-square rounded-lg bg-zinc-800 mb-3 overflow-hidden">
                          {product.images?.[0]?.url || product.images?.[0]?.thumbnail ? (
                            <img src={product.images[0].thumbnail || product.images[0].url} alt={product.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" onError={e => { e.target.style.display = 'none'; }} />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center"><Package className="w-8 h-8 text-zinc-600" /></div>
                          )}
                        </div>
                        <h3 className="text-white font-semibold text-sm truncate">{product.name}</h3>
                        {product.brand && <p className="text-zinc-500 text-xs">{product.brand}</p>}
                        <div className="flex items-center justify-between mt-2">
                          {product.category && <Badge className="bg-indigo-500/20 text-indigo-300 text-[9px]">{product.category}</Badge>}
                          <span className="text-zinc-600 text-[10px] flex items-center gap-1"><Clock className="w-3 h-3" />{new Date(product.created_at).toLocaleDateString()}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Product Detail Panel */}
            {selectedProduct && (
              <div className="w-full lg:w-1/2 lg:sticky lg:top-6 space-y-4" data-testid="product-detail">
                <button className="lg:hidden flex items-center gap-1 text-zinc-400 text-sm mb-2" onClick={() => setSelectedProduct(null)}>
                  <ChevronLeft className="w-4 h-4" />Back to list
                </button>

                <Card className="bg-zinc-900/50 border-white/10">
                  <CardContent className="p-5">
                    {/* Images */}
                    {selectedProduct.images?.length > 0 && (
                      <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
                        {selectedProduct.images.slice(0, 6).map((img, i) => (
                          <img key={i} src={img.thumbnail || img.url} alt="" className="w-20 h-20 rounded-lg object-cover border border-white/10 flex-shrink-0" onError={e => { e.target.style.display = 'none'; }} />
                        ))}
                      </div>
                    )}

                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h2 className="text-xl font-bold text-white font-['Outfit']" data-testid="product-detail-name">{selectedProduct.name}</h2>
                        {selectedProduct.brand && <p className="text-indigo-400 text-sm">{selectedProduct.brand}</p>}
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="border-white/10 text-zinc-400 h-8 w-8 p-0"
                          onClick={() => rescanProduct(selectedProduct.product_id)}
                          disabled={rescanning === selectedProduct.product_id}
                          data-testid="rescan-btn">
                          <RefreshCw className={`w-3.5 h-3.5 ${rescanning === selectedProduct.product_id ? 'animate-spin' : ''}`} />
                        </Button>
                        <Button variant="outline" size="sm" className="border-red-500/30 text-red-400 hover:bg-red-500/10 h-8 w-8 p-0"
                          onClick={() => deleteProduct(selectedProduct.product_id)}
                          data-testid="delete-product-btn">
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>

                    {selectedProduct.description && <p className="text-zinc-400 text-sm mb-3">{selectedProduct.description}</p>}
                    {selectedProduct.specs && (
                      <div className="p-3 rounded-lg bg-white/5 mb-3">
                        <p className="text-[10px] text-zinc-500 font-medium mb-1">SPECIFICATIONS</p>
                        <p className="text-zinc-300 text-xs whitespace-pre-wrap">{selectedProduct.specs.slice(0, 500)}</p>
                      </div>
                    )}
                    {selectedProduct.price_info && (
                      <div className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/10 mb-3">
                        <p className="text-[10px] text-emerald-500 font-medium mb-1">PRICE INFO</p>
                        <p className="text-zinc-300 text-xs">{selectedProduct.price_info}</p>
                      </div>
                    )}

                    <div className="text-[10px] text-zinc-600 flex items-center gap-3">
                      <span>Scanned: {new Date(selectedProduct.last_scanned).toLocaleString()}</span>
                      {selectedProduct.source_chat_id && (
                        <Link to={`/chat?chat=${selectedProduct.source_chat_id}`} className="text-indigo-400 hover:underline flex items-center gap-1">
                          <ExternalLink className="w-3 h-3" />Source chat
                        </Link>
                      )}
                    </div>
                  </CardContent>
                </Card>

                {/* Quick Generate */}
                <Card className="bg-zinc-900/50 border-white/10">
                  <CardContent className="p-5">
                    <h3 className="text-white font-semibold text-sm mb-3">Quick Generate</h3>
                    <div className="grid grid-cols-2 gap-2">
                      {contentTypes.map(ct => (
                        <Button
                          key={ct.key}
                          onClick={() => generateContent(selectedProduct.product_id, ct.key)}
                          disabled={generating !== null}
                          className={`bg-gradient-to-r ${ct.color} text-white text-xs h-10 justify-start`}
                          data-testid={`generate-${ct.key}-btn`}
                        >
                          {generating === ct.key ? <Loader2 className="w-3.5 h-3.5 mr-2 animate-spin" /> : <ct.icon className="w-3.5 h-3.5 mr-2" />}
                          {ct.label}
                        </Button>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Generated Content */}
                {generatedContent && (
                  <Card className="bg-zinc-900/50 border-white/10" data-testid="generated-content">
                    <CardContent className="p-5">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-white font-semibold text-sm">
                          Generated: {contentTypes.find(c => c.key === generatedContent.type)?.label}
                        </h3>
                        <Button variant="outline" size="sm" className="border-white/10 text-zinc-400 h-7 text-[10px]"
                          onClick={() => { navigator.clipboard.writeText(generatedContent.content); toast.success("Copied!"); }}>
                          Copy
                        </Button>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5 max-h-80 overflow-y-auto">
                        <p className="text-zinc-300 text-sm whitespace-pre-wrap">{generatedContent.content}</p>
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* History */}
                {selectedProduct.generated_content?.length > 0 && (
                  <Card className="bg-zinc-900/50 border-white/10">
                    <CardContent className="p-5">
                      <h3 className="text-white font-semibold text-sm mb-3">Generation History</h3>
                      <div className="space-y-2">
                        {selectedProduct.generated_content.slice(-5).reverse().map((gen, i) => (
                          <div key={gen.content_id || i} className="p-2 rounded bg-white/5 cursor-pointer hover:bg-white/10 transition-colors"
                            onClick={() => setGeneratedContent({ type: gen.type, content: gen.content })}>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-indigo-300">{contentTypes.find(c => c.key === gen.type)?.label || gen.type}</span>
                              <span className="text-[10px] text-zinc-600">{new Date(gen.created_at).toLocaleDateString()}</span>
                            </div>
                            <p className="text-zinc-500 text-[10px] truncate mt-0.5">{gen.content?.slice(0, 80)}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            )}
          </div>

          {/* Batch Progress Tracker */}
          {batchProgress && batchProgress.status === "processing" && (
            <Card className="mt-6 bg-zinc-900/50 border-indigo-500/20" data-testid="batch-progress">
              <CardContent className="p-5">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />
                    <h3 className="text-white font-semibold text-sm">Batch Import in Progress</h3>
                  </div>
                  <span className="text-zinc-400 text-xs">
                    {(batchProgress.completed || 0) + (batchProgress.failed || 0)}/{batchProgress.total} processed
                  </span>
                </div>
                <div className="h-2 rounded-full bg-zinc-800 overflow-hidden mb-3">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-emerald-500 transition-all duration-500"
                    style={{ width: `${Math.max(((batchProgress.completed || 0) + (batchProgress.failed || 0)) / batchProgress.total * 100, 3)}%` }}
                  />
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 max-h-48 overflow-y-auto">
                  {(batchProgress.items || []).map((item, i) => (
                    <div key={i} className={`p-2 rounded-lg text-[10px] border ${
                      item.status === "done" ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" :
                      item.status === "scanning" ? "bg-amber-500/10 border-amber-500/20 text-amber-400" :
                      item.status === "failed" ? "bg-red-500/10 border-red-500/20 text-red-400" :
                      "bg-zinc-800/50 border-white/5 text-zinc-500"
                    }`} data-testid={`batch-item-${i}`}>
                      <p className="font-medium truncate">{item.name}</p>
                      <p className="capitalize mt-0.5">
                        {item.status === "scanning" && <Loader2 className="w-2.5 h-2.5 inline animate-spin mr-1" />}
                        {item.status}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Completed batch summary */}
          {batchProgress && batchProgress.status === "complete" && (
            <Card className="mt-6 bg-zinc-900/50 border-emerald-500/20" data-testid="batch-complete">
              <CardContent className="p-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Package className="w-4 h-4 text-emerald-400" />
                  </div>
                  <div>
                    <p className="text-white text-sm font-medium">Batch Import Complete</p>
                    <p className="text-zinc-500 text-xs">{batchProgress.completed} scanned, {batchProgress.failed} failed</p>
                  </div>
                </div>
                <Button variant="outline" size="sm" className="border-white/10 text-zinc-400" onClick={() => setBatchProgress(null)}>Dismiss</Button>
              </CardContent>
            </Card>
          )}
        </div>

      {/* Import Modal */}
      {showImport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="import-modal">
          <Card className="w-full max-w-md bg-zinc-900 border-white/10">
            <CardContent className="p-6">
              <h2 className="text-lg font-bold text-white font-['Outfit'] mb-1">Batch Product Import</h2>
              <p className="text-zinc-400 text-sm mb-4">Upload a CSV or XLSX file with product data. Required column: <code className="text-indigo-400">name</code>. Optional: <code className="text-indigo-400">brand</code>, <code className="text-indigo-400">category</code>.</p>

              <div
                className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${importFile ? "border-emerald-500/40 bg-emerald-500/5" : "border-white/10 hover:border-indigo-500/30"}`}
                onDragOver={e => e.preventDefault()}
                onDrop={e => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) setImportFile(f); }}
              >
                {importFile ? (
                  <div>
                    <Package className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                    <p className="text-white text-sm font-medium">{importFile.name}</p>
                    <p className="text-zinc-500 text-xs mt-1">{(importFile.size / 1024).toFixed(1)} KB</p>
                    <button className="text-red-400 text-xs mt-2 hover:underline" onClick={() => setImportFile(null)}>Remove</button>
                  </div>
                ) : (
                  <div>
                    <Plus className="w-8 h-8 text-zinc-600 mx-auto mb-2" />
                    <p className="text-zinc-400 text-sm">Drag & drop your file here</p>
                    <p className="text-zinc-600 text-xs mt-1">or</p>
                    <label className="inline-block mt-2 px-4 py-1.5 rounded-lg bg-white/10 text-white text-sm cursor-pointer hover:bg-white/20 transition-colors">
                      Browse Files
                      <input type="file" accept=".csv,.xlsx,.xls" className="hidden" onChange={e => { if (e.target.files[0]) setImportFile(e.target.files[0]); }} />
                    </label>
                  </div>
                )}
              </div>

              <div className="p-3 rounded-lg bg-white/5 mt-4">
                <p className="text-[10px] text-zinc-500 font-medium mb-1">EXAMPLE CSV FORMAT</p>
                <code className="text-[11px] text-zinc-400 block">name,brand,category<br/>iPhone 16 Pro,Apple,Smartphone<br/>Air Max 90,Nike,Footwear<br/>Model Y,Tesla,Electric Vehicle</code>
              </div>

              <div className="flex gap-3 mt-5">
                <Button variant="outline" className="flex-1 border-white/10 text-zinc-400" onClick={() => { setShowImport(false); setImportFile(null); }}>Cancel</Button>
                <Button
                  className="flex-1 bg-gradient-to-r from-indigo-500 to-violet-500"
                  disabled={!importFile || importing}
                  onClick={handleBatchImport}
                  data-testid="start-import-btn"
                >
                  {importing ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Scan className="w-4 h-4 mr-2" />}
                  {importing ? "Importing..." : `Import ${importFile ? "& Scan" : ""}`}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
