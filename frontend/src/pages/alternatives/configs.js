/* Competitor comparison configs for the generic AlternativePage.
   Keep claims accurate — only list features MAARS genuinely ships. */

export const JASPER = {
  competitorName: "Jasper AI",
  meta: {
    title: "Jasper AI Alternative — MAARS Command (2026)",
    description: "Looking for a Jasper AI alternative? MAARS Command gives you 458+ specialized agents, outbound campaigns, lead research, and free-tier image generation — at a fraction of the cost. Try free.",
    keyword: "jasper ai alternative",
  },
  hero: {
    headline: "The Jasper alternative that actually does the outreach, not just the copy.",
    sub: "Jasper writes marketing content. MAARS writes it AND sends it: finds leads, drafts personalized emails, schedules sends, posts to LinkedIn, generates images — in one place, under one subscription.",
  },
  theyAre: {
    headline: "Jasper = AI copy generator",
    body: "Jasper is strong at writing blog posts, ads, and social captions. You still need separate tools for lead research, email sending, social scheduling, image generation, and CRM — each with its own subscription and learning curve.",
  },
  weAre: {
    headline: "MAARS = AI workforce + execution",
    body: "MAARS is a complete AI workforce. 458+ specialist agents write the copy, generate the images, find the leads, send the emails, post to social, and track the outcomes — all through one platform, one bill, one dashboard.",
  },
  comparison: [
    ["AI copy generation",               true, true,  false],
    ["458+ specialized agents",          false, true,  true],
    ["Built-in lead research",           false, true,  true],
    ["Outbound email campaigns",         false, true,  true],
    ["LinkedIn posting + scheduling",    false, true,  true],
    ["Image generation included",        "Add-on", true, true],
    ["Video generation",                 false, true,  true],
    ["Cold-call automation",             false, true,  true],
    ["Workflow / automation builder",    false, true,  true],
    ["Universal LLM gateway (33+ providers)", false, true, true],
    ["Starts at",                        "$49/mo", "$19/mo", true],
    ["Annual discount",                  "18%",   "20% + bonus credits", true],
  ],
  whySwitch: [
    { title: "One tool, not six", body: "Stop paying for Jasper + Copy.ai + Apollo + SendGrid + Buffer + Midjourney. MAARS bundles the whole stack." },
    { title: "Writes AND sends", body: "Jasper writes the email draft. MAARS writes the draft, personalizes per lead, schedules across days, and handles the unsubscribe headers." },
    { title: "Under 1/2 the price", body: "Starter at $19/mo vs Jasper's $49/mo Creator — and MAARS includes capabilities Jasper charges extra for." },
    { title: "Zero vendor lock-in", body: "Export your data as JSON anytime (GDPR Art. 15). We don't hold your content hostage." },
    { title: "Free-tier friendly", body: "Actually a free plan — no credit card, no trial countdown. See if the agents deliver before you commit." },
  ],
  faq: [
    { q: "Is MAARS really cheaper than Jasper?", a: "Yes at every tier. Starter ($19) vs Jasper Creator ($49); Pro ($79) vs Jasper Pro ($69) but MAARS Pro includes features Jasper reserves for $125+ Teams." },
    { q: "Can I import my Jasper content?", a: "Yes — use the prompt library to save your Jasper templates, or upload completed docs directly. We don't delete anything you bring in." },
    { q: "Does MAARS have brand voice like Jasper?", a: "Agents use per-workspace style blueprints — upload samples, MAARS learns the voice. Same capability as Jasper's brand voice feature." },
    { q: "What about SEO mode?", a: "MAARS ships a dedicated SEO agent + content briefing. For multi-page SEO campaigns the campaign orchestrator schedules over weeks, not one-at-a-time." },
  ],
  cta: { primary: "Try MAARS free →", secondary: "See pricing" },
};

