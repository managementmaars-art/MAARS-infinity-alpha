# Changelog

All notable changes to the Ecommerce SEO Audit Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-01-31

### Added
- **Limitations & Data Requirements section** - New upfront section clearly explaining what the skill can and cannot do without external data
- **Data requirements for each audit type** - Each audit type now specifies exactly what data is needed from the user
- **Crawl data guidance** - Clear instructions on when and how to provide crawl exports from Screaming Frog/Sitebulb
- **H1 verification protocol** - Detailed bash commands and verification process to ensure accurate heading analysis
- **Honest limitations messaging** - Warnings (⚠️) throughout indicating when crawl data or external tools are required

### Changed
- **Internal Linking Analysis** - Completely rewritten to distinguish between what can be done manually vs. what requires crawl data
- **Site Architecture Assessment** - Now sample-based, clearly stating it checks homepage and sample pages rather than entire site
- **Technical Audit section** - Updated with "What I'll do" and "What I'll need from you" sections for transparency
- **STEP 1 audit selection** - Each audit type now lists specific data requirements and expectations
- **Best Practices** - Added new practice: "Be Honest About Limitations"

### Removed
- Unrealistic promises about automatic site-wide crawling
- Claims about counting internal links across entire site without crawl data
- Assumptions about orphan page detection without proper tooling
- Any recommendations that cannot be verified with available tools

### Fixed
- Misleading claims about internal link analysis capabilities
- Overpromises regarding comprehensive audits without user-provided data
- Lack of clarity about when external crawling tools are needed

## [2.0.0] - 2026-01-31

### Added
- Content strategy and cannibalization analysis (TOFU/MOFU/BOFU framework)
- Internal linking structure analysis with hub-and-spoke model
- Structured output with audit report generation
- Competitor-based benchmarking for content length recommendations

### Changed
- Enhanced audit skill with content funnel analysis
- Improved keyword cannibalization detection
- Better internal linking recommendations

## [1.0.0] - Initial Release

### Added
- 7 specialized audit types (Technical, Product, Collection, Logs, Competitor, Keyword, Full)
- WebFetch and WebSearch integration for competitor analysis
- Ecommerce-specific SEO issue detection
- Schema markup validation
- Log file analysis capabilities
