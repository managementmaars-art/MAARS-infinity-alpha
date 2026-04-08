import { useState, useEffect } from "react";
import { useAuth } from "../App";
import {
  Send, Megaphone, Phone, Mail, Calendar, Target, Globe, MessageCircle,
  TrendingUp, Play, Loader2, Check, ChevronDown, Plus, X, MapPin,
  Languages, BarChart3, Clock, Zap, RefreshCw, Eye, Share2,
  Video, Radio, Hash, BookOpen, AlertCircle, Activity
} from "lucide-react";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

const PLATFORM_META = {
  facebook:  { color: "#1877F2", icon: "https://cdn.simpleicons.org/facebook/1877F2",  label: "Facebook" },
  instagram: { color: "#E4405F", icon: "https://cdn.simpleicons.org/instagram/E4405F", label: "Instagram" },
  twitter:   { color: "#ffffff", icon: "https://cdn.simpleicons.org/x/white",          label: "X / Twitter" },
  tiktok:    { color: "#FF0050", icon: "https://cdn.simpleicons.org/tiktok/white",     label: "TikTok" },
  whatsapp:  { color: "#25D366", icon: "https://cdn.simpleicons.org/whatsapp/25D366",  label: "WhatsApp" },
  viber:     { color: "#7360F2", icon: "https://cdn.simpleicons.org/viber/7360F2",     label: "Viber" },
  line:      { color: "#06C755", icon: "https://cdn.simpleicons.org/line/06C755",      label: "LINE" },
  linkedin:  { color: "#0A66C2", icon: "https://cdn.simpleicons.org/linkedin/0A66C2",  label: "LinkedIn" },
  youtube:   { color: "#FF0000", icon: "https://cdn.simpleicons.org/youtube/FF0000",   label: "YouTube" },
  telegram:  { color: "#2AABEE", icon: "https://cdn.simpleicons.org/telegram/2AABEE",  label: "Telegram" },
};

const GEO_REGIONS = {
  north_america: { name: "North America", flag: "🇺🇸", primary_lang: "en" },
  south_america: { name: "South America", flag: "🇧🇷", primary_lang: "es" },
  western_europe: { name: "Western Europe", flag: "🇬🇧", primary_lang: "en" },
  eastern_europe: { name: "Eastern Europe", flag: "🇵🇱", primary_lang: "en" },
  middle_east: { name: "Middle East", flag: "🇦🇪", primary_lang: "ar" },
  south_asia: { name: "South Asia", flag: "🇮🇳", primary_lang: "hi" },
  southeast_asia: { name: "Southeast Asia", flag: "🇹🇭", primary_lang: "en" },
  east_asia: { name: "East Asia", flag: "🇯🇵", primary_lang: "ja" },
  africa: { name: "Africa", flag: "🌍", primary_lang: "en" },
  australia_nz: { name: "Australia & NZ", flag: "🇦🇺", primary_lang: "en" },
  global: { name: "Global", flag: "🌐", primary_lang: "en" },
};

const TABS = [
  { key: "compose", label: "Compose & Post", icon: Send },
  { key: "boost", label: "Boost & Promote", icon: TrendingUp },
  { key: "outreach", label: "Cold Outreach", icon: Megaphone },
  { key: "schedule", label: "Schedule", icon: Calendar },
  { key: "campaign", label: "Campaign Builder", icon: Target },
  { key: "analytics", label: "Analytics", icon: BarChart3 },
];