export const COPY_AI = {
  competitorName: "Copy.ai",
  meta: {
    title: "Copy.ai Alternative — MAARS Command (2026)",
    description: "A Copy.ai alternative that actually executes: 458+ agents, outbound campaigns, lead research, image + video generation — one subscription. Free tier included.",
    keyword: "copy.ai alternative",
  },
  hero: {
    headline: "Everything Copy.ai does. Plus the outreach, leads, and media Copy.ai asks you to add other tools for.",
    sub: "Copy.ai's workflows are powerful inside Copy.ai. MAARS's workflows reach the outside world — finding leads, sending emails, posting to social, running full outbound campaigns.",
  },
  theyAre: {
    headline: "Copy.ai = marketing workflow builder",
    body: "Copy.ai is best for marketers running repeatable content workflows — product-launch copy, SEO briefs, ad variations. It generates; you paste into other tools to ship.",
  },
  weAre: {
    headline: "MAARS = end-to-end execution",
    body: "MAARS's workflow builder is a true DAG — lead search → email draft → send → wait 3 days → follow up — all in one place, executing 24/7 via background scheduler.",
  },
  comparison: [
    ["Marketing copy workflows",          true, true,  false],
    ["Team seats on starter plan",        "No",  "Yes (3)", true],
    ["Lead finding built-in",             false, true,  true],
    ["Outbound email sending (compliant)", false, true, true],
    ["LinkedIn post scheduling",           false, true,  true],
    ["Image + video generation",           "Add-on / separate", true, true],
    ["24/7 scheduler for automations",     "Limited", true, true],
    ["Universal LLM gateway",              false, true,  true],
    ["Free tier credits",                  "Limited", "Generous", true],
    ["Starts at",                          "$49/mo", "$19/mo", true],
  ],
  whySwitch: [
    { title: "One subscription replaces 4-5", body: "Copy.ai + Apollo + SendGrid + Buffer + Midjourney = $200+/mo. MAARS starter = $19." },
    { title: "Workflows that reach real people", body: "Copy.ai workflows stop at the clipboard. MAARS workflows send emails, post content, and message prospects." },
    { title: "Team access starts at $19", body: "Copy.ai Team plan is $186/mo for 5 seats. MAARS Starter has 3 seats on day one." },
    { title: "Switch without losing your brand voice", body: "Upload a Copy.ai export, set your style blueprint once — every agent matches." },
    { title: "Free forever, not free 7 days", body: "MAARS free plan renews monthly. No trial countdown." },
  ],
  faq: [
    { q: "Is MAARS like Copy.ai's Workflows feature?", a: "It's broader. Copy.ai workflows chain content steps. MAARS workflows chain any action — find leads, enrich, draft, send, post, wait, branch on conditions." },
    { q: "Can I use my own OpenAI key?", a: "Yes — bring-your-own-key is supported for all paid plans. MAARS still routes to free tiers when possible." },
    { q: "Does MAARS have unlimited words?", a: "MAARS uses credits, not words. 500 credits ≈ 500K tokens of LLM work, which is roughly 350K words of generated content per month on Starter." },
  ],
  cta: { primary: "Try MAARS free →", secondary: "See pricing" },
};

export const CURSOR = {
  competitorName: "Cursor",
  meta: {
    title: "Cursor Alternative — MAARS Command (2026)",
    description: "MAARS goes beyond code — 458+ agents across every business function: marketing, sales, finance, ops, research. Cursor writes code; MAARS runs businesses.",
    keyword: "cursor alternative",
  },
  hero: {
    headline: "Cursor for code. MAARS for everything else your business needs AI to do.",
    sub: "Cursor is the best AI pair-programmer. MAARS is the AI workforce for the other 80% of your business — marketing, sales, content, ops, finance, customer support.",
  },
  theyAre: {
    headline: "Cursor = AI-native IDE",
    body: "Cursor is a fork of VS Code with deep AI integration. It shines at autocompletion, refactoring, and codebase-wide changes. It's a developer tool for a developer's workflow.",
  },
  weAre: {
    headline: "MAARS = AI workforce OS",
    body: "MAARS isn't an IDE. It's a platform of 458+ specialized agents that run the parts of your business that aren't code — marketing campaigns, sales outreach, content production, customer replies, financial reports.",
  },
  comparison: [
    ["AI code completion",                true, "Via agent_appdev", false],
    ["Marketing automation agents",       false, true, true],
    ["Sales + outbound campaigns",        false, true, true],
    ["Content generation (blog, social, email)", false, true, true],
    ["Image + video generation",          false, true, true],
    ["Customer support agents",           false, true, true],
    ["Financial analysis agents",         false, true, true],
    ["CRM + tool integrations",           "Limited", "HubSpot, Salesforce, Shopify+", true],
    ["Works in browser, not only IDE",    false, true, true],
    ["Starts at",                          "$20/mo", "$19/mo", true],
  ],
  whySwitch: [
    { title: "Cursor is not a MAARS replacement", body: "They're complementary. Devs keep Cursor. The rest of the company (marketing, sales, ops) runs on MAARS." },
    { title: "458+ domain experts", body: "Cursor's one generalist agent is great at code. MAARS has 458 agents, each specialized." },
    { title: "Business tools, not dev tools", body: "Integrations with HubSpot, Salesforce, Shopify, Google Workspace, LinkedIn — where business actually happens." },
    { title: "Non-technical team members can use it", body: "Cursor assumes you're a developer. MAARS assumes you're trying to grow a business." },
  ],
  faq: [
    { q: "Does MAARS write code?", a: "Yes — the appdev agent handles code generation, review, and GitHub actions. But MAARS's strength is the other 458 agents handling marketing, sales, ops, and more." },
    { q: "Should I cancel Cursor to use MAARS?", a: "No — keep both. Cursor for your codebase IDE, MAARS for everything your business does outside the IDE." },
    { q: "Can MAARS connect to my codebase?", a: "MAARS can read public GitHub repos via the github_action tool. For IDE-level code flow, Cursor is still the right choice." },
  ],
  cta: { primary: "Run your business on MAARS →", secondary: "See pricing" },
};

