# Core Web Vitals Reference

## Overview

Core Web Vitals (CWV) are Google's standardized metrics for measuring real-world user experience. They directly impact SEO rankings and represent the three pillars of web UX: loading, interactivity, and visual stability.

## The Three Core Web Vitals

### LCP (Largest Contentful Paint)

**What it measures:** Time until the largest content element is rendered.

| Rating | Threshold |
|--------|-----------|
| Good | ≤ 2.5s |
| Needs Improvement | 2.5s - 4.0s |
| Poor | > 4.0s |

**LCP candidates:** Images, video poster images, background images (via `url()`), block-level text nodes.

**Common causes of poor LCP:**
- Slow server response (TTFB > 800ms)
- Render-blocking resources (CSS, sync JS)
- Slow resource load (large images, fonts)
- Client-side rendering delays

**Root cause identification:**
```
LCP = TTFB + Resource Load Delay + Resource Load Time + Element Render Delay
```
- If TTFB is high → Server/network issue
- If Resource Load Delay is high → Render-blocking resources
- If Resource Load Time is high → Large/slow resources
- If Element Render Delay is high → JS blocking or hydration

### CLS (Cumulative Layout Shift)

**What it measures:** Visual stability - how much content shifts unexpectedly.

| Rating | Threshold |
|--------|-----------|
| Good | ≤ 0.1 |
| Needs Improvement | 0.1 - 0.25 |
| Poor | > 0.25 |

**How CLS is calculated:**
```
CLS = Impact Fraction × Distance Fraction
```
- Impact Fraction: % of viewport affected
- Distance Fraction: Distance moved as % of viewport

**Session window:** CLS uses a "session window" approach - shifts within 1s and max 5s session are grouped. Final CLS is the largest session value.

**Common causes of poor CLS:**
- Images without dimensions (`width`/`height`)
- Ads, embeds, iframes without reserved space
- Web fonts causing FOIT/FOUT
- Dynamically injected content above fold
- Late-loading components (hydration)

**Debugging CLS:**
- Check `PerformanceObserver` layout-shift entries
- Look at `sources` array for shifted elements
- Common culprits: hero images, nav bars, cookie banners

### INP (Interaction to Next Paint)

**What it measures:** Responsiveness - delay between user interaction and visual feedback.

| Rating | Threshold |
|--------|-----------|
| Good | ≤ 200ms |
| Needs Improvement | 200ms - 500ms |
| Poor | > 500ms |

**INP calculation:**
- Measures all interactions (clicks, taps, key presses)
- Takes the p98 (98th percentile) of all interactions
- Includes: input delay + processing time + presentation delay

**Common causes of poor INP:**
- Long JavaScript tasks (> 50ms)
- Heavy event handlers
- Forced synchronous layouts
- Main thread contention during hydration

**Breakdown:**
```
INP = Input Delay + Processing Time + Presentation Delay
```
- Input Delay: Main thread busy, can't start handler
- Processing Time: Event handler execution
- Presentation Delay: Browser rendering after handler

## Secondary Metrics

### FCP (First Contentful Paint)
Time until first content (text, image) renders. Good: ≤ 1.8s

### TTFB (Time to First Byte)
Server response time. Good: ≤ 800ms. High TTFB cascades to all other metrics.

### TBT (Total Blocking Time)
Sum of blocking portions of long tasks (> 50ms) between FCP and TTI. Lab proxy for INP.

### Speed Index
How quickly content is visually populated. Lower is better.

## Lighthouse vs Field Data

| Aspect | Lighthouse (Lab) | Field (CrUX) |
|--------|------------------|--------------|
| Environment | Simulated | Real users |
| Network | Throttled | Varies |
| Device | Emulated | Real devices |
| INP | Uses TBT proxy | Real INP |
| Best for | Debugging | Business decisions |

**Key insight:** Lighthouse scores can differ significantly from field data. A "perfect" Lighthouse score doesn't guarantee good real-world performance.

## Interpreting Scores

### Lighthouse Performance Score
Weighted average of metrics:
- FCP: 10%
- Speed Index: 10%
- LCP: 25%
- TBT: 30%
- CLS: 25%

### What scores mean
- 90-100: Good performance, minor optimizations possible
- 50-89: Moderate issues, prioritize worst metrics
- 0-49: Significant problems, focus on fundamentals

### Reading the Lighthouse report
1. **Metrics section:** Raw values with filmstrip
2. **Opportunities:** Estimated savings (prioritize by impact)
3. **Diagnostics:** Explanations without time estimates
4. **Passed Audits:** Already optimized areas

## Quick Reference: Metric to Action

| Symptom | Likely Metric | First Check |
|---------|---------------|-------------|
| Page feels slow to load | LCP | TTFB, image sizes, render-blocking resources |
| Content jumps around | CLS | Images without dimensions, late-injected content |
| Clicks feel laggy | INP | Long tasks, heavy handlers, hydration timing |
| Blank screen too long | FCP | TTFB, render-blocking CSS/JS |
