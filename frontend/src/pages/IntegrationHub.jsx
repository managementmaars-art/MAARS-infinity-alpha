import { useState, useEffect } from "react";
import { useAuth } from "../App";
import {
  Link2, Unlink, Check, ExternalLink, Settings, ToggleLeft, ToggleRight,
  Zap, Globe, MessageCircle, Mail, Phone, Calendar, Database, Code,
  Share2, Radio, Users, ChevronDown, ChevronUp, Shield, Target,
  MapPin, Languages, TrendingUp, Megaphone, Video, Play, Send,
  Hash, BookOpen, Activity, Plus, X, AlertCircle
} from "lucide-react";
import { toast } from "sonner";

const API = process.env.REACT_APP_BACKEND_URL;

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
const STYLES = `@keyframes fadeUp { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:none} } @keyframes spin { to{transform:rotate(360deg)} }`;
const formInput = { background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,0.08)", borderRadius: 8, padding: "8px 12px", color: "#fff", fontSize: 13, outline: "none", fontFamily: "inherit", width: "100%", boxSizing: "border-box", transition: "border-color .2s" };

/* ── Platform color + icon map ─────────────────────────────────────────────── */
const PLATFORM_META = {
  facebook:  { color: "#1877F2", bg: "rgba(24,119,242,0.1)",  icon: "https://cdn.simpleicons.org/facebook/1877F2",  label: "Facebook",      category: "social_media" },
  instagram: { color: "#E4405F", bg: "rgba(228,64,95,0.1)",   icon: "https://cdn.simpleicons.org/instagram/E4405F", label: "Instagram",     category: "social_media" },
  twitter:   { color: "#000000", bg: "rgba(255,255,255,0.06)",icon: "https://cdn.simpleicons.org/x/white",          label: "X (Twitter)",   category: "social_media" },
  tiktok:    { color: "#FF0050", bg: "rgba(255,0,80,0.1)",    icon: "https://cdn.simpleicons.org/tiktok/white",    label: "TikTok",        category: "social_media" },
  whatsapp:  { color: "#25D366", bg: "rgba(37,211,102,0.1)",  icon: "https://cdn.simpleicons.org/whatsapp/25D366", label: "WhatsApp",      category: "social_media" },
  viber:     { color: "#7360F2", bg: "rgba(115,96,242,0.1)",  icon: "https://cdn.simpleicons.org/viber/7360F2",    label: "Viber",         category: "social_media" },
  line:      { color: "#06C755", bg: "rgba(6,199,85,0.1)",    icon: "https://cdn.simpleicons.org/line/06C755",     label: "LINE",          category: "social_media" },
  linkedin:  { color: "#0A66C2", bg: "rgba(10,102,194,0.1)",  icon: "https://cdn.simpleicons.org/linkedin/0A66C2", label: "LinkedIn",      category: "social_media" },
  youtube:   { color: "#FF0000", bg: "rgba(255,0,0,0.1)",     icon: "https://cdn.simpleicons.org/youtube/FF0000",  label: "YouTube",       category: "social_media" },
  telegram:  { color: "#2AABEE", bg: "rgba(42,171,238,0.1)",  icon: "https://cdn.simpleicons.org/telegram/2AABEE",label: "Telegram",      category: "social_media" },
  slack:     { color: "#E01E5A", bg: "rgba(224,30,90,0.1)",   icon: "https://cdn.simpleicons.org/slack/E01E5A",    label: "Slack",         category: "productivity" },
  github:    { color: "#ffffff", bg: "rgba(255,255,255,0.06)",icon: "https://cdn.simpleicons.org/github/white",    label: "GitHub",        category: "development" },
  sendgrid:  { color: "#1A82E2", bg: "rgba(26,130,226,0.1)",  icon: "https://cdn.simpleicons.org/sendgrid/1A82E2", label: "SendGrid",      category: "email" },
  resend:    { color: "#ffffff", bg: "rgba(255,255,255,0.06)",icon: "https://cdn.simpleicons.org/resend/white",    label: "Resend",        category: "email" },
  twilio:    { color: "#F22F46", bg: "rgba(242,47,70,0.1)",   icon: "https://cdn.simpleicons.org/twilio/F22F46",  label: "Twilio",        category: "communications" },
  airtable:  { color: "#18BFFF", bg: "rgba(24,191,255,0.1)",  icon: "https://cdn.simpleicons.org/airtable/18BFFF",label: "Airtable",      category: "productivity" },
  calendly:  { color: "#006BFF", bg: "rgba(0,107,255,0.1)",   icon: "https://cdn.simpleicons.org/calendly/006BFF",label: "Calendly",      category: "scheduling" },
  google_suite:{ color:"#4285F4",bg:"rgba(66,133,244,0.1)",   icon: "https://cdn.simpleicons.org/google/4285F4",  label: "Google Suite",  category: "productivity" },
};

