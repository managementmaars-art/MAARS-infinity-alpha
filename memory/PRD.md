# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI with auto-task delegation, multi-language audio, file generation, subscription SaaS with Stripe, custom "Build Your Own" packages, private admin dashboard with cost reference.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents, Chat with 10+ LLMs, File gen (PDF/Excel/Word/CSV/Images/Videos)

### Admin Dashboard (8 tabs)
- **Pricing Manager**: LIVE SYNC calculator for subscription plans with live BDT rate
- **Pricing Control Center** (Custom Packages tab):
  - Profit Margin Calculator with LIVE SYNC
  - AI Cost per Credit from real usage data (read-only)
  - Target Profit Margin % with "Apply to All Credits" button
  - **Live BDT Exchange Rate** fetched from HexaRate API (refreshes hourly)
  - "Refresh Live" button for manual rate refresh
  - All BDT prices auto-calculate from USD × live rate
  - BDT fields are read-only with "auto" labels
  - Full cost/profit/margin visibility per row
  - `/api/exchange-rate` - public endpoint for live USD/BDT rate

### Commander AI + Group Chat
- Delegation renders as individual agent chat bubbles with avatars, roles, priority badges

### Subscriptions & Billing
- 4 plans + "Build Your Own" + Extra Credit Packs (all admin-configurable)
- Stripe checkout, multi-currency (USD/BDT)

### Brand Footer
- "Martian AI by MAARS Global Corporation © 2026" on ALL pages

## Key API Endpoints
- Auth: /api/auth/register, /api/auth/login, /api/auth/me
- Chat: /api/chats, /api/chats/{id}/messages
- Admin: /api/admin/stats, /api/admin/pricing, /api/admin/avg-cost
- Admin Pricing: /api/admin/custom-package, /api/admin/credit-packages
- Public: /api/exchange-rate (live USD/BDT from HexaRate API)

## Backlog
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on for Build Your Own
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
