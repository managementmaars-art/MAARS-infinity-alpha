import { createContext, useContext, useState, useEffect, useCallback } from "react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const defaults = {
  platform_name: "MAARS ∞",
  tagline: "AI-Powered Team Platform",
  logo_url: "",
  favicon_url: "",
  primary_color: "#ef4444",
  accent_color: "#f97316",
  footer_text: "MAARS Global Corporation",
};

const BrandingContext = createContext(defaults);

export const useBranding = () => useContext(BrandingContext);

export const BrandingProvider = ({ children }) => {
  const [branding, setBranding] = useState(defaults);

  const fetchBranding = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/api/branding/public`);
      if (res.ok) {
        const data = await res.json();
        setBranding(prev => ({ ...prev, ...data }));
      }
    } catch {}
  }, []);

  useEffect(() => {
    fetchBranding();
    const interval = setInterval(fetchBranding, 60000);
    return () => clearInterval(interval);
  }, [fetchBranding]);

  // Apply CSS custom properties for dynamic theming
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty("--brand-primary", branding.primary_color);
    root.style.setProperty("--brand-accent", branding.accent_color);

    // Update favicon if set
    if (branding.favicon_url) {
      const url = branding.favicon_url.startsWith("/api")
        ? `${BACKEND_URL}${branding.favicon_url}`
        : branding.favicon_url;
      let link = document.querySelector("link[rel~='icon']");
      if (!link) {
        link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
      }
      link.href = url;
    }

    // Update page title
    if (branding.platform_name) {
      document.title = branding.platform_name;
    }
  }, [branding]);

  return (
    <BrandingContext.Provider value={branding}>
      {children}
    </BrandingContext.Provider>
  );
};