const CAPABILITY_ICONS = {
  post: Play, message: MessageCircle, boost: TrendingUp, call: Phone,
  dm: MessageCircle, tweet: Send, broadcast: Radio, email: Mail,
  ads: Megaphone, geo_target: MapPin, analytics: Activity, upload: Video,
  reply: MessageCircle, schedule: Calendar, lead_gen: Target, article: BookOpen,
  template: Hash, inmail: Mail, channel: Hash,
};

const CATEGORIES = {
  social_media: { label: "Social Media & Messaging", icon: Share2, color: "#4fd1c5", description: "Connect platforms for AI-powered posting, messaging, boosting & geo-targeting" },
  communications: { label: "Communications & Outreach", icon: Phone, color: "#f59e0b", description: "Cold calls, SMS, voice campaigns" },
  email: { label: "Email & Cold Outreach", icon: Mail, color: "#ec4899", description: "Transactional email, cold outreach, campaigns" },
  scheduling: { label: "Scheduling & Calendar", icon: Calendar, color: "#10b981", description: "Book meetings, schedule calls, manage events" },
  productivity: { label: "Productivity & Data", icon: Database, color: "#8b5cf6", description: "Airtable, Google Suite, Slack" },
  development: { label: "Development", icon: Code, color: "#64748b", description: "GitHub repos, PRs, issues" },
};

const GEO_REGIONS = {
  north_america: "North America",
  south_america: "South America",
  western_europe: "Western Europe",
  eastern_europe: "Eastern Europe",
  middle_east: "Middle East",
  south_asia: "South Asia",
  southeast_asia: "Southeast Asia",
  east_asia: "East Asia",
  africa: "Africa",
  australia_nz: "Australia & NZ",
  global: "Global",
};

