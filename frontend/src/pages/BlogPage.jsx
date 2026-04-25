/* Blog list + detail. Hits /api/blog (list) and /api/blog/:slug (post).
   Empty state until first post is published — keeps UX clean. */
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { API } from "../App";

const formatDate = (iso) => {
  try { return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "short", day: "numeric" }); }
  catch { return ""; }
};

const pageStyle = { minHeight: "100vh", background: "#030712", color: "#e5e7eb" };
const container = { maxWidth: 780, margin: "0 auto", padding: "56px 24px" };

const TopNav = () => (
  <nav style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", padding: "14px 24px" }}>
    <div style={{ maxWidth: 1200, margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
      <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
        <img src="/branding/maars-logo.jpeg" alt="" style={{ width: 28, height: 28, borderRadius: 8, objectFit: "cover" }} />
        <span style={{ fontSize: 15, fontWeight: 700, color: "#fff" }}>MAARS Command</span>
      </Link>
      <div style={{ display: "flex", gap: 20, fontSize: 13, color: "#94a3b8" }}>
        <Link to="/pricing" style={{ color: "inherit", textDecoration: "none" }}>Pricing</Link>
        <Link to="/blog" style={{ color: "#fff", textDecoration: "none" }}>Blog</Link>
        <Link to="/changelog" style={{ color: "inherit", textDecoration: "none" }}>Changelog</Link>
        <Link to="/login" style={{ color: "inherit", textDecoration: "none" }}>Login</Link>
      </div>
    </div>
  </nav>
);

export const BlogListPage = () => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    document.title = "Blog — MAARS Command";
    fetch(`${API}/blog?limit=30`)
      .then((r) => (r.ok ? r.json() : { data: [] }))
      .then((d) => { setPosts(d.data || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={pageStyle}>
      <TopNav />
      <div style={container}>
        <p style={{ fontSize: 11, color: "#4fd1c5", fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>
          Blog
        </p>
        <h1 style={{ fontSize: 40, fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif", marginBottom: 14, lineHeight: 1.1 }}>
          Practical AI-workforce playbooks
        </h1>
        <p style={{ fontSize: 16, color: "#94a3b8", lineHeight: 1.6, marginBottom: 32 }}>
          How operators use MAARS agents to ship outbound, content, and automation that would take a full team.
        </p>

        {loading && <p style={{ color: "#64748b", fontSize: 14 }}>Loading…</p>}

        {!loading && posts.length === 0 && (
          <div style={{
            padding: 32, textAlign: "center",
            border: "1px dashed rgba(255,255,255,0.12)", borderRadius: 14,
            color: "#64748b", fontSize: 14,
          }}>
            <p style={{ marginBottom: 8, color: "#94a3b8", fontWeight: 600 }}>No posts yet.</p>
            <p>First article lands this week. Subscribe via the <a href="/api/blog" style={{ color: "#60a5fa" }}>JSON feed</a>.</p>
          </div>
        )}

        {posts.map((p) => (
          <Link
            key={p.slug}
            to={`/blog/${p.slug}`}
            style={{
              display: "block", padding: 24, marginBottom: 16,
              borderRadius: 14, background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.06)",
              textDecoration: "none", color: "inherit",
            }}
          >
            <div style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 8, flexWrap: "wrap" }}>
              {(p.tags || []).slice(0, 2).map((t) => (
                <span key={t} style={{
                  fontSize: 10, padding: "3px 10px", borderRadius: 999,
                  background: "rgba(79,209,197,0.1)", color: "#4fd1c5",
                  fontWeight: 600, letterSpacing: "0.05em", textTransform: "uppercase",
                }}>{t}</span>
              ))}
              <span style={{ color: "#64748b", fontSize: 12 }}>{formatDate(p.published_at)}</span>
              {p.reading_minutes && (
                <span style={{ color: "#64748b", fontSize: 12 }}>· {p.reading_minutes} min read</span>
              )}
            </div>
            <h2 style={{ fontSize: 20, fontWeight: 700, color: "#fff", marginBottom: 6, fontFamily: "Outfit, sans-serif" }}>
              {p.title}
            </h2>
            {p.summary && <p style={{ color: "#94a3b8", fontSize: 14, lineHeight: 1.55 }}>{p.summary}</p>}
          </Link>
        ))}
      </div>
    </div>
  );
};

export const BlogPostPage = () => {
  const { slug } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    fetch(`${API}/blog/${slug}`)
      .then((r) => { if (!r.ok) throw new Error("not found"); return r.json(); })
      .then((p) => {
        setPost(p); setLoading(false);
        document.title = `${p.title} — MAARS Blog`;
      })
      .catch(() => { setNotFound(true); setLoading(false); });
  }, [slug]);

  return (
    <div style={pageStyle}>
      <TopNav />
      <div style={container}>
        <Link to="/blog" style={{ color: "#60a5fa", fontSize: 13, textDecoration: "none" }}>← Back to blog</Link>
        {loading && <p style={{ color: "#64748b", fontSize: 14, marginTop: 20 }}>Loading…</p>}
        {notFound && (
          <div style={{ marginTop: 40 }}>
            <h1 style={{ fontSize: 28, color: "#fff", fontFamily: "Outfit, sans-serif" }}>Post not found</h1>
            <p style={{ color: "#94a3b8", marginTop: 10 }}>It may have been moved. <Link to="/blog" style={{ color: "#60a5fa" }}>See all posts</Link>.</p>
          </div>
        )}
        {post && (
          <article style={{ marginTop: 20 }}>
            <p style={{ color: "#4fd1c5", fontSize: 11, fontWeight: 600, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 10 }}>
              {(post.tags || [])[0] || "Article"} · {formatDate(post.published_at)}
            </p>
            <h1 style={{ fontSize: "clamp(1.8rem,4vw,2.6rem)", fontWeight: 800, color: "#fff", fontFamily: "Outfit, sans-serif", lineHeight: 1.15, marginBottom: 24 }}>
              {post.title}
            </h1>
            {post.cover_image && (
              <img src={post.cover_image} alt="" style={{ width: "100%", borderRadius: 12, marginBottom: 32 }} />
            )}
            <div style={{ color: "#cbd5e1", fontSize: 16, lineHeight: 1.75 }}>
              {(post.body || "").split("\n\n").map((p, i) => (
                <p key={i} style={{ marginBottom: 16 }}>{p}</p>
              ))}
            </div>
          </article>
        )}
      </div>
    </div>
  );
};

export default BlogListPage;
