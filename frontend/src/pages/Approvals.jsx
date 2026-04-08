import { useState, useEffect } from "react";
import { useAuth, API } from "../App";
import {
  CheckCircle, XCircle, Clock, Send, ChevronDown, ChevronUp,
  Loader2, Trash2, FileCheck, AlertTriangle, Filter, Eye
} from "lucide-react";
import { toast } from "sonner";

/* ─── Design tokens ─────────────────────────────────────────────────── */
const T = {
  teal:   "#4fd1c5",
  violet: "#7c3aed",
  blue:   "#2563eb",
  green:  "#34d399",
  amber:  "#f59e0b",
  red:    "#f87171",
  orange: "#f97316",
  indigo: "#6366f1",
  border: "rgba(255,255,255,0.07)",
  glass:  "rgba(8,15,28,0.65)",
};

const STATUS_META = {
  draft:              { label: "Pending",  color: T.amber,  icon: Clock },
  approved:           { label: "Approved", color: T.green,  icon: CheckCircle },
  revision_requested: { label: "Revision", color: T.orange, icon: AlertTriangle },
  published:          { label: "Published",color: T.indigo, icon: Send },
};

const TYPE_LABELS = {
  social_post:    "Social Post",
  email_campaign: "Email Campaign",
  blog_post:      "Blog Post",
  general:        "General",
};

/* ─── Keyframes ─────────────────────────────────────────────────────── */
const STYLES = `
  @keyframes ap_fadeUp { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
  @keyframes ap_spin   { to { transform: rotate(360deg); } }
  @keyframes ap_pulse  { 0%,100% { opacity:1; transform:scale(1); } 50% { opacity:0.4; transform:scale(1.5); } }
`;

