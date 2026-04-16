# Framer Plugin Marketplace Requirements

Everything needed to ship a plugin to the Framer Marketplace. Non-compliance causes rejection during the ~3-week review process. Source: official Framer documentation (March 2026).

---

## Publishing Workflow

### Pack & Submit

```bash
npm run pack          # Generates plugin.zip at project root
```

1. Go to Marketplace Creator Dashboard → **New Plugin**
2. Upload the generated `plugin.zip`
3. Fill in the listing form and submit

### Updates

Same workflow for updates:
```bash
npm run pack          # Regenerate zip with new code
```
Upload the new zip via the Creator Dashboard. New plugin versions require **expedited review** (faster than initial submission). Most metadata edits (name, description, images) apply instantly without review.

### Review Timeline

| Phase | Duration | What's Evaluated |
|-------|----------|-----------------|
| Initial review | ~7 days | Basic submission requirements met |
| Design review | ~14 days | Design quality, UX, overall polish |

Total: **approximately 3 weeks** from submission to approval.

### Submission Statuses (Creator Dashboard)

- **In Review** — currently being evaluated
- **Needs Changes** — revision requested; detailed feedback provided
- **Published** — live on the Marketplace
- **Rejected** — not accepted

### Contact

For questions about submission or review: **creators@framer.com**

---

## Listing Assets — Exact Specs

| Asset | Required Spec |
|-------|--------------|
| Plugin thumbnail | **1600 × 1200 px**, high-quality, clutter-free |
| Plugin icon | High-quality **SVG**, 30×30 viewBox in `framer.json` |
| Creator avatar | 200 × 200 px |
| Creator banner | 2400 × 400 px |

Thumbnails must be clutter-free and accurately represent the plugin — no misleading visuals.

---

## Mandatory UI Requirements

These are **rejection criteria** if not met:

| Requirement | Detail |
|-------------|--------|
| **Light + dark mode** | Plugin UI must look correct in both. Framer users switch between them. |
| **English only** | All plugin UI text must be in English. |
| **Intuitive, polished UX** | Aligned with Framer's design language. Clean and minimal. |
| **High-quality SVG icon** | Used in `framer.json` and displayed in the Marketplace. |
| **No unrelated ads** | No promotional content for other products inside the plugin. |
| **Accurate description** | Plugin must solve exactly what the listing claims. No feature overpromising. |

---

## Performance Requirements

- Must load **quickly** without blocking Framer content
- Avoid **high memory or CPU consumption** — plugins run inside an iframe alongside a heavy design app
- Must be **extensively tested** to prevent crashes and bugs
- Test across **different project states and browsers**

---

## Security & Legal Requirements

| Rule | Implication |
|------|-------------|
| Use only secure, transparent external services | No hidden/obfuscated endpoints |
| Don't over-rely on third-party services for core features | Core functionality should degrade gracefully if a 3rd-party is down |
| Creators must hold IP rights for all assets | No unlicensed icons, images, or code |
| Properly credit open-source licenses | Follow OSS license terms; display attribution where required |
| No harmful, illegal, or adult content | Instant rejection |
| Write clean, documented, modular code | Code quality is evaluated during design review |

---

## Pricing & Monetisation Rules

- If the plugin has **paid features**, the pricing model must be **clearly explained** in the listing
- All prices must be displayed in **USD only**
- Clearly disclose any **required authentication** (API keys, OAuth, subscription) in the listing description
- Listing fees: **none** — but all plugins go through manual review

---

## Post-Publication Obligations

Rejection can also happen to existing published plugins if these obligations aren't met:

- **Keep the plugin updated** alongside Framer platform changes (SDK updates, API changes)
- **Respond promptly** to user-reported issues
- **Set transparent support expectations** (response time, support channels)
- **Maintain accuracy** — update the listing if features change

---

## Pre-Submission Checklist

Before submitting, verify:

- [ ] Plugin icon and name are finalized and accurate
- [ ] All core functionality is tested thoroughly
- [ ] Tested across different project states and browsers
- [ ] UI looks correct in both **dark and light mode**
- [ ] All UI text is in **English**
- [ ] Thumbnail is 1600 × 1200 px and clutter-free
- [ ] Pricing model is clearly explained in the description (if paid)
- [ ] Authentication requirements are disclosed in the description
- [ ] IP rights held for all assets used
- [ ] No unrelated ads or promotional content
- [ ] All features work exactly as described
- [ ] Include test accounts or license keys with the submission (if needed for review)

---

## Private Plugins

If you need a plugin for **internal team use only** (not listed publicly), contact Framer directly to discuss private plugin options.

---

## Creator Dashboard Analytics

Once published, the dashboard provides:

| Metric | Description |
|--------|-------------|
| **Unique users** | Number of distinct creator accounts using the plugin |
| **Total uses** | Cumulative usage count across all users |

Use these to understand adoption and prioritize improvements.
