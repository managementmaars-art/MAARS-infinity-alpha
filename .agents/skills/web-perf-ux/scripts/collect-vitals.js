/**
 * Web Vitals Collection Script
 *
 * Inject this script via Playwright to collect real Core Web Vitals.
 * Uses the web-vitals library pattern for accurate measurement.
 *
 * Usage in Playwright:
 *   await page.evaluate(collectVitalsScript);
 *   // ... interact with page ...
 *   const vitals = await page.evaluate(() => window.__WEB_VITALS__);
 */

(function collectWebVitals() {
  // Initialize storage
  window.__WEB_VITALS__ = {
    LCP: null,
    CLS: null,
    INP: null,
    FCP: null,
    TTFB: null,
    FID: null, // Legacy, but useful for older browsers
    layoutShifts: [],
    longTasks: [],
    resourceTimings: [],
    collected: false,
    errors: []
  };

  const vitals = window.__WEB_VITALS__;

  // Helper: safe metric recording
  function recordMetric(name, value, entries = []) {
    vitals[name] = {
      value: value,
      rating: getRating(name, value),
      entries: entries.map(e => ({
        name: e.name,
        startTime: e.startTime,
        duration: e.duration
      }))
    };
  }

  // Rating thresholds per Core Web Vitals
  function getRating(metric, value) {
    const thresholds = {
      LCP: [2500, 4000],
      CLS: [0.1, 0.25],
      INP: [200, 500],
      FCP: [1800, 3000],
      TTFB: [800, 1800],
      FID: [100, 300]
    };

    const [good, poor] = thresholds[metric] || [Infinity, Infinity];
    if (value <= good) return 'good';
    if (value <= poor) return 'needs-improvement';
    return 'poor';
  }

  // Largest Contentful Paint
  try {
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      if (lastEntry) {
        recordMetric('LCP', lastEntry.startTime, entries);
      }
    });
    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (e) {
    vitals.errors.push({ metric: 'LCP', error: e.message });
  }

  // Cumulative Layout Shift
  try {
    let clsValue = 0;
    let clsEntries = [];
    let sessionValue = 0;
    let sessionEntries = [];
    let lastSessionEnd = 0;

    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // Only count shifts without recent input
        if (!entry.hadRecentInput) {
          const gap = entry.startTime - lastSessionEnd;

          // New session if gap > 1s or session > 5s
          if (gap > 1000 || entry.startTime - sessionEntries[0]?.startTime > 5000) {
            if (sessionValue > clsValue) {
              clsValue = sessionValue;
              clsEntries = [...sessionEntries];
            }
            sessionValue = 0;
            sessionEntries = [];
          }

          sessionValue += entry.value;
          sessionEntries.push(entry);
          lastSessionEnd = entry.startTime + entry.duration;

          // Track individual shifts for debugging
          vitals.layoutShifts.push({
            value: entry.value,
            startTime: entry.startTime,
            sources: entry.sources?.map(s => ({
              node: s.node?.nodeName,
              previousRect: s.previousRect,
              currentRect: s.currentRect
            }))
          });
        }
      }

      // Update CLS with max session
      const finalCLS = Math.max(clsValue, sessionValue);
      recordMetric('CLS', finalCLS, clsEntries.length ? clsEntries : sessionEntries);
    });
    clsObserver.observe({ type: 'layout-shift', buffered: true });
  } catch (e) {
    vitals.errors.push({ metric: 'CLS', error: e.message });
  }

  // Interaction to Next Paint (INP)
  try {
    let maxINP = 0;
    let inpEntries = [];

    const inpObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        // INP considers all interactions, takes p98 of longest
        const duration = entry.duration;
        if (duration > maxINP) {
          maxINP = duration;
          inpEntries = [entry];
        }
      }
      recordMetric('INP', maxINP, inpEntries);
    });
    inpObserver.observe({ type: 'event', buffered: true, durationThreshold: 16 });
  } catch (e) {
    vitals.errors.push({ metric: 'INP', error: e.message });
  }

  // First Input Delay (legacy, fallback)
  try {
    const fidObserver = new PerformanceObserver((list) => {
      const entry = list.getEntries()[0];
      if (entry) {
        recordMetric('FID', entry.processingStart - entry.startTime, [entry]);
      }
    });
    fidObserver.observe({ type: 'first-input', buffered: true });
  } catch (e) {
    vitals.errors.push({ metric: 'FID', error: e.message });
  }

  // First Contentful Paint
  try {
    const fcpObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name === 'first-contentful-paint') {
          recordMetric('FCP', entry.startTime, [entry]);
        }
      }
    });
    fcpObserver.observe({ type: 'paint', buffered: true });
  } catch (e) {
    vitals.errors.push({ metric: 'FCP', error: e.message });
  }

  // Time to First Byte
  try {
    const navEntries = performance.getEntriesByType('navigation');
    if (navEntries.length > 0) {
      const nav = navEntries[0];
      recordMetric('TTFB', nav.responseStart, [nav]);
    }
  } catch (e) {
    vitals.errors.push({ metric: 'TTFB', error: e.message });
  }

  // Long Tasks (for debugging TBT/INP issues)
  try {
    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        vitals.longTasks.push({
          startTime: entry.startTime,
          duration: entry.duration,
          attribution: entry.attribution?.[0]?.name
        });
      }
    });
    longTaskObserver.observe({ type: 'longtask', buffered: true });
  } catch (e) {
    // Long tasks not supported in all browsers
  }

  // Resource Timings (for identifying slow resources)
  try {
    const resources = performance.getEntriesByType('resource');
    vitals.resourceTimings = resources
      .filter(r => r.duration > 100) // Only slow resources
      .map(r => ({
        name: r.name,
        type: r.initiatorType,
        duration: r.duration,
        transferSize: r.transferSize,
        startTime: r.startTime
      }))
      .sort((a, b) => b.duration - a.duration)
      .slice(0, 20); // Top 20 slowest
  } catch (e) {
    vitals.errors.push({ metric: 'resources', error: e.message });
  }

  // Mark as collected after initial load
  window.addEventListener('load', () => {
    setTimeout(() => {
      vitals.collected = true;
    }, 1000); // Wait 1s after load for late metrics
  });

  // Expose helper to get summary
  window.__GET_VITALS_SUMMARY__ = function() {
    return {
      LCP: vitals.LCP?.value,
      CLS: vitals.CLS?.value,
      INP: vitals.INP?.value,
      FCP: vitals.FCP?.value,
      TTFB: vitals.TTFB?.value,
      ratings: {
        LCP: vitals.LCP?.rating,
        CLS: vitals.CLS?.rating,
        INP: vitals.INP?.rating
      },
      layoutShiftCount: vitals.layoutShifts.length,
      longTaskCount: vitals.longTasks.length,
      slowResources: vitals.resourceTimings.length
    };
  };
})();