const PLATFORM_FIELDS = {
  facebook:   [
    { key: "page_access_token", label: "Page Access Token", type: "password", help: "Get from Facebook Developers > Your App > Graph API Explorer" },
    { key: "page_id", label: "Facebook Page ID", type: "text", help: "Found in Page Settings > About" },
    { key: "app_id", label: "App ID", type: "text", help: "From Facebook Developers dashboard" },
    { key: "app_secret", label: "App Secret", type: "password", help: "From Facebook Developers dashboard" },
  ],
  instagram:  [
    { key: "access_token", label: "Instagram Access Token", type: "password", help: "Facebook Graph API — requires Instagram Business Account" },
    { key: "instagram_business_account_id", label: "Instagram Business Account ID", type: "text", help: "From Facebook Graph API or Business Manager" },
  ],
  twitter:    [
    { key: "api_key", label: "API Key", type: "password", help: "From Twitter Developer Portal > App > Keys & Tokens" },
    { key: "api_secret", label: "API Secret", type: "password" },
    { key: "access_token", label: "Access Token", type: "password" },
    { key: "access_token_secret", label: "Access Token Secret", type: "password" },
    { key: "bearer_token", label: "Bearer Token", type: "password" },
  ],
  tiktok:     [
    { key: "access_token", label: "Access Token", type: "password", help: "From TikTok for Developers > Apps" },
    { key: "advertiser_id", label: "Advertiser ID", type: "text" },
    { key: "app_id", label: "App ID", type: "text" },
  ],
  whatsapp:   [
    { key: "phone_number_id", label: "Phone Number ID", type: "text", help: "From Meta Business Suite > WhatsApp > Phone Numbers" },
    { key: "access_token", label: "Access Token", type: "password" },
    { key: "waba_id", label: "WhatsApp Business Account ID", type: "text" },
  ],
  viber:      [{ key: "auth_token", label: "Auth Token", type: "password", help: "From Viber Partners — requires approved Bot/Business account" }],
  line:       [
    { key: "channel_access_token", label: "Channel Access Token", type: "password", help: "From LINE Developers Console > Messaging API channel" },
    { key: "channel_secret", label: "Channel Secret", type: "password" },
  ],
  linkedin:   [
    { key: "access_token", label: "Access Token", type: "password", help: "From LinkedIn Developers > Your App > Auth" },
    { key: "organization_id", label: "Organization / Company ID", type: "text" },
  ],
  youtube:    [
    { key: "api_key", label: "API Key", type: "password", help: "From Google Cloud Console > APIs & Services > Credentials" },
    { key: "oauth_client_id", label: "OAuth Client ID", type: "text" },
    { key: "oauth_client_secret", label: "OAuth Client Secret", type: "password" },
  ],
  telegram:   [
    { key: "bot_token", label: "Bot Token", type: "password", help: "Create a bot via @BotFather on Telegram" },
    { key: "channel_username", label: "Channel Username", type: "text", help: "e.g. @MyChannel" },
  ],
  slack:      [{ key: "bot_token", label: "Bot Token", type: "password", help: "From api.slack.com/apps > OAuth & Permissions" }],
  github:     [{ key: "personal_access_token", label: "Personal Access Token", type: "password", help: "github.com/settings/tokens" }],
  sendgrid:   [{ key: "api_key", label: "API Key", type: "password", help: "app.sendgrid.com/settings/api_keys" }],
  resend:     [{ key: "api_key", label: "API Key", type: "password", help: "resend.com/api-keys" }],
  twilio:     [
    { key: "account_sid", label: "Account SID", type: "text", help: "console.twilio.com" },
    { key: "auth_token", label: "Auth Token", type: "password" },
    { key: "phone_number", label: "Phone Number", type: "text", help: "E.164 format: +1234567890" },
  ],
  airtable:   [{ key: "api_key", label: "API Key", type: "password", help: "airtable.com/create/tokens" }],
  calendly:   [{ key: "api_key", label: "API Key", type: "password", help: "calendly.com/integrations/api_webhooks" }],
  google_suite:[
    { key: "service_account_json", label: "Service Account JSON", type: "password", help: "console.cloud.google.com/iam-admin/serviceaccounts" },
    { key: "delegate_email", label: "Delegate Email", type: "text" },
  ],
};

const PLATFORM_CAPABILITIES = {
  facebook:  ["post", "story", "reel", "message", "boost", "reply", "ads", "geo_target", "analytics"],
  instagram: ["post", "reel", "story", "dm", "boost", "reply", "hashtag", "geo_target", "analytics"],
  twitter:   ["tweet", "reply", "dm", "thread", "ads", "analytics"],
  tiktok:    ["post", "boost", "ads", "geo_target", "analytics"],
  whatsapp:  ["message", "call", "broadcast", "template", "reply", "geo_target"],
  viber:     ["message", "broadcast", "reply"],
  line:      ["message", "broadcast", "reply", "schedule"],
  linkedin:  ["post", "article", "inmail", "ads", "lead_gen", "geo_target", "analytics"],
  youtube:   ["upload", "reply", "ads", "analytics", "schedule"],
  telegram:  ["message", "broadcast", "channel"],
  slack:     ["message", "broadcast"],
  github:    ["post"],
  sendgrid:  ["email"],
  resend:    ["email"],
  twilio:    ["call", "message"],
  airtable:  ["post"],
  calendly:  ["schedule"],
  google_suite: ["email", "schedule"],
};

