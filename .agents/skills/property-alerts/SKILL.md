---
name: property-alerts
description: Real estate property listing alerts and monitoring
version: 1.0.0
author: OpenClaw
license: MIT
---

# Property Alerts

Monitor real estate listings with saved searches, instant alerts, and price change detection.

## Features

- **Saved Searches**: Save your search criteria and get automatic updates
- **Instant Alerts**: Get notified of new listings, price changes, and status updates
- **Price Change Detection**: Track price drops, increases, and market changes
- **Price History**: View historical price data for tracked properties
- **Multi-Source Support**: Works with Zillow API or simulated data

## Installation

```bash
npm install
npm run build
```

## Configuration

Set the optional Zillow API key for real data:

```bash
export ZILLOW_API_KEY="your_api_key_here"
```

Without an API key, the skill uses simulated data for demonstration.

## Usage

### CLI Commands

```bash
# Search for properties
npm run cli -- search "Austin, TX" --min-price 300000 --beds 3

# Save a search with alerts
npm run cli -- save-search "Austin Homes" "Austin, TX" --max-price 500000

# List saved searches
npm run cli -- list-searches

# Check for new alerts
npm run cli -- check

# View alerts
npm run cli -- alerts --unread

# View price history
npm run cli -- history prop-001

# Statistics
npm run cli -- stats
```

### Library Usage

```typescript
import { PropertyAlertsSkill } from '@openclaw/property-alerts';

const skill = new PropertyAlertsSkill();

// Search for properties
const results = await skill.searchProperties({
  location: 'Austin, TX',
  minPrice: 300000,
  maxPrice: 600000,
  minBedrooms: 3,
  propertyTypes: ['house', 'condo']
});

// Save a search
const saved = await skill.saveSearch('Austin Search', {
  location: 'Austin, TX',
  minPrice: 300000
});

// Check for alerts
const alerts = await skill.checkForAlerts();

// Get price history
const history = await skill.getPriceHistory('prop-001');
```

## Alert Types

- **new_listing**: Property newly listed matching your criteria
- **price_drop**: Price has decreased
- **price_increase**: Price has increased
- **status_change**: Property status changed (sold, pending, etc.)
- **back_on_market**: Property is active again after being off market

## Database Schema

The skill stores data in SQLite at `~/.openclaw/skills/property-alerts/data.db`:

- **saved_searches**: Search criteria and alert settings
- **properties**: Tracked property listings
- **price_history**: Historical price changes
- **alerts**: Generated alerts with property data
