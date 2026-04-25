// MAARS dev-server proxy.
//
// Forwards /api/* (both HTTP and WebSocket) to the backend so the browser
// sees every request as same-origin (http://localhost:3000). This is the
// canonical React dev-server trick — eliminates CORS preflight rounds and
// sidesteps the "Failed to fetch" problem that otherwise hits cross-origin
// POSTs in some Chrome builds even when CORS itself is configured correctly.
//
// Target backend is taken from REACT_APP_BACKEND_URL (same var the production
// bundle uses) with a localhost fallback.

const { createProxyMiddleware } = require("http-proxy-middleware");

// Force IPv4: Node 18+ resolves `localhost` to ::1 (IPv6) first on Windows,
// but uvicorn binds 127.0.0.1 only. Use the literal IP so the proxy always
// hits the live backend instead of a stale/absent ::1 listener (which
// surfaces as a spurious 404 for any route added after the last dev-server
// startup that cached the old resolution).
const target =
  process.env.REACT_APP_BACKEND_URL?.trim() || "http://127.0.0.1:8001";

module.exports = function (app) {
  // REST / HTTP endpoints
  app.use(
    "/api",
    createProxyMiddleware({
      target,
      changeOrigin: true,
      ws: true,            // upgrade WebSocket handshakes on /api/**/ws
      logLevel: "warn",
    })
  );
};