const DOCS_URLS = {
  facebook: "https://developers.facebook.com/docs/graph-api/",
  instagram: "https://developers.facebook.com/docs/instagram-api/",
  twitter: "https://developer.twitter.com/en/docs/twitter-api",
  tiktok: "https://ads.tiktok.com/marketing_api/docs",
  whatsapp: "https://developers.facebook.com/docs/whatsapp/cloud-api/",
  viber: "https://developers.viber.com/docs/api/rest-bot-api/",
  line: "https://developers.line.biz/en/docs/messaging-api/",
  linkedin: "https://learn.microsoft.com/en-us/linkedin/",
  youtube: "https://developers.google.com/youtube/v3",
  telegram: "https://core.telegram.org/bots/api",
  slack: "https://api.slack.com/apps",
  github: "https://github.com/settings/tokens",
  sendgrid: "https://app.sendgrid.com/settings/api_keys",
  resend: "https://resend.com/api-keys",
  twilio: "https://console.twilio.com/",
  airtable: "https://airtable.com/create/tokens",
  calendly: "https://calendly.com/integrations/api_webhooks",
  google_suite: "https://console.cloud.google.com/iam-admin/serviceaccounts",
};

export default function IntegrationHub() {
  const { token } = useAuth();
  const [connected, setConnected] = useState({});       // platform → creds
  const [configuring, setConfiguring] = useState(null); // platform being configured
  const [configValues, setConfigValues] = useState({});
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expandedCategory, setExpandedCategory] = useState("social_media");
  const [testingPlatform, setTestingPlatform] = useState(null);
  const [filterCap, setFilterCap] = useState(null);
  const [geoSetup, setGeoSetup] = useState(null);

  const h = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchConnected = async () => {
    try {
      const res = await fetch(`${API}/api/social/accounts`, { headers: h });
      if (res.ok) {
        const data = await res.json();
        const map = {};
        (data.accounts || []).forEach(a => { map[a.platform] = a; });
        setConnected(map);
      }
      // Also fetch kernel integrations
      const ki = await fetch(`${API}/api/kernel/integrations/available`, { headers: h });
      if (ki.ok) {
        const kdata = await ki.json();
        const connIds = new Set(kdata.connected_ids || []);
        connIds.forEach(id => {
          if (!map) return;
          // merge kernel connections
        });
      }
    } catch {}
    setLoading(false);
  };

  useEffect(() => { fetchConnected(); }, [token]);

  const handleSaveConnect = async (platform) => {
    setSaving(true);
    try {
      const res = await fetch(`${API}/api/social/connect`, {
        method: "POST", headers: h,
        body: JSON.stringify({ platform, credentials: configValues }),
      });
      if (res.ok) {
        toast.success(`${PLATFORM_META[platform]?.label || platform} connected!`);
        setConfiguring(null);
        setConfigValues({});
        fetchConnected();
      } else {
        toast.error("Failed to connect — check credentials");
      }
    } catch { toast.error("Connection failed"); }
    setSaving(false);
  };

  const handleDisconnect = async (platform) => {
    await fetch(`${API}/api/social/connect/${platform}`, { method: "DELETE", headers: h });
    toast.success(`${PLATFORM_META[platform]?.label} disconnected`);
    fetchConnected();
  };

  // Group platforms by category
  const platformsByCategory = {};
  Object.entries(PLATFORM_META).forEach(([id, meta]) => {
    const cat = meta.category;
    if (!platformsByCategory[cat]) platformsByCategory[cat] = [];
    platformsByCategory[cat].push(id);
  });

  const connectedCount = Object.keys(connected).length;
  const socialConnected = Object.keys(connected).filter(p => PLATFORM_META[p]?.category === "social_media").length;

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 256 }}>
      <div style={{ width: 24, height: 24, border: "2px solid #22d3ee", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
    </div>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, animation: "fadeUp .4s ease" }} data-testid="integration-hub">
      <style>{STYLES}</style>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
        <div>
          <h1 style={{ fontSize: 24, fontWeight: 700, color: "#fff", fontFamily: "Outfit, sans-serif", margin: 0 }}>Integration Hub</h1>
          <p style={{ fontSize: 13, color: T.zinc, marginTop: 4, margin: "4px 0 0" }}>
            Connect social platforms so your agents can post, message, boost, call, and run geo-targeted campaigns — autonomously.
          </p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{ textAlign: "right" }}>
            <p style={{ fontSize: 11, color: "#52525b", margin: 0 }}>Connected</p>
            <p style={{ fontSize: 18, fontWeight: 700, color: "#fff", margin: 0 }}>{connectedCount} <span style={{ fontSize: 11, color: "#52525b", fontWeight: 400 }}>platforms</span></p>
          </div>
          <div style={{ width: 1, height: 32, background: "rgba(255,255,255,0.1)" }} />
          <div style={{ textAlign: "right" }}>
            <p style={{ fontSize: 11, color: "#52525b", margin: 0 }}>Social Media</p>
            <p style={{ fontSize: 18, fontWeight: 700, color: "#4fd1c5", margin: 0 }}>{socialConnected}</p>
          </div>
        </div>
      </div>

      {/* Connected platforms strip */}
      {connectedCount > 0 && (
        <div style={{ background: "rgba(24,24,27,0.4)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 12, padding: 16 }}>
          <p style={{ fontSize: 10, color: "#52525b", textTransform: "uppercase", letterSpacing: "0.08em", fontWeight: 600, marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
            <Check style={{ width: 12, height: 12, color: "#34d399" }} /> Active Connections
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {Object.entries(connected).map(([platform, info]) => {
              const meta = PLATFORM_META[platform];
              if (!meta) return null;
              return (
                <div key={platform}
                  style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 12px", borderRadius: 999, border: `1px solid ${meta.color}40`, background: meta.bg }}>
                  <img src={meta.icon} alt={meta.label} style={{ width: 14, height: 14, objectFit: "contain" }}
                    onError={e => { e.target.style.display = "none"; }} />
                  <span style={{ fontSize: 12, fontWeight: 500, color: meta.color }}>{meta.label}</span>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399" }} />
                  <button onClick={() => handleDisconnect(platform)} style={{ color: "#52525b", background: "none", border: "none", cursor: "pointer", padding: 0, display: "flex", alignItems: "center" }}>
                    <X style={{ width: 12, height: 12 }} />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Capability filter */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
        {["post", "message", "boost", "call", "email", "geo_target", "analytics", "schedule"].map(cap => (
          <button key={cap}
            onClick={() => setFilterCap(filterCap === cap ? null : cap)}
            style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "4px 10px", borderRadius: 999, fontSize: 10, fontWeight: 500,
              border: filterCap === cap ? "1px solid rgba(79,209,197,0.4)" : "1px solid rgba(255,255,255,0.1)",
              background: filterCap === cap ? "rgba(79,209,197,0.15)" : "transparent",
              color: filterCap === cap ? "#4fd1c5" : T.zinc,
              cursor: "pointer", transition: "all .2s", fontFamily: "inherit",
            }}>
            {cap.replace("_", " ")}
          </button>
        ))}
        {filterCap && (
          <button onClick={() => setFilterCap(null)} style={{ fontSize: 10, color: "#52525b", background: "none", border: "none", cursor: "pointer", padding: "4px 8px", fontFamily: "inherit" }}>
            clear
          </button>
        )}
      </div>

      {/* Categories */}
      {Object.entries(CATEGORIES).map(([catKey, catMeta]) => {
        const platformIds = (platformsByCategory[catKey] || []).filter(pid => {
          if (!filterCap) return true;
          return (PLATFORM_CAPABILITIES[pid] || []).includes(filterCap);
        });
        if (platformIds.length === 0) return null;

        const Icon = catMeta.icon;
        const isExpanded = expandedCategory === catKey;

        return (
          <div key={catKey} style={{ border: "1px solid rgba(255,255,255,0.05)", borderRadius: 12, overflow: "hidden" }}>
            {/* Category header */}
            <button
              style={{ width: "100%", display: "flex", alignItems: "center", gap: 12, padding: 16, background: "rgba(24,24,27,0.3)", border: "none", cursor: "pointer", textAlign: "left", transition: "background .2s", fontFamily: "inherit" }}
              onClick={() => setExpandedCategory(isExpanded ? null : catKey)}>
              <div style={{ width: 32, height: 32, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", background: `${catMeta.color}18` }}>
                <Icon style={{ width: 16, height: 16, color: catMeta.color }} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ fontSize: 14, fontWeight: 600, color: "#fff", margin: 0 }}>{catMeta.label}</p>
                <p style={{ fontSize: 10, color: T.zinc, margin: 0 }}>{catMeta.description}</p>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 10, color: "#52525b" }}>{platformIds.filter(p => connected[p]).length}/{platformIds.length} connected</span>
                {isExpanded ? <ChevronUp style={{ width: 16, height: 16, color: "#52525b" }} /> : <ChevronDown style={{ width: 16, height: 16, color: "#52525b" }} />}
              </div>
            </button>

            {/* Platform cards */}
            {isExpanded && (
              <div style={{ padding: 16, display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: 12, background: "rgba(9,9,11,0.3)" }}>
                {platformIds.map(platformId => (
                  <PlatformCard
                    key={platformId}
                    platformId={platformId}
                    meta={PLATFORM_META[platformId]}
                    fields={PLATFORM_FIELDS[platformId] || []}
                    capabilities={PLATFORM_CAPABILITIES[platformId] || []}
                    isConnected={!!connected[platformId]}
                    isConfiguring={configuring === platformId}
                    configValues={configValues}
                    saving={saving}
                    testing={testingPlatform === platformId}
                    docsUrl={DOCS_URLS[platformId]}
                    onConfigure={() => { setConfiguring(platformId); setConfigValues({}); }}
                    onCancel={() => { setConfiguring(null); setConfigValues({}); }}
                    onFieldChange={(key, val) => setConfigValues(prev => ({ ...prev, [key]: val }))}
                    onSave={() => handleSaveConnect(platformId)}
                    onDisconnect={() => handleDisconnect(platformId)}
                  />
                ))}
              </div>
            )}
          </div>
        );
      })}

      {/* What agents can do section */}
      <div style={{ background: "rgba(24,24,27,0.3)", border: "1px solid rgba(255,255,255,0.05)", borderRadius: 12, padding: 20 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, color: "#fff", marginBottom: 16, display: "flex", alignItems: "center", gap: 8, marginTop: 0 }}>
          <Zap style={{ width: 16, height: 16, color: "#4fd1c5" }} />
          What Your Agents Can Do When Connected
        </h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 12 }}>
          {[
            { icon: Megaphone, title: "Post & Publish", desc: "Auto-generate and post content to Facebook, Instagram, Twitter, TikTok, LinkedIn, YouTube in one click", color: "#4fd1c5" },
            { icon: Target, title: "Geo-Targeted Boost", desc: "Boost posts to specific geographic regions with the right language, age group, and interests automatically", color: "#f59e0b" },
            { icon: MessageCircle, title: "Send & Reply to Messages", desc: "Send DMs on WhatsApp, Instagram, Viber, LINE, Telegram. Reply to comments and mentions across all platforms", color: "#ec4899" },
            { icon: Mail, title: "Cold Email Campaigns", desc: "Send personalized cold emails via SendGrid or Resend with geo-aware language selection and CRM tracking", color: "#10b981" },
            { icon: Phone, title: "Cold Calls via AI", desc: "Initiate Twilio voice calls with AI-generated scripts in the language of the target region", color: "#8b5cf6" },
            { icon: Calendar, title: "Schedule Everything", desc: "Book meetings, schedule posts, calls, and campaigns — Calendly integration for fully automated scheduling", color: "#06b6d4" },
            { icon: Languages, title: "Multi-Language Content", desc: "Agents auto-translate content for each target region — Japanese for Japan, Arabic for Middle East, Thai for Thailand", color: "#f97316" },
            { icon: TrendingUp, title: "Non-Traditional Boosting", desc: "Beyond simple boosts: A/B test creatives by region, optimize bid strategy, spark ads on TikTok, LinkedIn lead gen", color: "#84cc16" },
            { icon: Globe, title: "Geographic Client Targeting", desc: "Pull clients from specific regions by geo-targeting ads and content — Southeast Asia, Middle East, Europe, Africa", color: "#e879f9" },
          ].map((item, i) => {
            const Icon = item.icon;
            return (
              <div key={i} style={{ display: "flex", gap: 12, padding: 12, borderRadius: 8, background: "rgba(39,39,42,0.3)", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div style={{ width: 32, height: 32, borderRadius: 8, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, background: `${item.color}15` }}>
                  <Icon style={{ width: 16, height: 16, color: item.color }} />
                </div>
                <div>
                  <p style={{ fontSize: 12, fontWeight: 600, color: "#fff", margin: "0 0 2px" }}>{item.title}</p>
                  <p style={{ fontSize: 10, color: T.zinc, lineHeight: 1.5, margin: 0 }}>{item.desc}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function PlatformCard({ platformId, meta, fields, capabilities, isConnected, isConfiguring, configValues, saving, testing, docsUrl, onConfigure, onCancel, onFieldChange, onSave, onDisconnect }) {
  const [showHelp, setShowHelp] = useState(null);

  return (
    <div
      style={{
        borderRadius: 12,
        border: `1px solid ${isConnected ? `${meta.color}40` : "rgba(255,255,255,0.06)"}`,
        background: isConnected ? meta.bg : "rgba(9,9,11,0.5)",
        transition: "all .2s",
      }}
      data-testid={`integration-${platformId}`}>

      {/* Platform header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, padding: 12 }}>
        <div style={{ width: 36, height: 36, borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, background: meta.bg, border: `1px solid ${meta.color}30` }}>
          <img src={meta.icon} alt={meta.label} style={{ width: 20, height: 20, objectFit: "contain" }}
            onError={e => { e.target.style.display = "none"; }} />
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <p style={{ fontSize: 14, fontWeight: 600, color: "#fff", margin: 0 }}>{meta.label}</p>
            {isConnected && <Check style={{ width: 14, height: 14, color: "#34d399" }} />}
          </div>
          <p style={{ fontSize: 9, color: T.zinc, margin: 0 }}>{meta.category.replace("_", " ")}</p>
        </div>
        {docsUrl && (
          <a href={docsUrl} target="_blank" rel="noopener noreferrer" style={{ color: "#52525b", display: "flex" }}>
            <ExternalLink style={{ width: 14, height: 14 }} />
          </a>
        )}
      </div>

      {/* Capabilities */}
      <div style={{ padding: "0 12px 8px", display: "flex", flexWrap: "wrap", gap: 4 }}>
        {capabilities.slice(0, 5).map(cap => {
          const Icon = CAPABILITY_ICONS[cap] || Zap;
          return (
            <span key={cap} style={{ display: "inline-flex", alignItems: "center", gap: 2, fontSize: 8, padding: "2px 6px", borderRadius: 4, background: "rgba(39,39,42,0.6)", color: T.zinc }}>
              <Icon style={{ width: 10, height: 10 }} />{cap.replace("_", " ")}
            </span>
          );
        })}
        {capabilities.length > 5 && (
          <span style={{ fontSize: 8, padding: "2px 6px", borderRadius: 4, background: "rgba(39,39,42,0.6)", color: "#52525b" }}>
            +{capabilities.length - 5}
          </span>
        )}
      </div>

      {/* Config form */}
      {isConfiguring && (
        <div style={{ margin: "0 12px 12px", padding: 12, background: "rgba(24,24,27,0.6)", borderRadius: 8, border: "1px solid rgba(255,255,255,0.05)", display: "flex", flexDirection: "column", gap: 8 }}>
          {fields.map(field => (
            <div key={field.key}>
              <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 2 }}>
                <label style={{ fontSize: 9, color: "#a1a1aa", fontWeight: 500 }}>{field.label}</label>
                {field.help && (
                  <button onClick={() => setShowHelp(showHelp === field.key ? null : field.key)} style={{ color: "#52525b", background: "none", border: "none", cursor: "pointer", padding: 0, display: "flex", alignItems: "center" }}>
                    <AlertCircle style={{ width: 10, height: 10 }} />
                  </button>
                )}
              </div>
              {showHelp === field.key && (
                <p style={{ fontSize: 8, color: T.amber, background: "rgba(245,158,11,0.1)", padding: "4px 8px", borderRadius: 4, marginBottom: 4, margin: "0 0 4px" }}>{field.help}</p>
              )}
              <input
                type={field.type || "text"}
                placeholder={`Enter ${field.label}`}
                value={configValues[field.key] || ""}
                onChange={e => onFieldChange(field.key, e.target.value)}
                style={{ ...formInput, fontSize: 10, padding: "6px 8px", fontFamily: "monospace" }}
                data-testid={`config-${platformId}-${field.key}`}
              />
            </div>
          ))}
        </div>
      )}

      {/* Actions */}
      <div style={{ padding: "0 12px 12px", display: "flex", alignItems: "center", gap: 8 }}>
        {isConnected ? (
          <>
            <span style={{ fontSize: 10, color: "#34d399", display: "flex", alignItems: "center", gap: 4 }}>
              <div style={{ width: 6, height: 6, borderRadius: "50%", background: "#34d399" }} />
              Connected
            </span>
            <button onClick={onDisconnect} style={{ marginLeft: "auto", fontSize: 9, color: "#52525b", background: "none", border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 4, fontFamily: "inherit" }}>
              <Unlink style={{ width: 12, height: 12 }} />Disconnect
            </button>
          </>
        ) : isConfiguring ? (
          <>
            <button
              onClick={onSave}
              disabled={saving}
              style={{ display: "flex", alignItems: "center", gap: 4, padding: "6px 12px", borderRadius: 8, fontSize: 10, fontWeight: 500, color: "#fff", border: "none", cursor: saving ? "not-allowed" : "pointer", background: `linear-gradient(135deg, ${meta.color}cc, ${meta.color}88)`, transition: "all .2s", fontFamily: "inherit", opacity: saving ? 0.7 : 1 }}
              data-testid={`connect-save-${platformId}`}>
              <Link2 style={{ width: 12, height: 12 }} />
              {saving ? "Saving..." : "Save & Connect"}
            </button>
            <button onClick={onCancel} style={{ padding: "6px 8px", borderRadius: 4, fontSize: 10, color: T.zinc, background: "none", border: "none", cursor: "pointer", fontFamily: "inherit" }}>
              Cancel
            </button>
          </>
        ) : (
          <button
            onClick={onConfigure}
            style={{ display: "flex", alignItems: "center", gap: 4, padding: "6px 10px", borderRadius: 8, fontSize: 10, border: "1px solid rgba(255,255,255,0.1)", color: "#a1a1aa", background: "transparent", cursor: "pointer", transition: "all .2s", fontFamily: "inherit" }}
            data-testid={`connect-btn-${platformId}`}>
            <Plus style={{ width: 12, height: 12 }} />Connect
          </button>
        )}
      </div>
    </div>
  );
}
