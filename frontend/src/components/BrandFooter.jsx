import { useBranding } from "./BrandingProvider";

export const BrandFooter = ({ className = "" }) => {
  const branding = useBranding();
  const name   = branding.platform_name || "MAARS Command";
  const footer = branding.footer_text   || "MAARS Global Corporation";
  const logoSrc = branding.logo_url
    ? (branding.logo_url.startsWith("/api")
        ? `${process.env.REACT_APP_BACKEND_URL}${branding.logo_url}`
        : branding.logo_url)
    : "/branding/maars-logo.jpeg";

  return (
    <footer
      data-testid="brand-footer"
      className={className}
      style={{
        padding: "14px 20px",
        borderTop: "1px solid rgba(255,255,255,0.06)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        gap: 8,
      }}
    >
      <img
        src={logoSrc}
        alt={name}
        style={{ width: 18, height: 18, borderRadius: 5, objectFit: "cover", opacity: 0.7 }}
        onError={e => { e.target.style.display = "none"; }}
      />
      <span style={{ fontSize: 11, color: "#64748b" }}>
        {name} by {footer} &copy; {new Date().getFullYear()}
      </span>
    </footer>
  );
};
