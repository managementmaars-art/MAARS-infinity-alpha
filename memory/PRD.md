# Martian AI by MAARS Global Corporation - PRD

## Original Problem Statement
Full-stack AI team platform with 20+ agents, Commander AI with auto-task delegation, multi-language audio, file generation, subscription SaaS with Stripe, custom "Build Your Own" packages, private admin dashboard with cost reference.

## Implemented Features

### Core Platform
- React + FastAPI + MongoDB, JWT + Google OAuth
- 21 AI agents, Chat with 10+ LLMs, File gen (PDF/Excel/Word/CSV/Images/Videos)

### Admin Dashboard (8 tabs)
- **Pricing Manager**: LIVE SYNC calculator for subscription plans (Free/Starter/Pro/Business)
- **Pricing Control Center** (Custom Packages tab):
  - Profit Margin Calculator with LIVE SYNC at top
  - AI Cost per Credit (read-only, from real usage), Target Margin %, BDT Exchange Rate
  - "Apply X% Margin to All Credits" button to auto-set prices
  - Agent & Commander per-unit pricing (USD/BDT)
  - Credit Presets table: Credits | AI Cost | USD Price | BDT Price | Profit | Margin
  - Extra Credit Packs table: same columns
  - All pricing stored in DB, fully admin-configurable
  - Single "Save All Pricing" button

### Commander AI + Group Chat
- Delegation renders as individual agent chat bubbles with avatars, roles, priority badges

### Subscriptions & Billing
- 4 plans + "Build Your Own" + Extra Credit Packs
- Stripe checkout, multi-currency (USD/BDT)
- Brand Footer on ALL pages

## Backlog
- P1: E2E subscription/credit testing
- P1: Commander AI as purchasable add-on for Build Your Own
- P2: Backend refactoring (break server.py into modules)
- P2: Custom domain UI

## Credentials
- Admin: management.maars@marsgc.net / MaarsAdmin2024!