export default function SocialMediaCommand() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState("compose");
  const [accounts, setAccounts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [campaigns, setCampaigns] = useState([]);
  const [schedule, setSchedule] = useState([]);
  const [outreach, setOutreach] = useState({ emails: [], calls: [] });
  const [loading, setLoading] = useState(true);

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/social/accounts`, { headers: h }).then(r => r.ok ? r.json() : { accounts: [] }),
      fetch(`${API}/api/social/analytics`, { headers: h }).then(r => r.ok ? r.json() : null),
      fetch(`${API}/api/social/campaigns`, { headers: h }).then(r => r.ok ? r.json() : { campaigns: [] }),
      fetch(`${API}/api/social/schedule`, { headers: h }).then(r => r.ok ? r.json() : { scheduled: [] }),
      fetch(`${API}/api/social/outreach`, { headers: h }).then(r => r.ok ? r.json() : { emails: [], calls: [] }),
    ]).then(([acc, ana, camp, sched, out]) => {
      setAccounts(acc.accounts || []);
      setAnalytics(ana);
      setCampaigns(camp.campaigns || []);
      setSchedule(sched.scheduled || []);
      setOutreach(out);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, [token]);

  const connectedPlatforms = accounts.map(a => a.platform);

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-6 h-6 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );

  return (
    <div className="space-y-5" data-testid="social-media-command">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white font-['Outfit'] flex items-center gap-2">
            <Share2 className="w-6 h-6 text-teal-400" />
            Social Media Command
          </h1>
          <p className="text-sm text-zinc-400 mt-1">
            AI-powered omnichannel — post, message, boost, call, email, schedule across every platform, in every language.
          </p>
        </div>
        {/* Connected platforms strip */}
        <div className="flex items-center gap-1.5 flex-wrap">
          {connectedPlatforms.length === 0 ? (
            <a href="/integrations" className="text-xs text-teal-400 hover:underline flex items-center gap-1">
              <Plus className="w-3 h-3" /> Connect platforms in Integration Hub
            </a>
          ) : connectedPlatforms.map(p => {
            const meta = PLATFORM_META[p];
            if (!meta) return null;
            return (
              <div key={p} className="flex items-center gap-1.5 px-2 py-1 rounded-full" style={{ background: `${meta.color}15`, border: `1px solid ${meta.color}30` }}>
                <img src={meta.icon} alt={meta.label} className="w-3.5 h-3.5 object-contain" onError={e => { e.target.style.display = "none"; }} />
                <span className="text-[9px] font-medium" style={{ color: meta.color }}>{meta.label}</span>
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              </div>
            );
          })}
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-zinc-900/50 border border-white/5 rounded-xl p-1 overflow-x-auto">
        {TABS.map(tab => {
          const Icon = tab.icon;
          return (
            <button key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                activeTab === tab.key
                  ? "bg-teal-500/15 text-teal-400 border border-teal-500/30"
                  : "text-zinc-500 hover:text-white"
              }`}>
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab content */}
      {activeTab === "compose" && <ComposeTab connectedPlatforms={connectedPlatforms} h={h} />}
      {activeTab === "boost" && <BoostTab connectedPlatforms={connectedPlatforms} h={h} />}
      {activeTab === "outreach" && <OutreachTab outreach={outreach} h={h} />}
      {activeTab === "schedule" && <ScheduleTab schedule={schedule} h={h} />}
      {activeTab === "campaign" && <CampaignTab connectedPlatforms={connectedPlatforms} h={h} campaigns={campaigns} />}
      {activeTab === "analytics" && <AnalyticsTab analytics={analytics} accounts={accounts} />}
    </div>
  );
}

