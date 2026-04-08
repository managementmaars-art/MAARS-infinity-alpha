import { useState, useEffect, useCallback } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth, API } from "../App";
import { toast } from "sonner";
import {
  Package, Search, Plus, RefreshCw, Trash2, Video, FileText, Share2,
  Megaphone, ChevronLeft, ExternalLink, Clock, Scan, MessageSquare,
} from "lucide-react";

const T = {
  glass: "rgba(255,255,255,0.03)",
  border: "rgba(255,255,255,0.08)",
  indigo: "#818cf8",
  violet: "#7c3aed",
  green: "#34d399",
  amber: "#f59e0b",
  red: "#ef4444",
  cyan: "#22d3ee",
  zinc: "#71717a",
};

const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} } @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }`;

const formInput = {
  background: "rgba(255,255,255,.04)",
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 8,
  padding: "8px 12px",
  color: "#fff",
  fontSize: 13,
  outline: "none",
  fontFamily: "inherit",
  width: "100%",
  boxSizing: "border-box",
  transition: "border-color .2s",
};

const btnPrimary = {
  background: "linear-gradient(135deg,#6366f1,#7c3aed)",
  border: "none",
  borderRadius: 8,
  color: "#fff",
  fontSize: 13,
  fontWeight: 600,
  padding: "8px 16px",
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  fontFamily: "inherit",
};

const btnOutline = {
  background: "transparent",
  border: "1px solid rgba(255,255,255,0.10)",
  borderRadius: 8,
  color: "#a1a1aa",
  fontSize: 13,
  fontWeight: 500,
  padding: "8px 16px",
  cursor: "pointer",
  display: "inline-flex",
  alignItems: "center",
  gap: 6,
  fontFamily: "inherit",
};

const btnIconOutline = {
  ...btnOutline,
  padding: 0,
  width: 32,
  height: 32,
  justifyContent: "center",
};

const card = {
  background: T.glass,
  border: "1px solid rgba(255,255,255,0.08)",
  borderRadius: 14,
};

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
    { key: "video", label: "Video Prompt", icon: Video, gradient: "linear-gradient(135deg,#ef4444,#f43f5e)" },
    { key: "ad_copy", label: "Ad Copy", icon: FileText, gradient: "linear-gradient(135deg,#3b82f6,#6366f1)" },
    { key: "social_post", label: "Social Posts", icon: Share2, gradient: "linear-gradient(135deg,#a855f7,#7c3aed)" },
    { key: "full_campaign", label: "Full Campaign", icon: Megaphone, gradient: "linear-gradient(135deg,#f59e0b,#f97316)" },
  ];

  return (
    <div data-testid="products-page" style={{ animation: "fadeUp .4s ease" }}>
      <style>{STYLES}</style>
      <div style={{ maxWidth: 1280, margin: "0 auto", display: "flex", flexDirection: "column", gap: 24 }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ fontSize: 22, fontWeight: 700, color: "#fff", margin: 0, fontFamily: "Outfit, sans-serif" }} data-testid="products-title">Product Catalog</h1>
            <p style={{ fontSize: 13, color: "#71717a", margin: "4px 0 0" }}>{products.length} product{products.length !== 1 ? "s" : ""} saved</p>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button style={btnOutline} onClick={() => setShowImport(true)} data-testid="import-btn">
              <Plus style={{ width: 16, height: 16 }} />Import CSV
            </button>
            <button style={btnPrimary} onClick={() => navigate("/chat")} data-testid="scan-new-btn">
              <Scan style={{ width: 16, height: 16 }} />Scan New Product
            </button>
          </div>
        </div>

        {/* Search */}
        <div style={{ position: "relative" }}>
          <Search style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", width: 16, height: 16, color: "#52525b" }} />
          <input
            placeholder="Search products..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{ ...formInput, paddingLeft: 38 }}
            data-testid="product-search"
          />
        </div>

        <div style={{ display: "flex", gap: 24 }}>
          {/* Product Grid */}
          <div style={{ flex: 1, minWidth: 0, display: selectedProduct ? undefined : "block" }}>
            {loading ? (
              <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
                <div style={{ width: 32, height: 32, border: "2px solid #6366f1", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
              </div>
            ) : filtered.length === 0 ? (
              <div style={{ ...card, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: 64 }}>
                <Package style={{ width: 48, height: 48, color: "#3f3f46", marginBottom: 16 }} />
                <h3 style={{ fontSize: 15, fontWeight: 500, color: "#fff", margin: "0 0 8px" }}>{searchQuery ? "No products match" : "No products yet"}</h3>
                <p style={{ fontSize: 13, color: "#52525b", textAlign: "center", margin: "0 0 16px" }}>Upload a product image in any chat and ask the agent to scan it. Then save it here!</p>
                <button style={btnOutline} onClick={() => navigate("/chat")}>
                  <MessageSquare style={{ width: 16, height: 16 }} />Go to Chat
                </button>
              </div>
            ) : (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 16 }}>
                {filtered.map(product => {
                  const isSelected = selectedProduct?.product_id === product.product_id;
                  return (
                    <div
                      key={product.product_id}
                      style={{
                        ...card,
                        cursor: "pointer",
                        transition: "border-color .15s",
                        border: isSelected ? "1px solid rgba(99,102,241,0.5)" : "1px solid rgba(255,255,255,0.08)",
                        boxShadow: isSelected ? "0 0 0 1px rgba(99,102,241,0.2)" : "none",
                      }}
                      onClick={() => { setSelectedProduct(product); setGeneratedContent(null); }}
                      data-testid={`product-card-${product.product_id}`}
                      onMouseEnter={e => { if (!isSelected) e.currentTarget.style.borderColor = "rgba(99,102,241,0.3)"; }}
                      onMouseLeave={e => { if (!isSelected) e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"; }}
                    >
                      <div style={{ padding: 16 }}>
                        <div style={{ aspectRatio: "1 / 1", borderRadius: 10, background: "#18181b", marginBottom: 12, overflow: "hidden" }}>
                          {product.images?.[0]?.url || product.images?.[0]?.thumbnail ? (
                            <img
                              src={product.images[0].thumbnail || product.images[0].url}
                              alt={product.name}
                              style={{ width: "100%", height: "100%", objectFit: "cover", transition: "transform .3s" }}
                              onError={e => { e.target.style.display = "none"; }}
                              onMouseEnter={e => e.target.style.transform = "scale(1.05)"}
                              onMouseLeave={e => e.target.style.transform = "none"}
                            />
                          ) : (
                            <div style={{ width: "100%", height: "100%", display: "flex", alignItems: "center", justifyContent: "center" }}>
                              <Package style={{ width: 32, height: 32, color: "#3f3f46" }} />
                            </div>
                          )}
                        </div>
                        <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>{product.name}</h3>
                        {product.brand && <p style={{ fontSize: 11, color: "#52525b", margin: "2px 0 0" }}>{product.brand}</p>}
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginTop: 8 }}>
                          {product.category && (
                            <span style={{ fontSize: 9, fontWeight: 700, padding: "2px 9px", borderRadius: 20, background: "rgba(99,102,241,0.2)", color: "#a5b4fc" }}>
                              {product.category}
                            </span>
                          )}
                          <span style={{ fontSize: 10, color: "#3f3f46", display: "flex", alignItems: "center", gap: 3 }}>
                            <Clock style={{ width: 10, height: 10 }} />{new Date(product.created_at).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Product Detail Panel */}
          {selectedProduct && (
            <div style={{ width: "100%", maxWidth: 400, flexShrink: 0, display: "flex", flexDirection: "column", gap: 16, position: "sticky", top: 24, alignSelf: "flex-start" }} data-testid="product-detail">
              <button
                style={{ display: "flex", alignItems: "center", gap: 4, color: "#71717a", fontSize: 13, background: "none", border: "none", cursor: "pointer", padding: 0, fontFamily: "inherit", marginBottom: 4 }}
                onClick={() => setSelectedProduct(null)}
              >
                <ChevronLeft style={{ width: 16, height: 16 }} />Back to list
              </button>

              <div style={{ ...card, padding: 20 }}>
                {selectedProduct.images?.length > 0 && (
                  <div style={{ display: "flex", gap: 8, marginBottom: 16, overflowX: "auto", paddingBottom: 8 }}>
                    {selectedProduct.images.slice(0, 6).map((img, i) => (
                      <img
                        key={i}
                        src={img.thumbnail || img.url}
                        alt=""
                        style={{ width: 80, height: 80, borderRadius: 8, objectFit: "cover", border: "1px solid rgba(255,255,255,0.10)", flexShrink: 0 }}
                        onError={e => { e.target.style.display = "none"; }}
                      />
                    ))}
                  </div>
                )}

                <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 12 }}>
                  <div>
                    <h2 style={{ fontSize: 20, fontWeight: 700, color: "#fff", margin: 0, fontFamily: "Outfit, sans-serif" }} data-testid="product-detail-name">{selectedProduct.name}</h2>
                    {selectedProduct.brand && <p style={{ fontSize: 13, color: T.indigo, margin: "2px 0 0" }}>{selectedProduct.brand}</p>}
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    <button
                      style={{ ...btnIconOutline, borderColor: "rgba(255,255,255,0.10)" }}
                      onClick={() => rescanProduct(selectedProduct.product_id)}
                      disabled={rescanning === selectedProduct.product_id}
                      data-testid="rescan-btn"
                    >
                      <RefreshCw style={{ width: 14, height: 14, animation: rescanning === selectedProduct.product_id ? "spin 1s linear infinite" : "none" }} />
                    </button>
                    <button
                      style={{ ...btnIconOutline, borderColor: "rgba(239,68,68,0.3)", color: "#f87171" }}
                      onClick={() => deleteProduct(selectedProduct.product_id)}
                      data-testid="delete-product-btn"
                    >
                      <Trash2 style={{ width: 14, height: 14 }} />
                    </button>
                  </div>
                </div>

                {selectedProduct.description && <p style={{ fontSize: 13, color: "#71717a", margin: "0 0 12px" }}>{selectedProduct.description}</p>}
                {selectedProduct.specs && (
                  <div style={{ padding: 12, borderRadius: 8, background: "rgba(255,255,255,0.05)", marginBottom: 12 }}>
                    <p style={{ fontSize: 10, color: "#52525b", fontWeight: 500, marginBottom: 4 }}>SPECIFICATIONS</p>
                    <p style={{ fontSize: 11, color: "#d4d4d8", margin: 0, whiteSpace: "pre-wrap" }}>{selectedProduct.specs.slice(0, 500)}</p>
                  </div>
                )}
                {selectedProduct.price_info && (
                  <div style={{ padding: 12, borderRadius: 8, background: "rgba(16,185,129,0.05)", border: "1px solid rgba(16,185,129,0.10)", marginBottom: 12 }}>
                    <p style={{ fontSize: 10, color: "#10b981", fontWeight: 500, marginBottom: 4 }}>PRICE INFO</p>
                    <p style={{ fontSize: 11, color: "#d4d4d8", margin: 0 }}>{selectedProduct.price_info}</p>
                  </div>
                )}

                <div style={{ fontSize: 10, color: "#3f3f46", display: "flex", alignItems: "center", gap: 12 }}>
                  <span>Scanned: {new Date(selectedProduct.last_scanned).toLocaleString()}</span>
                  {selectedProduct.source_chat_id && (
                    <Link to={`/chat?chat=${selectedProduct.source_chat_id}`} style={{ color: T.indigo, textDecoration: "none", display: "flex", alignItems: "center", gap: 3 }}>
                      <ExternalLink style={{ width: 10, height: 10 }} />Source chat
                    </Link>
                  )}
                </div>
              </div>

              {/* Quick Generate */}
              <div style={{ ...card, padding: 20 }}>
                <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: "0 0 12px" }}>Quick Generate</h3>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
                  {contentTypes.map(ct => (
                    <button
                      key={ct.key}
                      onClick={() => generateContent(selectedProduct.product_id, ct.key)}
                      disabled={generating !== null}
                      style={{
                        background: ct.gradient,
                        border: "none",
                        borderRadius: 8,
                        color: "#fff",
                        fontSize: 11,
                        fontWeight: 600,
                        padding: "10px 12px",
                        cursor: generating !== null ? "not-allowed" : "pointer",
                        display: "flex",
                        alignItems: "center",
                        gap: 6,
                        fontFamily: "inherit",
                        opacity: generating !== null ? 0.6 : 1,
                        transition: "opacity .15s",
                      }}
                      data-testid={`generate-${ct.key}-btn`}
                    >
                      {generating === ct.key
                        ? <div style={{ width: 14, height: 14, border: "2px solid rgba(255,255,255,0.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                        : <ct.icon style={{ width: 14, height: 14 }} />
                      }
                      {ct.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Generated Content */}
              {generatedContent && (
                <div style={{ ...card, padding: 20 }} data-testid="generated-content">
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                    <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>
                      Generated: {contentTypes.find(c => c.key === generatedContent.type)?.label}
                    </h3>
                    <button
                      style={{ ...btnOutline, fontSize: 10, padding: "4px 10px" }}
                      onClick={() => { navigator.clipboard.writeText(generatedContent.content); toast.success("Copied!"); }}
                    >
                      Copy
                    </button>
                  </div>
                  <div style={{ padding: 12, borderRadius: 8, background: "rgba(255,255,255,0.05)", maxHeight: 320, overflowY: "auto" }}>
                    <p style={{ fontSize: 13, color: "#d4d4d8", margin: 0, whiteSpace: "pre-wrap" }}>{generatedContent.content}</p>
                  </div>
                </div>
              )}

              {/* History */}
              {selectedProduct.generated_content?.length > 0 && (
                <div style={{ ...card, padding: 20 }}>
                  <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: "0 0 12px" }}>Generation History</h3>
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    {selectedProduct.generated_content.slice(-5).reverse().map((gen, i) => (
                      <div
                        key={gen.content_id || i}
                        style={{ padding: 8, borderRadius: 6, background: "rgba(255,255,255,0.05)", cursor: "pointer", transition: "background .15s" }}
                        onClick={() => setGeneratedContent({ type: gen.type, content: gen.content })}
                        onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.09)"}
                        onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.05)"}
                      >
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                          <span style={{ fontSize: 11, color: "#a5b4fc" }}>{contentTypes.find(c => c.key === gen.type)?.label || gen.type}</span>
                          <span style={{ fontSize: 10, color: "#3f3f46" }}>{new Date(gen.created_at).toLocaleDateString()}</span>
                        </div>
                        <p style={{ fontSize: 10, color: "#52525b", margin: "2px 0 0", overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>{gen.content?.slice(0, 80)}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Batch Progress Tracker */}
        {batchProgress && batchProgress.status === "processing" && (
          <div style={{ ...card, border: "1px solid rgba(99,102,241,0.2)", padding: 20, marginTop: 24 }} data-testid="batch-progress">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 16, height: 16, border: "2px solid #818cf8", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                <h3 style={{ fontSize: 13, fontWeight: 600, color: "#fff", margin: 0 }}>Batch Import in Progress</h3>
              </div>
              <span style={{ fontSize: 11, color: "#71717a" }}>
                {(batchProgress.completed || 0) + (batchProgress.failed || 0)}/{batchProgress.total} processed
              </span>
            </div>
            <div style={{ height: 8, borderRadius: 9999, background: "#27272a", overflow: "hidden", marginBottom: 12 }}>
              <div style={{
                height: "100%",
                borderRadius: 9999,
                background: "linear-gradient(90deg,#6366f1,#34d399)",
                transition: "width 0.5s ease",
                width: `${Math.max(((batchProgress.completed || 0) + (batchProgress.failed || 0)) / batchProgress.total * 100, 3)}%`,
              }} />
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(100px, 1fr))", gap: 8, maxHeight: 192, overflowY: "auto" }}>
              {(batchProgress.items || []).map((item, i) => {
                const itemStyle = item.status === "done"
                  ? { background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", color: "#34d399" }
                  : item.status === "scanning"
                  ? { background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)", color: "#fbbf24" }
                  : item.status === "failed"
                  ? { background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)", color: "#f87171" }
                  : { background: "rgba(39,39,42,0.5)", border: "1px solid rgba(255,255,255,0.05)", color: "#52525b" };
                return (
                  <div key={i} style={{ padding: 8, borderRadius: 8, fontSize: 10, ...itemStyle }} data-testid={`batch-item-${i}`}>
                    <p style={{ fontWeight: 500, margin: 0, overflow: "hidden", whiteSpace: "nowrap", textOverflow: "ellipsis" }}>{item.name}</p>
                    <p style={{ textTransform: "capitalize", margin: "2px 0 0", display: "flex", alignItems: "center", gap: 3 }}>
                      {item.status === "scanning" && <span style={{ display: "inline-block", width: 10, height: 10, border: "1.5px solid currentColor", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />}
                      {item.status}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Completed batch summary */}
        {batchProgress && batchProgress.status === "complete" && (
          <div style={{ ...card, border: "1px solid rgba(16,185,129,0.2)", padding: 16, marginTop: 24, display: "flex", alignItems: "center", justifyContent: "space-between" }} data-testid="batch-complete">
            <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
              <div style={{ width: 32, height: 32, borderRadius: "50%", background: "rgba(16,185,129,0.2)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Package style={{ width: 16, height: 16, color: "#34d399" }} />
              </div>
              <div>
                <p style={{ fontSize: 13, fontWeight: 500, color: "#fff", margin: 0 }}>Batch Import Complete</p>
                <p style={{ fontSize: 11, color: "#52525b", margin: "2px 0 0" }}>{batchProgress.completed} scanned, {batchProgress.failed} failed</p>
              </div>
            </div>
            <button style={btnOutline} onClick={() => setBatchProgress(null)}>Dismiss</button>
          </div>
        )}
      </div>

      {/* Import Modal */}
      {showImport && (
        <div style={{ position: "fixed", inset: 0, zIndex: 50, display: "flex", alignItems: "center", justifyContent: "center", background: "rgba(0,0,0,0.6)", backdropFilter: "blur(6px)" }} data-testid="import-modal">
          <div style={{ ...card, width: "100%", maxWidth: 448, padding: 24 }}>
            <h2 style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: "0 0 4px", fontFamily: "Outfit, sans-serif" }}>Batch Product Import</h2>
            <p style={{ fontSize: 13, color: "#71717a", margin: "0 0 16px" }}>
              Upload a CSV or XLSX file with product data. Required column: <code style={{ color: T.indigo }}>name</code>. Optional: <code style={{ color: T.indigo }}>brand</code>, <code style={{ color: T.indigo }}>category</code>.
            </p>

            <div
              style={{
                border: importFile ? "2px dashed rgba(16,185,129,0.4)" : "2px dashed rgba(255,255,255,0.10)",
                borderRadius: 12,
                padding: 32,
                textAlign: "center",
                background: importFile ? "rgba(16,185,129,0.05)" : "transparent",
                transition: "border-color .2s, background .2s",
              }}
              onDragOver={e => e.preventDefault()}
              onDrop={e => { e.preventDefault(); const f = e.dataTransfer.files[0]; if (f) setImportFile(f); }}
            >
              {importFile ? (
                <div>
                  <Package style={{ width: 32, height: 32, color: "#34d399", margin: "0 auto 8px", display: "block" }} />
                  <p style={{ fontSize: 13, fontWeight: 500, color: "#fff", margin: 0 }}>{importFile.name}</p>
                  <p style={{ fontSize: 11, color: "#52525b", margin: "4px 0 0" }}>{(importFile.size / 1024).toFixed(1)} KB</p>
                  <button style={{ fontSize: 11, color: "#f87171", background: "none", border: "none", cursor: "pointer", marginTop: 8, fontFamily: "inherit" }} onClick={() => setImportFile(null)}>Remove</button>
                </div>
              ) : (
                <div>
                  <Plus style={{ width: 32, height: 32, color: "#3f3f46", margin: "0 auto 8px", display: "block" }} />
                  <p style={{ fontSize: 13, color: "#71717a", margin: 0 }}>Drag & drop your file here</p>
                  <p style={{ fontSize: 11, color: "#3f3f46", margin: "4px 0 0" }}>or</p>
                  <label style={{ display: "inline-block", marginTop: 8, padding: "6px 16px", borderRadius: 8, background: "rgba(255,255,255,0.10)", color: "#fff", fontSize: 13, cursor: "pointer", transition: "background .15s" }}>
                    Browse Files
                    <input type="file" accept=".csv,.xlsx,.xls" style={{ display: "none" }} onChange={e => { if (e.target.files[0]) setImportFile(e.target.files[0]); }} />
                  </label>
                </div>
              )}
            </div>

            <div style={{ padding: 12, borderRadius: 8, background: "rgba(255,255,255,0.05)", marginTop: 16 }}>
              <p style={{ fontSize: 10, color: "#52525b", fontWeight: 500, marginBottom: 4 }}>EXAMPLE CSV FORMAT</p>
              <code style={{ fontSize: 11, color: "#71717a", display: "block" }}>name,brand,category<br />iPhone 16 Pro,Apple,Smartphone<br />Air Max 90,Nike,Footwear<br />Model Y,Tesla,Electric Vehicle</code>
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
              <button style={{ ...btnOutline, flex: 1, justifyContent: "center" }} onClick={() => { setShowImport(false); setImportFile(null); }}>Cancel</button>
              <button
                style={{ ...btnPrimary, flex: 1, justifyContent: "center", opacity: (!importFile || importing) ? 0.5 : 1, cursor: (!importFile || importing) ? "not-allowed" : "pointer" }}
                disabled={!importFile || importing}
                onClick={handleBatchImport}
                data-testid="start-import-btn"
              >
                {importing
                  ? <><div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.4)", borderTopColor: "#fff", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} /> Importing...</>
                  : <><Scan style={{ width: 16, height: 16 }} /> {importFile ? "Import & Scan" : "Import"}</>
                }
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
