# NOAA Weather Skill

Teaches AI agents how to fetch weather data from the [NOAA Weather.gov API](https://www.weather.gov/documentation/services-web-api) — a free, public service from the National Weather Service providing forecasts, alerts, observations, and more for the United States.

## What This Skill Provides

The `SKILL.md` file gives your agent full context on:

- **Forecasts** — 12-hour period, hourly, and raw numerical forecasts for any US location
- **Active Alerts** — Warnings, watches, and advisories by state, zone, or region
- **Station Observations** — Current conditions from thousands of observation stations
- **Core Workflow** — The two-step pattern: resolve coordinates via `/points` → fetch forecast via `/gridpoints`
- **Aviation Data** — TAFs, SIGMETs, AIRMETs, and Center Weather Advisories
- **Radar & Stations** — Radar station metadata, wind profilers, and observation station lookups
- **Zones & Offices** — Zone-based forecasts, NWS office metadata, and text products
- **Rate Limits & Error Handling** — Best practices for caching and retry behavior

## When to Use This Skill

Use the NOAA Weather skill when your agent needs to:

- Get the weather forecast for any US latitude/longitude
- Check active weather alerts for a state or zone
- Fetch current conditions (temperature, wind, humidity) from an observation station
- Look up nearby weather stations for a location
- Access aviation weather data (TAFs, SIGMETs)
- Retrieve zone-based text forecasts
- Query historical observations from a station

## Getting Started

### 1. No API Key Required

The NOAA Weather API is **fully public and free**. The only requirement is a `User-Agent` header on every request to identify your application:

```
User-Agent: (myweatherapp.com, contact@myweatherapp.com)
```

### 2. Get a Forecast (Two-Step Pattern)

```bash
# Step 1: Resolve coordinates to grid info
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/points/39.7456,-104.9994" | jq '.properties.forecast'

# Step 2: Fetch the forecast
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/gridpoints/BOU/63,62/forecast" \
  | jq '.properties.periods[0]'
```

### 3. Get Active Alerts

```bash
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/alerts/active?area=TX" \
  | jq '.features[].properties.headline'
```

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Point** | A lat/lon coordinate resolved via `/points/{lat},{lon}` to get grid and zone info |
| **Gridpoint** | A 2.5km forecast grid cell identified by WFO office + x,y coordinates |
| **WFO** | Weather Forecast Office — the NWS office responsible for a geographic area |
| **Zone** | A geographic area for forecasts and alerts (land, marine, forecast, fire, county) |
| **Station** | An observation station (e.g., `KDEN`) reporting current weather conditions |
| **Alert** | A weather warning, watch, or advisory from the NWS |
| **User-Agent** | Required header on every request — identifies your application |

## Endpoint Summary

| Category | Key Endpoints | Purpose |
|----------|---------------|---------|
| **Points** | `/points/{lat},{lon}` | Resolve coordinates to grid/forecast info |
| **Forecasts** | `/gridpoints/{wfo}/{x},{y}/forecast` | 12-hour or hourly forecasts |
| **Alerts** | `/alerts/active?area={state}` | Active weather alerts |
| **Stations** | `/stations/{id}/observations/latest` | Current conditions |
| **Zones** | `/zones/{type}/{zoneId}/forecast` | Zone-based text forecasts |
| **Aviation** | `/stations/{id}/tafs`, `/aviation/sigmets` | Aviation weather |
| **Radar** | `/radar/stations` | Radar station info |
| **Products** | `/products` | NWS text products |

## Tips

- **Cache `/points` responses** — grid info for a coordinate rarely changes, so cache it to reduce API calls.
- **Use the two-step pattern** — always start with `/points/{lat},{lon}` to get the correct WFO and grid coordinates for forecasts.
- **GeoJSON is the default** — responses include geometry; use `jq` or a JSON parser to extract `.properties`.
- **Alerts support rich filtering** — filter by `status`, `event`, `urgency`, `severity`, `certainty`, `area`, and `zone`.
- **Station IDs are ICAO codes** — airports like `KDEN` (Denver), `KJFK` (JFK), `KLAX` (LAX) are common stations.
- **Observation data has a ~20 minute delay** — data comes from the MADIS upstream source.
- **All times are ISO-8601** — responses use standard datetime formatting.

## Resources

| Resource | URL |
|----------|-----|
| API Documentation | [weather.gov/documentation/services-web-api](https://www.weather.gov/documentation/services-web-api) |
| OpenAPI Spec | [api.weather.gov/openapi.json](https://api.weather.gov/openapi.json) |
| GitHub Discussion | [weather-gov.github.io/api](https://weather-gov.github.io/api/) |
| NWS Home | [weather.gov](https://www.weather.gov) |
