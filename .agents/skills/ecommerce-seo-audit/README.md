# Ecommerce SEO Audit Skill

Professional ecommerce SEO audit skill for AI coding agents, developed by **Auckland Shopify SEO Agency** - Affilino NZ. This skill provides comprehensive SEO audits for online stores, covering product pages, collection pages, technical SEO, log file analysis, and competitor research.

**Works with:** Claude Code, Cursor, Windsurf, Cline, Codex, and other AI coding assistants that support skills.

## Features

- **7 Specialized Audit Types** - Technical, Product, Collection, Log Files, Competitors, Keywords, and Full Comprehensive audits
- **Competitor-Based Benchmarking** - Data-driven content targets based on top 5 competitors' averages (not arbitrary word counts)
- **Ecommerce Issue Detection** - Automatically flags thin category pages, duplicate product descriptions, faceted navigation duplicates, and out-of-stock mishandling
- **Enhanced On-Page Analysis** - Detects duplicate titles, multiple H1 tags, missing product images, and thin content issues
- **Competitor Analysis** - Analyze top 5 ranking sites for any keyword with detailed gap analysis
- **Log File Analysis** - Crawl budget optimization and Googlebot behavior insights
- **Keyword Research & Mapping** - Find opportunities and map keywords to pages
- **Real, Actionable Recommendations** - Prioritized action plans with before/after examples
- **Three-Bucket Framework** - Systematic approach covering Technical, On-Page, and Off-Page SEO

## Installation

Install this skill using the skills manager:

```bash
npx skills add https://github.com/affilino/ecommerce-seo-audit-skill
```

This will launch an interactive installer where you can **select which AI coding agents** to install the skill to:

- ✅ Claude Code
- ✅ Cursor
- ✅ Windsurf
- ✅ Cline
- ✅ Codex
- ✅ Continue
- ✅ And more...

### Start a Session

After installation, start your AI coding agent:

**Claude Code:**
```bash
claude
```

**Cursor / Windsurf / Other agents:**
Open your editor and start a new chat session.

Then invoke the skill in any session:

```bash
/ecommerce-seo-audit
```

## Usage

Invoke the skill in your AI coding agent:

```bash
/ecommerce-seo-audit
```

Or provide arguments directly:

```bash
/ecommerce-seo-audit technical https://yourstore.com
/ecommerce-seo-audit product https://yourstore.com/products/example
/ecommerce-seo-audit competitor https://yourstore.com "running shoes"
```

### Available Audit Types

1. **Quick Technical Audit** - Crawlability, indexability, and schema check
2. **Product Page Audit** - Deep analysis of product page optimization
3. **Collection Page Audit** - Category/collection page SEO review
4. **Log File Analysis** - Crawl budget and Googlebot behavior analysis
5. **Competitor Analysis** - Analyze top 5 ranking competitors
6. **Keyword Research & Mapping** - Find opportunities and map keywords
7. **Full Comprehensive Audit** - Complete audit covering all areas

## Examples

### Quick Technical Audit
```bash
/ecommerce-seo-audit technical https://mystore.com
```

Get a health score with top 3 critical issues and quick wins.

### Product Page Audit
```bash
/ecommerce-seo-audit product https://mystore.com
```

Analyze 5-10 products with detailed optimization recommendations.

### Competitor Analysis
```bash
/ecommerce-seo-audit competitor https://mystore.com "men's running shoes"
```

Analyze top 5 ranking competitors with actionable roadmap to outrank them.

## Output Format

All audits provide:

- **Executive Summary** - SEO health score, critical issues, and quick wins
- **Detailed Findings** - Comprehensive analysis with data and examples
- **Prioritized Action Plan** - CRITICAL, HIGH, MEDIUM, and LOW priority items
- **Expected Impact** - Quantified traffic and revenue projections
- **Benchmarking** - How you compare to competitors

## Requirements

- Any AI coding agent that supports skills (Claude Code, Cursor, Windsurf, Cline, etc.)
- Internet connection for WebSearch and WebFetch tools
- For log file analysis: Access to server logs (Apache, Nginx, or IIS format)

## Who Should Use This

- Ecommerce store owners (Shopify, WooCommerce, Magento, etc.)
- SEO professionals managing ecommerce clients
- Marketing teams optimizing online stores
- Agencies offering SEO services

## Developed By

**Affilino NZ - Auckland Shopify SEO Agency**

This skill was developed by the team at Affilino, a leading Auckland-based Shopify SEO agency specializing in ecommerce SEO audits and optimization for online stores.

### Need Professional Help?

For assistance, customization, or professional SEO services:

- **Website:** [affilino.co.nz](https://affilino.co.nz)
- **Email:** hello@affilino.co.nz
- **Specialization:** Shopify SEO, Ecommerce SEO Audits, Technical SEO

## Contributing

We welcome contributions! If you'd like to improve this skill:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -m 'Add new audit feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## Version History

- **v1.1.0** (2026-01-31) - Enhanced ecommerce audit features
  - Added common ecommerce SEO issues detection (thin pages, duplicate content, faceted navigation)
  - Competitor-based content benchmarking (data-driven word count targets)
  - Enhanced on-page checks (duplicate titles, multiple H1s, missing images)
  - Out-of-stock product handling strategies
  - Faceted navigation duplicate detection
  - Improved product/collection page analysis

- **v1.0.0** (2026-01-30) - Initial release
  - 7 audit types
  - Competitor analysis
  - Log file analysis
  - Keyword research & mapping

## License

Copyright (c) 2026 Affilino NZ. All rights reserved.

## Support

If you encounter any issues or have questions:

1. Check the [GitHub Issues](https://github.com/affilino/ecommerce-seo-audit-skill/issues)
2. Contact us at hello@affilino.co.nz
3. Visit [affilino.co.nz](https://affilino.co.nz) for professional support

---

**Made with focus by Auckland Shopify SEO Agency - Affilino NZ**
