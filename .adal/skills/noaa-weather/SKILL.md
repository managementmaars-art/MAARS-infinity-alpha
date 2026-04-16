---
name: noaa-weather
description: >
  The NOAA Weather.gov API provides access to National Weather Service forecasts,
  alerts, observations, radar data, and more for the United States. Use this skill
  to fetch weather forecasts, active alerts, station observations, and zone data.
  No API key is required — just a User-Agent header.

metadata:
  author: Outsharp Inc.
  version: 0.1.0

compatibility:
  requirements:
    - Internet access
    - Any HTTP client (curl, wget, fetch, requests, etc.)
    - A JSON parser (jq, Python json module, etc.)
  notes:
    - All data is free and open — no API key, account, or authentication is needed.
    - A User-Agent header is required on every request to identify your application.
    - Responses are GeoJSON by default; other formats available via Accept header.
    - Rate limits are generous but undisclosed; retry after 5 seconds on errors.
    - Observation data may be delayed up to 20 minutes from the upstream MADIS source.

allowed-tools:
  - Bash(curl:https://api.weather.gov/*)
  - Bash(python*:*)
  - Bash(pip*:*)
  - Bash(node*:*)
  - Bash(npx*:*)
  - Bash(jq:*)

---

# NOAA Weather.gov API

The [National Weather Service (NWS) API](https://www.weather.gov/documentation/services-web-api) provides free, open access to weather forecasts, alerts, observations, radar data, and more for the United States. All data is public domain — no API key or account required.

> Always check the [official API documentation](https://www.weather.gov/documentation/services-web-api) and [OpenAPI spec](https://api.weather.gov/openapi.json) for the latest endpoint details.

---

## Base URL

```
https://api.weather.gov
```

---

## Authentication

No API key is needed. However, a **User-Agent header is required** on every request to identify your application.

```
User-Agent: (myweatherapp.com, contact@myweatherapp.com)
```

The string can be anything — the more unique to your application, the less likely it will be affected by a security event. Requests without a User-Agent may be blocked.

---

## Key Concepts

| Term | Description |
|------|-------------|
| **Point** | A latitude/longitude coordinate. Use `/points/{lat},{lon}` to resolve it to grid and zone info. |
| **Gridpoint** | A 2.5km forecast grid cell identified by a WFO office ID and x,y coordinates. |
| **WFO** | Weather Forecast Office — the NWS office responsible for a geographic area (e.g., `DEN`, `OKX`, `LOT`). |
| **Zone** | A geographic area used for forecasts and alerts. Types include `land`, `marine`, `forecast`, `fire`, `county`. |
| **Station** | An observation station (e.g., `KDEN` for Denver International Airport) that reports current conditions. |
| **Alert** | A weather warning, watch, or advisory issued by the NWS (e.g., tornado warning, winter storm watch). |
| **SIGMET/AIRMET** | Aviation weather advisories for significant or airmen's meteorological conditions. |
| **TAF** | Terminal Aerodrome Forecast — aviation weather forecast for an airport. |
| **GeoJSON** | The default response format — standard JSON with geographic feature geometry. |

---

## Core Workflow: Get a Forecast for a Location

The API uses a **two-step pattern** to get a forecast:

### Step 1: Resolve coordinates to a grid point

```
GET /points/{latitude},{longitude}
```

This returns metadata including the WFO office, grid coordinates, and URLs for forecasts.

### Step 2: Fetch the forecast using the grid info

```
GET /gridpoints/{wfo}/{gridX},{gridY}/forecast
```

This returns the human-readable 12-hour period forecast (7 days).

### Example (curl)

```bash
# Step 1: Get grid info for Denver, CO
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/points/39.7456,-104.9994" | jq '.properties.forecast'

# Returns: "https://api.weather.gov/gridpoints/BOU/63,62/forecast"

# Step 2: Get the forecast
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/gridpoints/BOU/63,62/forecast" | jq '.properties.periods[0]'
```

---

## Endpoint Reference

### Points / Location Lookup

| Endpoint | Description |
|----------|-------------|
| `GET /points/{lat},{lon}` | Metadata for a coordinate — returns grid info, forecast URLs, timezone, county, zone |
| `GET /points/{lat},{lon}/stations` | Nearby observation stations (deprecated — use gridpoint stations instead) |

### Forecasts

| Endpoint | Description |
|----------|-------------|
| `GET /gridpoints/{wfo}/{x},{y}/forecast` | 12-hour period forecast (7-day), human-readable |
| `GET /gridpoints/{wfo}/{x},{y}/forecast/hourly` | Hourly forecast (7-day), human-readable |
| `GET /gridpoints/{wfo}/{x},{y}` | Raw numerical forecast data (temperature, wind, precip probability, etc.) |
| `GET /gridpoints/{wfo}/{x},{y}/stations` | Observation stations within the grid area |

### Alerts

| Endpoint | Description |
|----------|-------------|
| `GET /alerts` | Query alerts (past 7 days) with filters: `status`, `event`, `area`, `zone`, `urgency`, `severity`, `certainty` |
| `GET /alerts/active` | All currently active alerts |
| `GET /alerts/active/count` | Count of active alerts by area, zone, and region |
| `GET /alerts/active/zone/{zoneId}` | Active alerts for a specific zone |
| `GET /alerts/active/area/{area}` | Active alerts for a state (2-letter code) or marine area |
| `GET /alerts/active/region/{region}` | Active alerts for a marine region |
| `GET /alerts/types` | List of recognized alert event types |
| `GET /alerts/{id}` | Retrieve a specific alert by its ID |

### Stations & Observations

| Endpoint | Description |
|----------|-------------|
| `GET /stations` | List observation stations; filter by `id`, `state`, `limit` |
| `GET /stations/{stationId}` | Metadata for a specific station |
| `GET /stations/{stationId}/observations` | Historical observations (paginated) |
| `GET /stations/{stationId}/observations/latest` | Most recent observation |
| `GET /stations/{stationId}/observations/{time}` | Observation at a specific ISO-8601 timestamp |

### Zones

| Endpoint | Description |
|----------|-------------|
| `GET /zones` | Query zones; filter by `id`, `area`, `type`, `point`, `include_geometry` |
| `GET /zones/{type}` | List zones of a specific type (`land`, `marine`, `forecast`, `fire`, `county`) |
| `GET /zones/{type}/{zoneId}` | Metadata for a specific zone |
| `GET /zones/{type}/{zoneId}/forecast` | Current text forecast for a zone |
| `GET /zones/forecast/{zoneId}/observations` | Observations within a forecast zone |
| `GET /zones/forecast/{zoneId}/stations` | Stations within a forecast zone |

### Aviation

| Endpoint | Description |
|----------|-------------|
| `GET /stations/{stationId}/tafs` | Terminal Aerodrome Forecasts for a station |
| `GET /stations/{stationId}/tafs/{date}/{time}` | Specific TAF |
| `GET /aviation/cwsus/{cwsuId}` | Center Weather Service Unit metadata |
| `GET /aviation/cwsus/{cwsuId}/cwas` | Center Weather Advisories |
| `GET /aviation/sigmets` | Query SIGMETs/AIRMETs with filters |
| `GET /aviation/sigmets/{atsu}` | SIGMETs for a specific ATSU |
| `GET /aviation/cwsus/{cwsuId}/cwas/{date}/{sequence}` | Specific Center Weather Advisory |
| `GET /aviation/sigmets/{atsu}/{date}/{time}` | Specific SIGMET by date and time |

### Radar

| Endpoint | Description |
|----------|-------------|
| `GET /radar/servers` | List of radar servers |
| `GET /radar/stations` | List of radar stations; filter by `stationType`, `host` |
| `GET /radar/stations/{stationId}` | Specific radar station metadata |
| `GET /radar/stations/{stationId}/alarms` | Alarms for a radar station |
| `GET /radar/profilers/{stationId}` | Wind profiler data |

### Text Products

| Endpoint | Description |
|----------|-------------|
| `GET /products` | Query text products; filter by `location`, `type`, `start`, `end` |
| `GET /products/{productId}` | Specific text product |
| `GET /products/types` | List of valid product type codes |
| `GET /products/locations` | List of valid product issuance locations |
| `GET /products/types/{typeId}` | Products of a given type |
| `GET /products/types/{typeId}/locations` | Issuance locations for a product type |
| `GET /products/locations/{locationId}/types` | Product types for a location |
| `GET /products/types/{typeId}/locations/{locationId}` | Products by type and location |
| `GET /products/types/{typeId}/locations/{locationId}/latest` | Latest product by type and location |

### Offices

| Endpoint | Description |
|----------|-------------|
| `GET /offices/{officeId}` | NWS forecast office metadata |
| `GET /offices/{officeId}/headlines` | News headlines from an office |
| `GET /offices/{officeId}/headlines/{headlineId}` | Specific headline |
| `GET /offices/{officeId}/briefing` | Active office briefing |
| `GET /offices/{officeId}/weatherstories` | Active weather stories |

### Miscellaneous

| Endpoint | Description |
|----------|-------------|
| `GET /glossary` | Weather terminology definitions |
| `GET /points/{lat},{lon}/radio` | NOAA Weather Radio script for a location |
| `GET /radio/{callSign}/broadcast` | Weather Radio broadcast script by call sign |

---

## Response Format

The default response format is **GeoJSON** (`application/geo+json`). Control the format with the `Accept` header:

| Format | Accept Header |
|--------|---------------|
| GeoJSON (default) | `application/geo+json` |
| JSON-LD | `application/ld+json` |
| DWML (XML) | `application/vnd.noaa.dwml+xml` |
| CAP (Alerts XML) | `application/cap+xml` |
| OXML (Observations XML) | `application/vnd.noaa.obs+xml` |
| ATOM | `application/atom+xml` |

All times are in **ISO-8601** format.

---

## Feature Flags

Optional headers to enable new features:

| Header Value | Description |
|--------------|-------------|
| `Feature-Flags: forecast_temperature_qv` | Represent temperature as QuantitativeValue |
| `Feature-Flags: forecast_wind_speed_qv` | Represent wind speed as QuantitativeValue |
| `Feature-Flags: obs_station_provider` | Show MADIS provider details for stations |

---

## Code Examples

### Get Forecast for a Location (Python)

```python
import requests

BASE = "https://api.weather.gov"
HEADERS = {"User-Agent": "(myapp, contact@example.com)"}

# Step 1: Resolve coordinates
point = requests.get(f"{BASE}/points/39.7456,-104.9994", headers=HEADERS).json()
forecast_url = point["properties"]["forecast"]

# Step 2: Get forecast
forecast = requests.get(forecast_url, headers=HEADERS).json()
for period in forecast["properties"]["periods"][:4]:
    print(f"{period['name']}: {period['detailedForecast']}")
```

### Get Active Alerts for a State (curl)

```bash
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/alerts/active?area=CO" \
  | jq '.features[] | {event: .properties.event, headline: .properties.headline}'
```

### Get Current Observations (curl)

```bash
# Get latest observation from Denver International Airport
curl -s -H "User-Agent: MyApp" \
  "https://api.weather.gov/stations/KDEN/observations/latest" \
  | jq '.properties | {
    temperature: .temperature.value,
    windSpeed: .windSpeed.value,
    description: .textDescription
  }'
```

### Get Hourly Forecast (Node.js)

```javascript
const https = require("https");

const options = {
  headers: { "User-Agent": "MyApp (contact@example.com)" },
};

// Step 1: Get grid info
https.get("https://api.weather.gov/points/40.7128,-74.0060", options, (res) => {
  let data = "";
  res.on("data", (chunk) => (data += chunk));
  res.on("end", () => {
    const forecastUrl = JSON.parse(data).properties.forecastHourly;

    // Step 2: Get hourly forecast
    https.get(forecastUrl, options, (res2) => {
      let forecast = "";
      res2.on("data", (chunk) => (forecast += chunk));
      res2.on("end", () => {
        const periods = JSON.parse(forecast).properties.periods;
        periods.slice(0, 6).forEach((p) => {
          console.log(`${p.startTime}: ${p.temperature}°${p.temperatureUnit} - ${p.shortForecast}`);
        });
      });
    });
  });
});
```

### Find Nearby Stations (Python)

```python
import requests

BASE = "https://api.weather.gov"
HEADERS = {"User-Agent": "(myapp, contact@example.com)"}

# Get grid info for a point
point = requests.get(f"{BASE}/points/34.0522,-118.2437", headers=HEADERS).json()
stations_url = point["properties"]["observationStations"]

# List nearby stations
stations = requests.get(stations_url, headers=HEADERS).json()
for station in stations["features"][:5]:
    props = station["properties"]
    print(f"{props['stationIdentifier']}: {props['name']}")
```

---

## Rate Limits

The rate limit is not publicly documented but is described as "generous for typical use."

| Guideline | Details |
|-----------|---------|
| Rate limit | Undisclosed, but generous |
| On limit exceeded | Request returns an error; retry after ~5 seconds |
| User-Agent | Required — requests without it may be blocked |
| Best practice | Cache `/points` responses (they rarely change) to reduce calls |

---

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Parse the JSON response |
| 301/302 | Redirect | Follow the redirect |
| 404 | Not found | Check coordinates, station ID, or zone ID |
| 500 | Server error | Retry with backoff |
| 503 | Service unavailable | Common on `/radar/queues` — add filters to reduce results |

Error responses include a JSON body with `type`, `title`, `status`, `detail`, and `correlationId` fields.

---

## Known Issues

- `/radar/queues` endpoints may return 503 errors when results are large — filter with additional parameters.
- Station observations outside the central timezone may show null 24-hour max/min temperatures.
- Observation data can be delayed up to 20 minutes from the upstream MADIS source.
- Icon endpoints (`/icons`) are deprecated.

---

## Resources

| Resource | URL |
|----------|-----|
| API Documentation | [weather.gov/documentation/services-web-api](https://www.weather.gov/documentation/services-web-api) |
| OpenAPI Specification | [api.weather.gov/openapi.json](https://api.weather.gov/openapi.json) |
| GitHub Discussion | [weather-gov.github.io/api](https://weather-gov.github.io/api/) |
| Operational Support | nco.ops@noaa.gov |

---

## Changelog

- **0.1.0** — Initial release with forecasts, alerts, observations, stations, zones, aviation, radar, and text products.
