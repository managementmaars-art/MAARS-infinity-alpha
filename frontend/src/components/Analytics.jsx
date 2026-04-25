/* Analytics loader — respects cookie consent.

   Only loads a tracking script if the user explicitly accepted
   'analytics' in the cookie banner. Supports two providers:
     - Plausible (privacy-friendly, GDPR-safe by default)
     - Google Analytics 4 (only if operator explicitly opts for it)

   Operator config via env (build-time):
     REACT_APP_PLAUSIBLE_DOMAIN=maarscommand.com
     REACT_APP_GA4_ID=G-XXXXXXXXXX

   If neither is set, the component renders nothing — zero network
   traffic, zero privacy exposure. */
import { useEffect } from "react";

const CONSENT_KEY = "maars_cookie_consent_v1";

function analyticsConsented() {
  try {
    const raw = JSON.parse(localStorage.getItem(CONSENT_KEY) || "null");
    return !!raw?.analytics;
  } catch { return false; }
}

const Analytics = () => {
  useEffect(() => {
    if (!analyticsConsented()) return;

    const plausibleDomain = process.env.REACT_APP_PLAUSIBLE_DOMAIN;
    const ga4Id = process.env.REACT_APP_GA4_ID;

    // Plausible — prefer this, it's privacy-friendly
    if (plausibleDomain) {
      const s = document.createElement("script");
      s.defer = true;
      s.dataset.domain = plausibleDomain;
      s.src = "https://plausible.io/js/script.js";
      document.head.appendChild(s);
    }

    // GA4 only if Plausible isn't configured (avoid double-counting)
    if (!plausibleDomain && ga4Id) {
      const s1 = document.createElement("script");
      s1.async = true;
      s1.src = `https://www.googletagmanager.com/gtag/js?id=${ga4Id}`;
      document.head.appendChild(s1);
      const s2 = document.createElement("script");
      s2.textContent = `
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', '${ga4Id}', { anonymize_ip: true });
      `;
      document.head.appendChild(s2);
    }
  }, []);

  return null;
};

export default Analytics;
