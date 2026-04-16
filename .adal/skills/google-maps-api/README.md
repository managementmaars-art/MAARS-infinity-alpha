# Google Maps Platform API Skill for Claude Code

A complete CLI client for **20+ Google Maps Platform REST APIs** — built as a [Claude Code skill](https://docs.anthropic.com/en/docs/claude-code). No external dependencies; uses only Python standard library.

## APIs Covered

| Category | APIs |
|----------|------|
| **Core** | Geocoding, Reverse Geocoding, Directions, Distance Matrix |
| **Places** | Text Search, Nearby Search, Place Details, Autocomplete, Photos |
| **Environment** | Weather, Air Quality, Pollen, Solar |
| **Maps** | Static Maps, Street View, Maps Embed (free), Maps JavaScript |
| **Other** | Elevation, Time Zone, Address Validation, Roads, Geolocation, Aerial View, Route Optimization |

## Quick Start

### 1. Install the skill

```bash
claude skill install tivojn/google-maps-api-skill
```

### 2. Add your API key

```bash
echo 'GOOGLE_MAPS_API_KEY=your_key_here' >> ~/.env
```

Get a key from the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).

### 3. Enable APIs

Enable the APIs you need in [APIs & Services > Library](https://console.cloud.google.com/apis/library). If you forget, the skill will detect the error and offer to walk you through enabling it via Playwright.

### 4. Use it

Just ask Claude naturally:

- *"What's the weather in Tokyo?"*
- *"Find the best pizza near Times Square"*
- *"How do I drive from LA to San Francisco?"*
- *"What's the air quality in Delhi right now?"*
- *"Is this address valid: 1600 Amphitheatre Pkwy, Mountain View?"*
- *"Can I put solar panels on my roof at [address]?"*

## Usage Examples

```bash
# Geocode an address
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py geocode "1600 Amphitheatre Parkway, Mountain View, CA"

# Get directions
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py directions "New York, NY" "Boston, MA" --mode transit

# Search for places
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py places-search "best ramen in Tokyo"

# Check weather
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py weather 40.7128 -74.0060

# Air quality
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py air-quality 40.7128 -74.0060 --health --pollutants

# Pollen forecast
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py pollen 34.0522 -118.2437 --days 5

# Solar potential
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py solar 37.4219 -122.0841

# Elevation
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py elevation 39.7392 -104.9903

# Validate an address
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py validate-address "1600 Amphitheatre Pkwy, Mountain View, CA 94043"

# Street View
python3 ~/.claude/skills/google-maps-api/scripts/gmaps.py streetview --location "Eiffel Tower, Paris"
```

## Interactive HTML Output

When results benefit from a visual presentation, the skill can generate interactive HTML pages with maps, routes, dashboards, and Street View panoramas — using the **Warm Stone Sunrise** theme (light, warm-toned, premium design). It will always ask before generating HTML.

See `examples/trip-plan-example.html` for a sample.

## Key Features

- **Zero dependencies** — Python stdlib only (`urllib`, `json`, `ssl`)
- **20+ APIs** from a single `gmaps.py` script
- **Guided API enablement** — if an API isn't enabled, the skill offers to walk you through enabling it in your browser via Playwright
- **Interactive HTML pages** — maps, routes, weather dashboards, and more
- **API key security** — `.env` is gitignored; production architecture docs for multi-user deployments

## Project Structure

```
├── SKILL.md           # Full skill definition (API reference, themes, security docs)
├── scripts/
│   └── gmaps.py       # Main CLI script — all 20+ API commands
├── examples/
│   └── trip-plan-example.html
├── .env.example       # API key template
├── .env               # Your actual key (gitignored)
└── README.md
```

## API Key Security

- `.env` is in `.gitignore` — your key stays local
- For personal use, the key is embedded in generated HTML pages (your machine only)
- For production/multi-user apps, see the **API Key Security & Production Architecture** section in `SKILL.md` for a two-key backend proxy setup

## Pricing

Most APIs charge per request, but Google provides a **$200/month free credit**. The Maps Embed API is always free. See [Google Maps pricing](https://developers.google.com/maps/billing-and-pricing/pricing) for details.

## License

MIT