const Approvals = () => {
  const { token }     = useAuth();
  const [approvals,   setApprovals]   = useState([]);
  const [pendingCount,setPendingCount] = useState(0);
  const [loading,     setLoading]     = useState(true);
  const [filter,      setFilter]      = useState("");
  const [expanded,    setExpanded]    = useState({});
  const [actionLoading,setActionLoading] = useState({});

  const headers = { Authorization: `Bearer ${token}` };

  const fetchApprovals = async () => {
    try {
      const url = filter ? `${API}/approvals?status=${filter}` : `${API}/approvals`;
      const res = await fetch(url, { headers });
      if (res.ok) {
        const data = await res.json();
        setApprovals(data.approvals || []);
        setPendingCount(data.pending_count || 0);
      }
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { fetchApprovals(); }, [token, filter]);

  const handleAction = async (id, action) => {
    setActionLoading(prev => ({ ...prev, [id]: action }));
    try {
      const res = await fetch(`${API}/approvals/${id}/${action}`, { method: "POST", headers });
      if (res.ok) {
        toast.success(action === "approve" ? "Approved" : action === "publish" ? "Published" : "Revision requested");
        fetchApprovals();
      }
    } catch { toast.error("Action failed"); }
    finally { setActionLoading(prev => ({ ...prev, [id]: null })); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Delete this approval?")) return;
    await fetch(`${API}/approvals/${id}`, { method: "DELETE", headers });
    fetchApprovals();
    toast.success("Deleted");
  };

  const FILTERS = [
    { key: "",          label: "All",      count: approvals.length },
    { key: "draft",     label: "Pending",  count: approvals.filter(a => a.status === "draft").length },
    { key: "approved",  label: "Approved", count: approvals.filter(a => a.status === "approved").length },
    { key: "published", label: "Published",count: approvals.filter(a => a.status === "published").length },
  ];

  return (
    <div data-testid="approvals-page" style={{ animation: "ap_fadeUp 0.35s ease" }}>
      <style>{STYLES}</style>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ width: 44, height: 44, borderRadius: 14, background: "linear-gradient(135deg, rgba(52,211,153,0.2), rgba(37,99,235,0.12))", border: "1px solid rgba(52,211,153,0.2)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(52,211,153,0.1)" }}>
            <FileCheck style={{ width: 20, height: 20, color: T.green }} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <h1 style={{ fontSize: "clamp(1.2rem,2.5vw,1.5rem)", fontWeight: 800, color: "#f1f5f9", fontFamily: "Outfit, sans-serif", margin: 0 }}>Approvals</h1>
              {pendingCount > 0 && (
                <span style={{ padding: "2px 8px", borderRadius: 20, background: "rgba(245,158,11,0.12)", border: "1px solid rgba(245,158,11,0.25)", color: T.amber, fontSize: 11, fontWeight: 700 }}>
                  {pendingCount} pending
                </span>
              )}
            </div>
            <p style={{ fontSize: 12, color: "#475569", margin: 0 }}>Review agent-created content before publishing</p>
          </div>
        </div>
      </div>

      {/* ── Filter tabs ──────────────────────────────────────────────────── */}
      <div data-testid="approval-filters" style={{ display: "flex", gap: 6, marginBottom: 24 }}>
        {FILTERS.map(f => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            data-testid={`filter-${f.key || "all"}`}
            style={{ display: "flex", alignItems: "center", gap: 5, padding: "6px 14px", borderRadius: 20, border: `1px solid ${filter === f.key ? "rgba(79,209,197,0.3)" : T.border}`, background: filter === f.key ? "rgba(79,209,197,0.08)" : T.glass, color: filter === f.key ? T.teal : "#475569", fontSize: 12, fontWeight: 600, cursor: "pointer", transition: "all 0.15s", backdropFilter: "blur(8px)", boxShadow: filter === f.key ? "0 0 12px rgba(79,209,197,0.1)" : "none" }}>
            {f.label}
            {f.count > 0 && <span style={{ fontSize: 10, opacity: 0.7 }}>({f.count})</span>}
          </button>
        ))}
      </div>

      {/* ── Approval items ──────────────────────────────────────────────── */}
      {loading ? (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "48px 0" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: `2px solid transparent`, borderTopColor: T.teal, borderRightColor: "rgba(79,209,197,0.25)", animation: "ap_spin 0.85s linear infinite" }} />
        </div>
      ) : approvals.length === 0 ? (
        <div style={{ padding: "64px 0", textAlign: "center", border: "1px dashed rgba(52,211,153,0.12)", borderRadius: 20, background: "rgba(52,211,153,0.02)" }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(52,211,153,0.06)", border: "1px solid rgba(52,211,153,0.12)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 16px" }}>
            <FileCheck style={{ width: 28, height: 28, color: T.green, opacity: 0.5 }} />
          </div>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: "#e2e8f0", fontFamily: "Outfit, sans-serif", marginBottom: 8 }}>No Approvals</h3>
          <p style={{ fontSize: 12, color: "#475569" }}>When agents create publishable content, it will appear here for your review.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {approvals.map(item => {
            const cfg       = STATUS_META[item.status] || STATUS_META.draft;
            const Icon      = cfg.icon;
            const isExpanded= expanded[item.approval_id];
            const isLoading = actionLoading[item.approval_id];

            return (
              <div key={item.approval_id} data-testid={`approval-${item.approval_id}`}
                style={{ borderRadius: 14, background: T.glass, border: `1px solid ${T.border}`, backdropFilter: "blur(12px)", overflow: "hidden", transition: "border-color 0.15s" }}
                onMouseEnter={e => e.currentTarget.style.borderColor = "rgba(255,255,255,0.1)"}
                onMouseLeave={e => e.currentTarget.style.borderColor = T.border}>

                {/* Status top bar */}
                <div style={{ height: 2, background: `linear-gradient(90deg, ${cfg.color}, transparent)`, opacity: 0.6 }} />

                {/* Header row (collapsible trigger) */}
                <button
                  onClick={() => setExpanded(prev => ({ ...prev, [item.approval_id]: !prev[item.approval_id] }))}
                  style={{ width: "100%", display: "flex", alignItems: "center", gap: 12, padding: "14px 16px", background: "transparent", border: "none", cursor: "pointer", textAlign: "left" }}>
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: `${cfg.color}12`, border: `1px solid ${cfg.color}22`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    <Icon style={{ width: 16, height: 16, color: cfg.color }} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <p style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", margin: "0 0 3px" }}>{item.title}</p>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                      <span style={{ fontSize: 10, color: "#475569" }}>{TYPE_LABELS[item.type] || item.type}</span>
                      {item.agent_name && <span style={{ fontSize: 10, color: "#334155" }}>by {item.agent_name}</span>}
                      <span style={{ fontSize: 10, color: "#1e293b" }}>{new Date(item.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <span style={{ padding: "2px 8px", borderRadius: 20, background: `${cfg.color}12`, border: `1px solid ${cfg.color}22`, color: cfg.color, fontSize: 9, fontWeight: 700, flexShrink: 0 }}>{cfg.label}</span>
                  {isExpanded
                    ? <ChevronUp style={{ width: 14, height: 14, color: "#475569", flexShrink: 0 }} />
                    : <ChevronDown style={{ width: 14, height: 14, color: "#475569", flexShrink: 0 }} />}
                </button>

                {/* Expanded content */}
                {isExpanded && (
                  <div style={{ borderTop: `1px solid ${T.border}`, padding: 16 }}>
                    {/* Content preview */}
                    <div data-testid="approval-content-preview"
                      style={{ borderRadius: 11, background: "rgba(255,255,255,0.02)", border: `1px solid ${T.border}`, padding: 14, marginBottom: 12 }}>
                      <p style={{ fontSize: 9, color: "#475569", fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.1em", margin: "0 0 8px" }}>Content Preview</p>
                      <p style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6, margin: 0, whiteSpace: "pre-wrap" }}>{item.content}</p>
                    </div>

                    {/* Metadata tags */}
                    {item.metadata && Object.keys(item.metadata).length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 12 }}>
                        {Object.entries(item.metadata).map(([k, v]) => (
                          <span key={k} style={{ padding: "2px 8px", borderRadius: 6, background: "rgba(255,255,255,0.03)", border: `1px solid ${T.border}`, fontSize: 10, color: "#475569" }}>
                            <span style={{ color: "#334155" }}>{k}:</span> {String(v)}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Revision note */}
                    {item.rejection_reason && (
                      <div style={{ padding: "10px 14px", borderRadius: 10, background: "rgba(249,115,22,0.06)", border: "1px solid rgba(249,115,22,0.15)", marginBottom: 12 }}>
                        <p style={{ fontSize: 11, color: T.orange, margin: 0 }}>Revision note: {item.rejection_reason}</p>
                      </div>
                    )}

                    {/* Action buttons */}
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                      {item.status === "draft" && (
                        <>
                          <ActionBtn
                            color={T.green}
                            icon={isLoading === "approve" ? <Loader2 style={{ width: 12, height: 12, animation: "ap_spin 1s linear infinite" }} /> : <CheckCircle style={{ width: 12, height: 12 }} />}
                            label="Approve"
                            onClick={() => handleAction(item.approval_id, "approve")}
                            disabled={!!isLoading}
                            testId={`approve-btn-${item.approval_id}`}
                            gradient
                          />
                          <ActionBtn
                            color={T.orange}
                            icon={<XCircle style={{ width: 12, height: 12 }} />}
                            label="Request Revision"
                            onClick={() => handleAction(item.approval_id, "reject")}
                            disabled={!!isLoading}
                            testId={`reject-btn-${item.approval_id}`}
                          />
                        </>
                      )}
                      {item.status === "approved" && (
                        <ActionBtn
                          color={T.indigo}
                          icon={isLoading === "publish" ? <Loader2 style={{ width: 12, height: 12, animation: "ap_spin 1s linear infinite" }} /> : <Send style={{ width: 12, height: 12 }} />}
                          label="Publish Now"
                          onClick={() => handleAction(item.approval_id, "publish")}
                          disabled={!!isLoading}
                          testId={`publish-btn-${item.approval_id}`}
                          gradient
                        />
                      )}
                      <div style={{ flex: 1 }} />
                      <button
                        onClick={() => handleDelete(item.approval_id)}
                        data-testid={`delete-btn-${item.approval_id}`}
                        style={{ display: "flex", alignItems: "center", justifyContent: "center", width: 32, height: 32, borderRadius: 8, background: "transparent", border: `1px solid ${T.border}`, cursor: "pointer", color: "#334155", transition: "all 0.15s" }}
                        onMouseEnter={e => { e.currentTarget.style.color = T.red; e.currentTarget.style.borderColor = "rgba(248,113,113,0.25)"; e.currentTarget.style.background = "rgba(248,113,113,0.06)"; }}
                        onMouseLeave={e => { e.currentTarget.style.color = "#334155"; e.currentTarget.style.borderColor = T.border; e.currentTarget.style.background = "transparent"; }}>
                        <Trash2 style={{ width: 12, height: 12 }} />
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

function ActionBtn({ color, icon, label, onClick, disabled, testId, gradient }) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      data-testid={testId}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 9, border: "none", cursor: disabled ? "default" : "pointer", opacity: disabled ? 0.6 : 1, transition: "all 0.15s", fontSize: 12, fontWeight: 700,
        background: gradient
          ? (disabled ? `${color}12` : `${color}cc`)
          : (hovered ? `${color}18` : `${color}10`),
        color: gradient ? (disabled ? color : "#030712") : color,
        outline: gradient ? "none" : `1px solid ${color}25`,
      }}>
      {icon} {label}
    </button>
  );
}

export default Approvals;