/* ── Compose Tab ─────────────────────────────────────────────────────────────── */
function ComposeTab({ connectedPlatforms, h }) {
  const [content, setContent] = useState("");
  const [platforms, setPlatforms] = useState([]);
  const [regions, setRegions] = useState([]);
  const [hashtags, setHashtags] = useState("");
  const [scheduleAt, setScheduleAt] = useState("");
  const [sending, setSending] = useState(false);

  const allPlatforms = Object.keys(PLATFORM_META);

  const togglePlatform = p => setPlatforms(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
  const toggleRegion = r => setRegions(prev => prev.includes(r) ? prev.filter(x => x !== r) : [...prev, r]);

  const publish = async () => {
    if (!content.trim()) { toast.error("Content is required"); return; }
    if (platforms.length === 0) { toast.error("Select at least one platform"); return; }
    setSending(true);
    let successCount = 0;
    for (const platform of platforms) {
      try {
        const res = await fetch(`${API}/api/social/post`, {
          method: "POST", headers: h,
          body: JSON.stringify({
            platform, content,
            hashtags: hashtags.split(" ").filter(Boolean),
            geo_regions: regions,
            scheduled_at: scheduleAt || null,
          }),
        });
        if (res.ok) successCount++;
      } catch {}
    }
    toast.success(`Posted to ${successCount} platform${successCount !== 1 ? "s" : ""}!`);
    setContent(""); setPlatforms([]); setHashtags(""); setScheduleAt(""); setRegions([]);
    setSending(false);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Content editor */}
        <div className="lg:col-span-2 bg-zinc-900/40 border border-white/5 rounded-xl p-4 space-y-3">
          <p className="text-xs font-semibold text-zinc-400">Content</p>
          <textarea
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Write your post content here... Agents will auto-translate for each selected region."
            rows={6}
            className="w-full bg-zinc-900/50 border border-white/5 rounded-lg px-3 py-2.5 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-teal-500/30 resize-none"
            data-testid="compose-content"
          />
          <div>
            <label className="text-[10px] text-zinc-500 font-medium">Hashtags (space-separated)</label>
            <input
              type="text" value={hashtags} onChange={e => setHashtags(e.target.value)}
              placeholder="#ai #automation #maars"
              className="w-full mt-0.5 bg-zinc-900/50 border border-white/5 rounded-lg px-3 py-2 text-sm text-white placeholder:text-zinc-600 focus:outline-none focus:border-teal-500/30"
            />
          </div>
          <div>
            <label className="text-[10px] text-zinc-500 font-medium">Schedule (leave empty to publish now)</label>
            <input
              type="datetime-local" value={scheduleAt} onChange={e => setScheduleAt(e.target.value)}
              className="w-full mt-0.5 bg-zinc-900/50 border border-white/5 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-teal-500/30"
            />
          </div>
          <div className="flex items-center gap-3 pt-1">
            <span className="text-xs text-zinc-600">{content.length} chars</span>
            <div className="flex-1" />
            <button
              onClick={publish} disabled={sending || !content || platforms.length === 0}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-black disabled:opacity-50 transition-all"
              style={{ background: "linear-gradient(135deg, #4fd1c5, #06b6d4)" }}
              data-testid="publish-btn">
              {sending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              {scheduleAt ? "Schedule" : "Publish Now"}
            </button>
          </div>
        </div>

        {/* Platform + Region selector */}
        <div className="space-y-3">
          <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
            <p className="text-xs font-semibold text-zinc-400 mb-3">Platforms</p>
            <div className="flex flex-wrap gap-2">
              {allPlatforms.map(p => {
                const meta = PLATFORM_META[p];
                const isConnected = connectedPlatforms.includes(p);
                const isSelected = platforms.includes(p);
                return (
                  <button key={p} onClick={() => togglePlatform(p)} disabled={!isConnected}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border transition-all disabled:opacity-30"
                    style={{
                      borderColor: isSelected ? `${meta.color}70` : "rgba(255,255,255,0.08)",
                      background: isSelected ? `${meta.color}20` : "transparent",
                    }}
                    data-testid={`platform-${p}`}>
                    <img src={meta.icon} alt={meta.label} className="w-3.5 h-3.5 object-contain" onError={e => { e.target.style.display = "none"; }} />
                    <span className="text-[10px] font-medium" style={{ color: isSelected ? meta.color : "#71717a" }}>{meta.label}</span>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
            <p className="text-xs font-semibold text-zinc-400 mb-1 flex items-center gap-1.5">
              <MapPin className="w-3 h-3" />Geographic Targeting
            </p>
            <p className="text-[9px] text-zinc-600 mb-3">Content auto-translated to each region's primary language</p>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(GEO_REGIONS).map(([key, reg]) => (
                <button key={key} onClick={() => toggleRegion(key)}
                  className={`flex items-center gap-1 px-2 py-1 rounded text-[9px] font-medium border transition-all ${
                    regions.includes(key) ? "bg-teal-500/15 border-teal-500/30 text-teal-400" : "border-white/8 text-zinc-600 hover:text-zinc-400"
                  }`}>
                  {reg.flag} {reg.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Boost Tab ───────────────────────────────────────────────────────────────── */
function BoostTab({ connectedPlatforms, h }) {
  const [platform, setPlatform] = useState("");
  const [postId, setPostId] = useState("");
  const [budget, setBudget] = useState(50);
  const [days, setDays] = useState(7);
  const [regions, setRegions] = useState(["global"]);
  const [objective, setObjective] = useState("engagement");
  const [autoTranslate, setAutoTranslate] = useState(true);
  const [ageMin, setAgeMin] = useState(18);
  const [ageMax, setAgeMax] = useState(55);
  const [interests, setInterests] = useState("");
  const [sending, setSending] = useState(false);
  const [result, setResult] = useState(null);

  const toggleRegion = r => setRegions(prev => prev.includes(r) ? prev.filter(x => x !== r) : [...prev, r]);

  const createBoost = async () => {
    if (!platform || !postId) { toast.error("Platform and Post ID required"); return; }
    setSending(true);
    try {
      const res = await fetch(`${API}/api/social/boost`, {
        method: "POST", headers: h,
        body: JSON.stringify({
          platform, post_id: postId, budget_usd: budget, geo_regions: regions,
          duration_days: days, objective, auto_translate: autoTranslate,
          target_age_min: ageMin, target_age_max: ageMax,
          target_interests: interests.split(",").map(s => s.trim()).filter(Boolean),
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setResult(data);
        toast.success("Boost campaign created!");
      }
    } catch { toast.error("Failed to create boost"); }
    setSending(false);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="space-y-4">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 space-y-3">
          <p className="text-xs font-semibold text-zinc-300 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-teal-400" />Advanced Post Boost
          </p>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-zinc-500">Platform</label>
              <select value={platform} onChange={e => setPlatform(e.target.value)}
                className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                <option value="">Select platform</option>
                {connectedPlatforms.filter(p => ["facebook","instagram","twitter","tiktok","linkedin","youtube"].includes(p)).map(p => (
                  <option key={p} value={p}>{PLATFORM_META[p]?.label}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-zinc-500">Post ID</label>
              <input type="text" value={postId} onChange={e => setPostId(e.target.value)}
                placeholder="post_id or URL" className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-zinc-500">Budget (USD): ${budget}</label>
              <input type="range" min={5} max={5000} value={budget} onChange={e => setBudget(Number(e.target.value))}
                className="w-full mt-1 accent-teal-400" />
            </div>
            <div>
              <label className="text-[10px] text-zinc-500">Duration: {days} days</label>
              <input type="range" min={1} max={90} value={days} onChange={e => setDays(Number(e.target.value))}
                className="w-full mt-1 accent-teal-400" />
            </div>
          </div>

          <div>
            <label className="text-[10px] text-zinc-500">Objective</label>
            <select value={objective} onChange={e => setObjective(e.target.value)}
              className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
              {["engagement","reach","clicks","conversions","leads","video_views","brand_awareness"].map(o => (
                <option key={o} value={o}>{o.replace("_", " ").replace(/\b\w/g, l => l.toUpperCase())}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-zinc-500">Age Min: {ageMin}</label>
              <input type="range" min={13} max={65} value={ageMin} onChange={e => setAgeMin(Number(e.target.value))} className="w-full mt-1 accent-teal-400" />
            </div>
            <div>
              <label className="text-[10px] text-zinc-500">Age Max: {ageMax}</label>
              <input type="range" min={18} max={65} value={ageMax} onChange={e => setAgeMax(Number(e.target.value))} className="w-full mt-1 accent-teal-400" />
            </div>
          </div>

          <div>
            <label className="text-[10px] text-zinc-500">Target Interests (comma-separated)</label>
            <input type="text" value={interests} onChange={e => setInterests(e.target.value)}
              placeholder="e.g. technology, startups, AI, business"
              className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
          </div>

          <div className="flex items-center gap-2">
            <input type="checkbox" id="autoTranslate" checked={autoTranslate} onChange={e => setAutoTranslate(e.target.checked)} className="accent-teal-400" />
            <label htmlFor="autoTranslate" className="text-[10px] text-zinc-400 flex items-center gap-1">
              <Languages className="w-3 h-3 text-teal-400" />Auto-translate copy per region
            </label>
          </div>

          <button onClick={createBoost} disabled={sending || !platform || !postId}
            className="w-full py-2 rounded-lg text-sm font-medium text-black disabled:opacity-40"
            style={{ background: "linear-gradient(135deg, #4fd1c5, #06b6d4)" }}
            data-testid="boost-btn">
            {sending ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : <TrendingUp className="w-4 h-4 inline mr-2" />}
            Create Boost Campaign
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {/* Geo-region selector */}
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-zinc-300 mb-1 flex items-center gap-2">
            <Globe className="w-4 h-4 text-amber-400" />Target Regions
          </p>
          <p className="text-[9px] text-zinc-600 mb-3">Budget distributed proportionally. Copy translated per region.</p>
          <div className="flex flex-wrap gap-1.5">
            {Object.entries(GEO_REGIONS).map(([key, reg]) => (
              <button key={key} onClick={() => toggleRegion(key)}
                className={`flex items-center gap-1 px-2.5 py-1 rounded text-[10px] font-medium border transition-all ${
                  regions.includes(key) ? "bg-amber-500/15 border-amber-500/30 text-amber-400" : "border-white/8 text-zinc-600 hover:text-zinc-400"
                }`}>
                {reg.flag} {reg.name}
              </button>
            ))}
          </div>
        </div>

        {/* Budget breakdown */}
        {regions.length > 0 && (
          <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
            <p className="text-xs font-semibold text-zinc-300 mb-3">Budget Breakdown</p>
            {regions.map(rk => {
              const reg = GEO_REGIONS[rk];
              const share = budget / regions.length;
              return (
                <div key={rk} className="flex items-center justify-between py-1.5 border-b border-white/5 last:border-0">
                  <span className="text-xs text-zinc-400">{reg.flag} {reg.name}</span>
                  <div className="text-right">
                    <span className="text-xs font-medium text-white">${share.toFixed(2)}</span>
                    <span className="text-[9px] text-zinc-600 ml-1">· {reg.primary_lang}</span>
                  </div>
                </div>
              );
            })}
            <div className="mt-2 pt-2 border-t border-white/5 flex justify-between">
              <span className="text-xs text-zinc-500">Est. reach</span>
              <span className="text-xs font-semibold text-teal-400">{(budget * 250).toLocaleString()}–{(budget * 500).toLocaleString()} people</span>
            </div>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl p-4">
            <p className="text-xs font-semibold text-emerald-400 mb-2 flex items-center gap-1.5">
              <Check className="w-4 h-4" />Campaign Created
            </p>
            <p className="text-[10px] text-zinc-400">ID: <span className="font-mono text-zinc-300">{result.campaign_id}</span></p>
            <p className="text-[10px] text-zinc-400">Est. reach: <span className="text-white font-medium">{result.estimated_total_reach}</span></p>
            <p className="text-[10px] text-zinc-600 mt-2">{result.message}</p>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Outreach Tab ──────────────────────────────────────────────────────────── */
function OutreachTab({ outreach, h }) {
  const [mode, setMode] = useState("email"); // email | call
  const [toEmail, setToEmail] = useState(""); const [toName, setToName] = useState("");
  const [subject, setSubject] = useState(""); const [body, setBody] = useState("");
  const [provider, setProvider] = useState("sendgrid");
  const [geoRegion, setGeoRegion] = useState("global");
  const [toPhone, setToPhone] = useState(""); const [script, setScript] = useState("");
  const [language, setLanguage] = useState("en");
  const [sending, setSending] = useState(false);

  const sendEmail = async () => {
    setSending(true);
    try {
      const res = await fetch(`${API}/api/social/cold-email`, {
        method: "POST", headers: h,
        body: JSON.stringify({ to_email: toEmail, to_name: toName, subject, body_html: body, provider, geo_region: geoRegion }),
      });
      if (res.ok) { toast.success("Cold email sent!"); setToEmail(""); setSubject(""); setBody(""); }
      else toast.error("Send failed — check email integration credentials");
    } catch { toast.error("Send failed"); }
    setSending(false);
  };

  const makeCall = async () => {
    setSending(true);
    try {
      const res = await fetch(`${API}/api/social/cold-call`, {
        method: "POST", headers: h,
        body: JSON.stringify({ to_phone: toPhone, script, language, geo_region: geoRegion }),
      });
      if (res.ok) { toast.success("Call initiated!"); setToPhone(""); setScript(""); }
      else toast.error("Call failed — ensure Twilio is connected");
    } catch { toast.error("Call failed"); }
    setSending(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        {[{key:"email",label:"Cold Email",icon:Mail},{key:"call",label:"Cold Call",icon:Phone}].map(m => {
          const Icon = m.icon;
          return (
            <button key={m.key} onClick={() => setMode(m.key)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                mode === m.key ? "bg-teal-500/15 border-teal-500/30 text-teal-400" : "border-white/10 text-zinc-500 hover:text-white"
              }`}>
              <Icon className="w-4 h-4" />{m.label}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 space-y-3">
          {mode === "email" ? (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] text-zinc-500">To Email</label>
                  <input type="email" value={toEmail} onChange={e => setToEmail(e.target.value)}
                    placeholder="client@company.com"
                    className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
                </div>
                <div>
                  <label className="text-[10px] text-zinc-500">Name</label>
                  <input type="text" value={toName} onChange={e => setToName(e.target.value)}
                    placeholder="John Smith"
                    className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
                </div>
              </div>
              <div>
                <label className="text-[10px] text-zinc-500">Subject</label>
                <input type="text" value={subject} onChange={e => setSubject(e.target.value)}
                  placeholder="Unlock AI-Powered Growth for Your Business"
                  className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
              </div>
              <div>
                <label className="text-[10px] text-zinc-500">Body (HTML)</label>
                <textarea value={body} onChange={e => setBody(e.target.value)} rows={5}
                  placeholder="<p>Hi {first_name},</p><p>I'd love to show you how MAARS can...</p>"
                  className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none resize-none font-mono" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] text-zinc-500">Provider</label>
                  <select value={provider} onChange={e => setProvider(e.target.value)}
                    className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                    <option value="sendgrid">SendGrid</option>
                    <option value="resend">Resend</option>
                  </select>
                </div>
                <div>
                  <label className="text-[10px] text-zinc-500">Target Region</label>
                  <select value={geoRegion} onChange={e => setGeoRegion(e.target.value)}
                    className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                    {Object.entries(GEO_REGIONS).map(([k, v]) => <option key={k} value={k}>{v.flag} {v.name}</option>)}
                  </select>
                </div>
              </div>
              <button onClick={sendEmail} disabled={sending || !toEmail || !subject}
                className="w-full py-2 rounded-lg text-sm font-medium text-black disabled:opacity-40"
                style={{ background: "linear-gradient(135deg, #ec4899, #a855f7)" }}
                data-testid="send-email-btn">
                {sending ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : <Mail className="w-4 h-4 inline mr-2" />}
                Send Cold Email
              </button>
            </>
          ) : (
            <>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-[10px] text-zinc-500">Phone (E.164)</label>
                  <input type="text" value={toPhone} onChange={e => setToPhone(e.target.value)}
                    placeholder="+12025551234"
                    className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none font-mono" />
                </div>
                <div>
                  <label className="text-[10px] text-zinc-500">Language</label>
                  <select value={language} onChange={e => setLanguage(e.target.value)}
                    className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                    {[["en","English"],["es","Spanish"],["fr","French"],["de","German"],["ar","Arabic"],["hi","Hindi"],["ja","Japanese"],["zh-cn","Chinese"],["pt","Portuguese"],["id","Indonesian"],["th","Thai"]].map(([code, name]) => (
                      <option key={code} value={code}>{name}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="text-[10px] text-zinc-500">Call Script (AI reads this aloud)</label>
                <textarea value={script} onChange={e => setScript(e.target.value)} rows={6}
                  placeholder="Hi, this is MAARS AI calling on behalf of [Your Company]. We help businesses like yours automate their workflow using cutting-edge AI agents..."
                  className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none resize-none" />
              </div>
              <button onClick={makeCall} disabled={sending || !toPhone || !script}
                className="w-full py-2 rounded-lg text-sm font-medium text-black disabled:opacity-40"
                style={{ background: "linear-gradient(135deg, #10b981, #06b6d4)" }}
                data-testid="call-btn">
                {sending ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : <Phone className="w-4 h-4 inline mr-2" />}
                Initiate Cold Call
              </button>
            </>
          )}
        </div>

        {/* History */}
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-zinc-400 mb-3 flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5" />Recent {mode === "email" ? "Emails" : "Calls"}
          </p>
          <div className="space-y-2">
            {(mode === "email" ? (outreach.emails || []) : (outreach.calls || [])).slice(0, 8).map((item, i) => (
              <div key={i} className="flex items-center justify-between py-1.5 border-b border-white/5 last:border-0">
                <div className="min-w-0 flex-1">
                  <p className="text-xs text-white truncate">{item.to_email || item.to_phone}</p>
                  <p className="text-[9px] text-zinc-600">{item.created_at?.slice(0, 10)}</p>
                </div>
                <span className={`text-[9px] px-2 py-0.5 rounded-full ${
                  item.status === "sent" || item.status === "initiated" ? "bg-emerald-500/15 text-emerald-400" : "bg-zinc-800 text-zinc-500"
                }`}>{item.status}</span>
              </div>
            ))}
            {!(mode === "email" ? outreach.emails : outreach.calls)?.length && (
              <p className="text-xs text-zinc-600 text-center py-6">No {mode === "email" ? "emails" : "calls"} yet</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

/* ── Schedule Tab ─────────────────────────────────────────────────────────── */
function ScheduleTab({ schedule, h }) {
  const [type, setType] = useState("post");
  const [title, setTitle] = useState(""); const [platform, setPlatform] = useState("");
  const [scheduledAt, setScheduledAt] = useState(""); const [content, setContent] = useState("");
  const [participants, setParticipants] = useState("");
  const [sending, setSending] = useState(false);

  const create = async () => {
    if (!title || !scheduledAt) { toast.error("Title and date required"); return; }
    setSending(true);
    const res = await fetch(`${API}/api/social/schedule`, {
      method: "POST", headers: h,
      body: JSON.stringify({ type, platform, title, scheduled_at: scheduledAt, content, participants: participants.split(",").map(s => s.trim()).filter(Boolean) }),
    });
    if (res.ok) { toast.success("Scheduled!"); setTitle(""); setScheduledAt(""); setContent(""); }
    setSending(false);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4 space-y-3">
        <p className="text-xs font-semibold text-zinc-300 flex items-center gap-2">
          <Calendar className="w-4 h-4 text-teal-400" />Schedule Action
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="text-[10px] text-zinc-500">Type</label>
            <select value={type} onChange={e => setType(e.target.value)}
              className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
              {["post","call","meeting","email","campaign"].map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
            </select>
          </div>
          <div>
            <label className="text-[10px] text-zinc-500">Platform (optional)</label>
            <select value={platform} onChange={e => setPlatform(e.target.value)}
              className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
              <option value="">Any</option>
              {Object.keys(PLATFORM_META).map(p => <option key={p} value={p}>{PLATFORM_META[p].label}</option>)}
            </select>
          </div>
        </div>
        <div>
          <label className="text-[10px] text-zinc-500">Title / Description</label>
          <input type="text" value={title} onChange={e => setTitle(e.target.value)} placeholder="Weekly product update post"
            className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
        </div>
        <div>
          <label className="text-[10px] text-zinc-500">Date & Time</label>
          <input type="datetime-local" value={scheduledAt} onChange={e => setScheduledAt(e.target.value)}
            className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
        </div>
        <div>
          <label className="text-[10px] text-zinc-500">Content (optional)</label>
          <textarea value={content} onChange={e => setContent(e.target.value)} rows={3} placeholder="Post content or call script..."
            className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none resize-none" />
        </div>
        <div>
          <label className="text-[10px] text-zinc-500">Participants (emails, comma-separated)</label>
          <input type="text" value={participants} onChange={e => setParticipants(e.target.value)} placeholder="alice@co.com, bob@co.com"
            className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none" />
        </div>
        <button onClick={create} disabled={sending || !title || !scheduledAt}
          className="w-full py-2 rounded-lg text-sm font-medium text-black disabled:opacity-40"
          style={{ background: "linear-gradient(135deg, #4fd1c5, #06b6d4)" }}>
          {sending ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : <Calendar className="w-4 h-4 inline mr-2" />}
          Schedule
        </button>
      </div>

      {/* Upcoming schedule */}
      <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
        <p className="text-xs font-semibold text-zinc-400 mb-3 flex items-center gap-1.5">
          <Clock className="w-3.5 h-3.5" />Upcoming Schedule
        </p>
        <div className="space-y-2">
          {schedule.slice(0, 10).map((item, i) => (
            <div key={i} className="flex items-start gap-3 p-2.5 rounded-lg bg-zinc-800/40 border border-white/5">
              <div className="w-7 h-7 rounded-lg bg-teal-500/15 flex items-center justify-center shrink-0 mt-0.5">
                {item.type === "post" ? <Send className="w-3.5 h-3.5 text-teal-400" /> :
                 item.type === "call" ? <Phone className="w-3.5 h-3.5 text-emerald-400" /> :
                 item.type === "meeting" ? <Calendar className="w-3.5 h-3.5 text-violet-400" /> :
                 <Mail className="w-3.5 h-3.5 text-pink-400" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-xs font-medium text-white truncate">{item.title}</p>
                <p className="text-[9px] text-zinc-600">{new Date(item.scheduled_at).toLocaleString()}</p>
                {item.platform && <span className="text-[8px] text-zinc-600">{PLATFORM_META[item.platform]?.label}</span>}
              </div>
              <span className="text-[9px] px-1.5 py-0.5 rounded bg-teal-500/15 text-teal-400">{item.type}</span>
            </div>
          ))}
          {!schedule.length && <p className="text-xs text-zinc-600 text-center py-6">No scheduled actions</p>}
        </div>
      </div>
    </div>
  );
}

/* ── Campaign Builder Tab ──────────────────────────────────────────────────── */
function CampaignTab({ connectedPlatforms, h, campaigns }) {
  const [name, setName] = useState(""); const [content, setContent] = useState("");
  const [platforms, setPlatforms] = useState([]); const [regions, setRegions] = useState([]);
  const [budget, setBudget] = useState(100); const [objective, setObjective] = useState("awareness");
  const [autoTranslate, setAutoTranslate] = useState(true); const [hashtags, setHashtags] = useState("");
  const [sending, setSending] = useState(false); const [result, setResult] = useState(null);

  const togglePlatform = p => setPlatforms(prev => prev.includes(p) ? prev.filter(x => x !== p) : [...prev, p]);
  const toggleRegion = r => setRegions(prev => prev.includes(r) ? prev.filter(x => x !== r) : [...prev, r]);

  const create = async () => {
    if (!name || !content || platforms.length === 0 || regions.length === 0) {
      toast.error("Fill in all required fields"); return;
    }
    setSending(true);
    try {
      const res = await fetch(`${API}/api/social/campaign`, {
        method: "POST", headers: h,
        body: JSON.stringify({ name, platforms, content, geo_regions: regions, boost_budget_usd: budget, auto_translate: autoTranslate, objective, hashtags: hashtags.split(" ").filter(Boolean) }),
      });
      if (res.ok) { const data = await res.json(); setResult(data); toast.success("Campaign created!"); }
    } catch { toast.error("Failed"); }
    setSending(false);
  };

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-zinc-900/40 border border-white/5 rounded-xl p-4 space-y-3">
          <p className="text-xs font-semibold text-zinc-300 flex items-center gap-2">
            <Target className="w-4 h-4 text-teal-400" />Multi-Platform Geo Campaign
          </p>
          <input type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Campaign Name"
            className="w-full bg-zinc-900/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white focus:outline-none" />
          <textarea value={content} onChange={e => setContent(e.target.value)} rows={4} placeholder="Campaign content — will be translated per region if auto-translate is on..."
            className="w-full bg-zinc-900/60 border border-white/8 rounded-lg px-3 py-2 text-sm text-white focus:outline-none resize-none" />
          <input type="text" value={hashtags} onChange={e => setHashtags(e.target.value)} placeholder="#hashtags space-separated"
            className="w-full bg-zinc-900/60 border border-white/8 rounded-lg px-3 py-2 text-xs text-white focus:outline-none" />
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-[10px] text-zinc-500">Objective</label>
              <select value={objective} onChange={e => setObjective(e.target.value)}
                className="w-full mt-0.5 bg-zinc-900/60 border border-white/8 rounded-lg px-2 py-2 text-xs text-white focus:outline-none">
                {["awareness","engagement","leads","conversions","traffic"].map(o => <option key={o} value={o}>{o.charAt(0).toUpperCase() + o.slice(1)}</option>)}
              </select>
            </div>
            <div>
              <label className="text-[10px] text-zinc-500">Boost Budget: ${budget}</label>
              <input type="range" min={0} max={10000} step={50} value={budget} onChange={e => setBudget(Number(e.target.value))} className="w-full mt-2 accent-teal-400" />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <input type="checkbox" id="camAutoTr" checked={autoTranslate} onChange={e => setAutoTranslate(e.target.checked)} className="accent-teal-400" />
            <label htmlFor="camAutoTr" className="text-[10px] text-zinc-400">Auto-translate content per region</label>
          </div>
          <button onClick={create} disabled={sending}
            className="w-full py-2 rounded-lg text-sm font-medium text-black disabled:opacity-40"
            style={{ background: "linear-gradient(135deg, #4fd1c5, #a855f7)" }}>
            {sending ? <Loader2 className="w-4 h-4 animate-spin inline mr-2" /> : <Zap className="w-4 h-4 inline mr-2" />}
            Launch Campaign
          </button>
        </div>

        <div className="space-y-3">
          <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
            <p className="text-[10px] text-zinc-500 font-semibold uppercase mb-2">Platforms</p>
            <div className="flex flex-wrap gap-1.5">
              {Object.keys(PLATFORM_META).map(p => {
                const meta = PLATFORM_META[p]; const sel = platforms.includes(p);
                return (
                  <button key={p} onClick={() => togglePlatform(p)}
                    className="flex items-center gap-1 px-2 py-1 rounded text-[9px] border transition-all"
                    style={{ borderColor: sel ? `${meta.color}60` : "rgba(255,255,255,0.08)", background: sel ? `${meta.color}15` : "transparent", color: sel ? meta.color : "#71717a" }}>
                    {meta.label}
                  </button>
                );
              })}
            </div>
          </div>
          <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
            <p className="text-[10px] text-zinc-500 font-semibold uppercase mb-2">Target Regions</p>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(GEO_REGIONS).map(([k, v]) => (
                <button key={k} onClick={() => toggleRegion(k)}
                  className={`text-[9px] px-2 py-1 rounded border transition-all ${regions.includes(k) ? "bg-teal-500/15 border-teal-500/30 text-teal-400" : "border-white/8 text-zinc-600"}`}>
                  {v.flag} {v.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Existing campaigns */}
      {campaigns.length > 0 && (
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-zinc-400 mb-3">Active Campaigns</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {campaigns.slice(0,6).map((c, i) => (
              <div key={i} className="p-3 rounded-lg bg-zinc-800/40 border border-white/5">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs font-medium text-white truncate">{c.name}</p>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded-full ${c.status === "active" ? "bg-emerald-500/15 text-emerald-400" : "bg-zinc-700 text-zinc-500"}`}>{c.status}</span>
                </div>
                <p className="text-[9px] text-zinc-600">{(c.platforms || []).join(" · ")} · {(c.geo_regions || []).length} regions</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

/* ── Analytics Tab ───────────────────────────────────────────────────────── */
function AnalyticsTab({ analytics, accounts }) {
  if (!analytics) return (
    <div className="text-center py-12 text-zinc-600">
      <BarChart3 className="w-8 h-8 mx-auto mb-2 opacity-40" />
      <p className="text-sm">No analytics data yet. Connect platforms and start posting to see metrics.</p>
    </div>
  );

  const { summary, platform_breakdown, recent_posts, active_campaigns } = analytics;

  const statCards = [
    { label: "Total Posts", value: summary?.total_posts || 0, icon: Send, color: "#4fd1c5" },
    { label: "Messages Sent", value: summary?.total_messages || 0, icon: MessageCircle, color: "#ec4899" },
    { label: "Campaigns", value: summary?.total_campaigns || 0, icon: Target, color: "#f59e0b" },
    { label: "Cold Emails", value: summary?.cold_emails_sent || 0, icon: Mail, color: "#10b981" },
    { label: "Cold Calls", value: summary?.cold_calls_initiated || 0, icon: Phone, color: "#8b5cf6" },
    { label: "Platforms", value: accounts.length, icon: Globe, color: "#06b6d4" },
  ];

  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {statCards.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="bg-zinc-900/40 border border-white/5 rounded-xl p-3">
              <div className="flex items-center gap-1.5 mb-2">
                <Icon className="w-3.5 h-3.5" style={{ color: stat.color }} />
                <p className="text-[9px] text-zinc-500 uppercase tracking-wider">{stat.label}</p>
              </div>
              <p className="text-2xl font-bold text-white">{stat.value.toLocaleString()}</p>
            </div>
          );
        })}
      </div>

      {Object.keys(platform_breakdown || {}).length > 0 && (
        <div className="bg-zinc-900/40 border border-white/5 rounded-xl p-4">
          <p className="text-xs font-semibold text-zinc-400 mb-3">Platform Breakdown</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {Object.entries(platform_breakdown).map(([p, stats]) => {
              const meta = PLATFORM_META[p];
              return (
                <div key={p} className="p-3 rounded-lg border" style={{ borderColor: `${meta?.color || "#fff"}20`, background: `${meta?.color || "#fff"}08` }}>
                  <div className="flex items-center gap-2 mb-2">
                    {meta && <img src={meta.icon} alt={meta.label} className="w-4 h-4 object-contain" onError={e => { e.target.style.display = "none"; }} />}
                    <span className="text-xs font-medium text-white">{meta?.label || p}</span>
                  </div>
                  <p className="text-xs text-zinc-500">{stats.posts} posts</p>
                  <p className="text-xs text-zinc-500">{stats.messages} messages</p>
                  {stats.total_reach > 0 && <p className="text-xs text-teal-400">{stats.total_reach.toLocaleString()} reach</p>}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
