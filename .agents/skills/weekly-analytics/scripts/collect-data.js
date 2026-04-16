#!/usr/bin/env node
/**
 * Weekly Analytics — Data Collection Script
 * 
 * Pulls data from GA4, GSC, and Clarity for the weekly report.
 * 
 * Usage: node collect-data.js [--days=7] [--end=YYYY-MM-DD]
 * 
 * Required environment variables:
 *   GOOGLE_OAUTH_CLIENT_ID
 *   GOOGLE_OAUTH_CLIENT_SECRET
 *   GOOGLE_OAUTH_REFRESH_TOKEN
 *   GA4_PROPERTY_ID
 *   GSC_CREDENTIALS_PATH (path to service account JSON)
 *   GSC_SITE_URL (e.g., https://example.com/)
 *   CLARITY_API_TOKEN
 * 
 * Outputs JSON to stdout with all data needed for the report.
 */

const { google } = require('googleapis');
const https = require('https');

// Config from environment
const GA4_PROPERTY = `properties/${process.env.GA4_PROPERTY_ID}`;
const GSC_SITE = process.env.GSC_SITE_URL;
const GSC_CREDENTIALS = process.env.GSC_CREDENTIALS_PATH;

// Parse args
const args = process.argv.slice(2).reduce((acc, arg) => {
  const [key, val] = arg.replace('--', '').split('=');
  acc[key] = val;
  return acc;
}, {});

const days = parseInt(args.days) || 7;
const endDate = args.end ? new Date(args.end) : new Date(Date.now() - 86400000); // yesterday
const startDate = new Date(endDate.getTime() - (days - 1) * 86400000);

const formatDate = (d) => d.toISOString().split('T')[0];

async function getGA4Data() {
  const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_OAUTH_CLIENT_ID,
    process.env.GOOGLE_OAUTH_CLIENT_SECRET
  );
  oauth2Client.setCredentials({
    refresh_token: process.env.GOOGLE_OAUTH_REFRESH_TOKEN
  });

  const analyticsdata = google.analyticsdata({ version: 'v1beta', auth: oauth2Client });

  // Summary metrics
  const summary = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      metrics: [
        { name: 'activeUsers' },
        { name: 'sessions' },
        { name: 'screenPageViews' },
        { name: 'engagedSessions' },
        { name: 'engagementRate' },
        { name: 'averageSessionDuration' },
        { name: 'newUsers' }
      ]
    }
  });

  // Daily breakdown
  const daily = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      dimensions: [{ name: 'date' }],
      metrics: [
        { name: 'activeUsers' },
        { name: 'sessions' },
        { name: 'screenPageViews' },
        { name: 'bounceRate' }
      ],
      orderBys: [{ dimension: { dimensionName: 'date' } }]
    }
  });

  // Top pages
  const pages = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      dimensions: [{ name: 'pagePath' }],
      metrics: [
        { name: 'sessions' },
        { name: 'activeUsers' },
        { name: 'screenPageViews' }
      ],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
      limit: 20
    }
  });

  // Traffic sources
  const sources = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      dimensions: [{ name: 'sessionSource' }],
      metrics: [
        { name: 'sessions' },
        { name: 'activeUsers' },
        { name: 'screenPageViews' }
      ],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }],
      limit: 15
    }
  });

  // Channels
  const channels = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      dimensions: [{ name: 'sessionDefaultChannelGroup' }],
      metrics: [
        { name: 'sessions' },
        { name: 'activeUsers' }
      ],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }]
    }
  });

  // Countries
  const countries = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      dimensions: [{ name: 'country' }],
      metrics: [
        { name: 'activeUsers' },
        { name: 'sessions' }
      ],
      orderBys: [{ metric: { metricName: 'activeUsers' }, desc: true }],
      limit: 10
    }
  });

  // Devices
  const devices = await analyticsdata.properties.runReport({
    property: GA4_PROPERTY,
    requestBody: {
      dateRanges: [{ startDate: formatDate(startDate), endDate: formatDate(endDate) }],
      dimensions: [{ name: 'deviceCategory' }],
      metrics: [
        { name: 'activeUsers' },
        { name: 'sessions' }
      ],
      orderBys: [{ metric: { metricName: 'sessions' }, desc: true }]
    }
  });

  return {
    summary: summary.data,
    daily: daily.data,
    pages: pages.data,
    sources: sources.data,
    channels: channels.data,
    countries: countries.data,
    devices: devices.data
  };
}

async function getGSCData() {
  if (!GSC_CREDENTIALS || !GSC_SITE) {
    return { error: 'GSC_CREDENTIALS_PATH or GSC_SITE_URL not set' };
  }

  const auth = new google.auth.GoogleAuth({
    keyFile: GSC_CREDENTIALS,
    scopes: ['https://www.googleapis.com/auth/webmasters.readonly']
  });
  const client = await auth.getClient();
  const webmasters = google.webmasters({ version: 'v3', auth: client });

  // Search queries
  const queries = await webmasters.searchanalytics.query({
    siteUrl: GSC_SITE,
    requestBody: {
      startDate: formatDate(startDate),
      endDate: formatDate(endDate),
      dimensions: ['query'],
      rowLimit: 50
    }
  });

  // Pages
  const pages = await webmasters.searchanalytics.query({
    siteUrl: GSC_SITE,
    requestBody: {
      startDate: formatDate(startDate),
      endDate: formatDate(endDate),
      dimensions: ['page'],
      rowLimit: 30
    }
  });

  return {
    queries: queries.data.rows || [],
    pages: pages.data.rows || []
  };
}

async function getClarityData() {
  return new Promise((resolve) => {
    const token = process.env.CLARITY_API_TOKEN;
    if (!token) {
      resolve({ error: 'No CLARITY_API_TOKEN' });
      return;
    }

    const url = `https://www.clarity.ms/export-data/api/v1/project-live-insights?numOfDays=3&dimension1=Browser&dimension2=Device`;
    
    const req = https.get(url, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          resolve({ error: `Parse error: ${e.message}`, raw: data.slice(0, 500) });
        }
      });
    });
    req.on('error', (e) => resolve({ error: e.message }));
    req.setTimeout(10000, () => {
      req.destroy();
      resolve({ error: 'Timeout' });
    });
  });
}

async function main() {
  console.error(`Collecting data for ${formatDate(startDate)} to ${formatDate(endDate)}...`);

  const [ga4, gsc, clarity] = await Promise.all([
    getGA4Data().catch(e => ({ error: e.message })),
    getGSCData().catch(e => ({ error: e.message })),
    getClarityData()
  ]);

  const output = {
    window: {
      start: formatDate(startDate),
      end: formatDate(endDate),
      days
    },
    ga4,
    gsc,
    clarity,
    collectedAt: new Date().toISOString()
  };

  console.log(JSON.stringify(output, null, 2));
}

main().catch(e => {
  console.error('Fatal:', e);
  process.exit(1);
});
