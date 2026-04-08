---
name: travel-hospitality-ai
description: AI travel skills — itinerary planning, hotel recommendations, flight search, concierge automation, guest experience, revenue management, OTA optimization for MAARS travel agents
---

# Travel & Hospitality AI — MAARS Reference

## Itinerary Planner
```python
ITINERARY_PROMPT = """
You are an expert travel concierge. Create a detailed itinerary.

Trip details:
Destination: {destination}
Duration: {days} days / {nights} nights
Departure: {departure_city} on {departure_date}
Travelers: {adults} adults, {children} children (ages: {child_ages})
Budget: {budget_level} (budget/mid-range/luxury/ultra-luxury)
Interests: {interests}
Mobility: {mobility} (any accessibility needs)
Must-see: {must_sees}
Avoid: {avoid}

For each day:
- MORNING: Activity + estimated time + booking tips
- AFTERNOON: Activity or leisure + backup if weather
- EVENING: Dinner recommendation + entertainment
- LOGISTICS: Transport between activities
- ESTIMATED COST: Daily breakdown
- PRO TIPS: Local knowledge, skip-the-line, best times

Also include:
- PRE-TRIP CHECKLIST: Visa, vaccinations, currency, travel insurance
- ACCOMMODATION RECOMMENDATIONS: 3 options by budget
- TRANSPORT: Getting around (public transit/car rental/taxi apps)
- EMERGENCY INFO: Embassy, hospitals, local emergency numbers
"""
```

## Hotel Revenue Management
```python
REVENUE_MANAGEMENT = {
    "dynamic_pricing": {
        "demand_signals": [
            "Booking pace vs. same period last year",
            "Local events/conferences",
            "Competitor rates (STR data)",
            "Weather forecast",
            "Day-of-week patterns",
        ],
        "pricing_rules": {
            "high_demand": "Rate = Base × 1.5-2.5 (events, holidays)",
            "shoulder": "Rate = Base × 0.9-1.1",
            "low_demand": "Last-minute deals, packages, rate fences",
        },
        "overbooking_formula": "Accept bookings up to 105% occupancy (account for ~5% no-show)",
    },
    "channel_management": {
        "direct_booking": "Best rate guarantee, loyalty points — 0% commission",
        "booking_com": "15-17% commission, huge volume",
        "expedia": "15-25% commission",
        "airbnb": "3% host fee",
        "gds": "For corporate + travel agent bookings",
        "priority": "Direct > OTA (protect margins)",
    },
}

REVENUE_ANALYSIS_PROMPT = """
Analyze hotel revenue performance:
Property: {property_name}
Period: {period}
Data: {revenue_data}

Calculate and benchmark:
1. ADR (Average Daily Rate): vs. last year, vs. comp set
2. RevPAR (Revenue per Available Room): Target: ${target}
3. Occupancy Rate: {occupancy}% — above/below market?
4. TRevPAR (Total Revenue per Room): F&B, spa, parking
5. GOP PAR (Gross Operating Profit per Room)
6. Channel Mix: Direct % goal: >30%

Identify:
- Best performing periods and why
- Revenue leak opportunities
- Upsell opportunities (room upgrades, packages)
- Rate integrity issues
"""
```

## Guest Experience AI
```python
CONCIERGE_PROMPT = """
You are a 5-star hotel concierge AI for {hotel_name}.

Guest profile:
Name: {guest_name}
Room: {room_type}
Loyalty tier: {tier}
Stay dates: {checkin} to {checkout}
Purpose: {trip_purpose} (business/leisure/honeymoon/family)
Special occasions: {occasions}
Previous stays: {history}
Preferences: {preferences}

Guest request: {request}

Respond as a knowledgeable, warm concierge:
- Address by name
- Fulfill request with specific recommendations
- Anticipate follow-up needs
- Offer personalized additions based on profile
- If something is unavailable, offer alternatives
- For special occasions, suggest surprise elements

Always offer to arrange bookings/reservations.
"""

REVIEW_RESPONSE_TEMPLATES = {
    "5_star": """
Thank you so much, {guest_name}! We're thrilled to hear {specific_highlight}.
Your kind words about {staff_name} will mean the world to them.
We look forward to welcoming you back to {hotel_name} soon!
""",
    "negative": """
Dear {guest_name}, thank you for taking the time to share your feedback.
We sincerely apologize for {specific_issue} — this is not the standard we hold ourselves to.
{resolution_offered}. I'd love to make this right — please contact me directly at {manager_email}.
""",
}
```

