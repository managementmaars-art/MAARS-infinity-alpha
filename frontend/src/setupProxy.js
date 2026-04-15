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

const target =
  process.env.REACT_APP_BACKEND_URL?.trim() || "http://localhost:8000";

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