export const LOVABLE = {
  competitorName: "Lovable",
  meta: {
    title: "Lovable Alternative — MAARS Command (2026)",
    description: "Lovable builds apps. MAARS runs the business around the app: marketing, sales, support, ops — 458+ AI agents for everything your startup needs.",
    keyword: "lovable alternative",
  },
  hero: {
    headline: "Lovable builds your app. MAARS runs everything around it.",
    sub: "Lovable spins up React apps in minutes. MAARS is what you launch once the app is live — marketing, sales outreach, customer support, content, automations.",
  },
  theyAre: {
    headline: "Lovable = AI app builder",
    body: "Lovable is a text-to-app tool. Describe what you want, get a deployed full-stack application. Perfect for prototyping and shipping fast.",
  },
  weAre: {
    headline: "MAARS = AI-powered operations",
    body: "MAARS doesn't build apps — it runs the go-to-market for whatever you built. Find leads for your new app, email them, post launches to LinkedIn, generate marketing images, handle inbound support.",
  },
  comparison: [
    ["Text-to-app generation",             true, "No", true],
    ["Marketing agent workforce",          false, true, true],
    ["Outbound email + calls",             false, true, true],
    ["Lead research database",             false, true, true],
    ["Image + video for marketing",        false, true, true],
    ["Customer support automation",        false, true, true],
    ["Workflow automation (Zapier-like)",  false, true, true],
    ["Free tier",                          "Limited", "Generous", true],
    ["Starts at",                          "$25/mo", "$19/mo", true],
  ],
  whySwitch: [
    { title: "Build once. Run forever.", body: "Lovable builds the app in a weekend. MAARS keeps it alive — marketing, sales, support, ops." },
    { title: "458+ specialists vs. 1 builder", body: "Lovable's AI builds. MAARS's agents each do ONE thing well — sales, copy, finance, design, code review." },
    { title: "Your app needs customers", body: "A deployed app doesn't grow itself. MAARS's campaign orchestrator finds and messages your first 100 users." },
    { title: "Stay in control of data", body: "Full GDPR data export + delete. Your customers + their data stay yours." },
  ],
  faq: [
    { q: "Can MAARS build me an app like Lovable?", a: "No — MAARS is not a code generator. The appdev agent writes code snippets, but for full app scaffolding use Lovable or v0.dev, then plug MAARS in for go-to-market." },
    { q: "What if I built my app with Lovable?", a: "Perfect combo. Lovable ships the product; MAARS handles everything post-launch (landing page copy, cold email, SEO, support)." },
    { q: "Do MAARS agents talk to my app's users?", a: "Yes — via the customer-service agent, email campaigns, and webhooks that your app triggers when events happen." },
  ],
  cta: { primary: "Launch your startup with MAARS →", secondary: "See pricing" },
};

export const ALL_ALTERNATIVES = [
  { slug: "jasper", config: JASPER, tagline: "For marketers tired of paying $49+/mo for just copy." },
  { slug: "copy-ai", config: COPY_AI, tagline: "Workflows that reach real people, not just the clipboard." },
  { slug: "cursor", config: CURSOR, tagline: "Your IDE is covered. Let MAARS run the other 80%." },
  { slug: "lovable", config: LOVABLE, tagline: "Build the app in a weekend. Run it with MAARS." },
];