## Flight & Travel APIs
```python
# Amadeus API — flight search
import requests

class AmadeusAPI:
    BASE_URL = "https://api.amadeus.com"
    
    def get_token(self):
        resp = requests.post(f"{self.BASE_URL}/v1/security/oauth2/token",
            data={"grant_type": "client_credentials",
                  "client_id": AMADEUS_KEY, "client_secret": AMADEUS_SECRET})
        return resp.json()["access_token"]
    
    def search_flights(self, origin: str, destination: str, 
                       date: str, adults: int = 1):
        token = self.get_token()
        return requests.get(
            f"{self.BASE_URL}/v2/shopping/flight-offers",
            headers={"Authorization": f"Bearer {token}"},
            params={"originLocationCode": origin,
                    "destinationLocationCode": destination,
                    "departureDate": date,
                    "adults": adults,
                    "currencyCode": "USD",
                    "max": 10}
        ).json()
    
    def search_hotels(self, city_code: str, checkin: str, checkout: str):
        token = self.get_token()
        return requests.get(
            f"{self.BASE_URL}/v3/shopping/hotel-offers",
            headers={"Authorization": f"Bearer {token}"},
            params={"cityCode": city_code, "checkInDate": checkin,
                    "checkOutDate": checkout, "adults": 2}
        ).json()

# Google Places — attractions
def get_attractions(location: str, type_: str = "tourist_attraction"):
    return requests.get(
        "https://maps.googleapis.com/maps/api/place/textsearch/json",
        params={"query": f"{type_} in {location}",
                "key": GOOGLE_PLACES_KEY,
                "type": type_}
    ).json()
```

## Travel Content Generation
```python
DESTINATION_GUIDE_PROMPT = """
Write a comprehensive destination guide for: {destination}

Sections:
1. OVERVIEW: Character, vibe, what makes it unique (100 words)
2. BEST TIME TO VISIT: Month-by-month weather + events + crowd levels
3. GETTING THERE: Nearest airports, transit options, getting around
4. NEIGHBORHOODS: 3-5 key areas and their character
5. TOP EXPERIENCES:
   - Iconic (bucket list)
   - Hidden gems (off the beaten path)
   - Cultural (local experience)
   - Food & drink (must-eat)
   - Adventure/outdoor
6. WHERE TO STAY: Budget / Mid-range / Luxury recommendations
7. PRACTICAL INFO: Visa, currency, language tips, safety, tipping
8. SAMPLE ITINERARIES: 3 days / 5 days / 1 week

Tone: {tone} (adventure/luxury/budget-backpacker/family/solo)
"""
```

## OTA Optimization
```python
OTA_OPTIMIZATION = {
    "booking_com": {
        "ranking_factors": [
            "Review score (weight: 25%)",
            "Availability on requested dates",
            "Price competitiveness",
            "Response rate to messages",
            "Commission level (higher = better placement)",
            "Genius program participation",
            "Completeness of listing",
        ],
        "quick_wins": [
            "Upload 30+ high-quality photos",
            "Complete all amenities checkbox",
            "Enable instant booking",
            "Respond to all reviews within 24h",
            "Set up last-minute promotions",
        ],
    },
    "airbnb": {
        "ranking_factors": [
            "Superhost status",
            "Response rate >90%",
            "Review quality and recency",
            "Pricing (competitive + smart pricing)",
            "Instant book enabled",
            "Cancellation policy (flexible ranks better)",
        ],
    },
}
```

## Models to Use
- **Itinerary planning**: `claude-opus-4-6` (best local knowledge + planning)
- **Guest concierge**: `claude-sonnet-4-6` (warm, personalized)
- **Review responses**: `claude-sonnet-4-6` (empathetic writing)
- **Revenue analysis**: `gpt-4o` with code tools
- **Destination content**: `claude-sonnet-4-6` (engaging travel writing)
- **Real-time prices/availability**: Amadeus API + `perplexity/sonar-pro`
- **Multilingual guest comms**: `gpt-4o` (150+ languages)
