---
name: sports-analytics-ai
description: AI sports analytics — performance analysis, player scouting, injury prediction, betting analytics, fantasy sports optimization, sports content for MAARS sports agents
---

# Sports Analytics AI — MAARS Reference

## Performance Analysis
```python
PERFORMANCE_ANALYSIS_PROMPT = """
Analyze athlete/team performance data:
Sport: {sport}
Subject: {player_or_team}
Time period: {period}
Data provided: {data_types}

Metrics data:
{performance_data}

Analyze:
1. PERFORMANCE SUMMARY: Key stats vs. league average/personal best
2. STRENGTHS: Where they excel (with specific evidence)
3. WEAKNESSES: Areas limiting performance
4. TRENDS: Performance over time (improving/declining/consistent)
5. SITUATIONAL ANALYSIS: 
   - Home vs. away
   - vs. specific opposition types
   - Clutch performance (high-pressure moments)
6. PHYSICAL LOAD: Minutes played, rest days, fatigue indicators
7. COMPARISON: vs. similar players/teams in the league

Recommendations:
- Tactical adjustments
- Training focus areas
- Matchup advantages to exploit
"""

SPORT_SPECIFIC_METRICS = {
    "basketball": {
        "shooting": ["TS%", "eFG%", "3PAr", "FTr"],
        "playmaking": ["AST%", "TOV%", "USG%"],
        "defense": ["STL%", "BLK%", "DBPM", "DRtg"],
        "overall": ["PER", "WS", "BPM", "VORP"],
    },
    "soccer": {
        "attacking": ["xG", "xA", "Progressive Passes", "Key Passes"],
        "defending": ["PPDA", "Pressures", "Tackle Success%", "Aerial Duels Won%"],
        "possession": ["Pass Accuracy%", "Progressive Carries", "Ball Recoveries"],
        "goalkeeping": ["PSxG", "Save%", "xG Prevented"],
    },
    "american_football": {
        "qb": ["EPA/play", "CPOE", "ADOT", "Air Yards"],
        "skill_positions": ["YAC", "Separation", "Route Win Rate", "Target Share"],
        "line": ["Pass Block Win Rate", "Run Block Win Rate", "Pressure Rate"],
    },
}
```

## Scouting Report Generator
```python
SCOUTING_REPORT_PROMPT = """
Generate a professional scouting report.
Sport: {sport}
Player: {player_name}
Position: {position}
Current team: {team}
Age: {age}
Contract status: {contract}

Available data:
{stats_and_film_notes}

Report structure:
1. EXECUTIVE SUMMARY: 3-sentence evaluation for front office
2. PHYSICAL PROFILE:
   - Measurables (height, weight, speed, wingspan)
   - Athletic comparisons
3. STRENGTHS (detailed, with examples):
   [5-7 specific, observable attributes]
4. WEAKNESSES/CONCERNS:
   [3-5 with honest assessment]
5. PROJECTION:
   - Current level vs. ceiling
   - Development timeline
   - Scheme fit with {scouting_team}
6. COMPARABLE PLAYERS: 2-3 comps with explanation
7. RISK ASSESSMENT: Injury history, attitude, off-field
8. RECOMMENDATION: {tiers} + contract parameters
"""
```

## Injury Prediction & Prevention
```python
INJURY_RISK_PROMPT = """
Analyze injury risk for:
Player: {player_name}
Sport: {sport}
Position: {position}

Data inputs:
- Workload: {recent_workload} (minutes/plays over last 30 days)
- Previous injuries: {injury_history}
- Age/career stage: {age}, {years_pro} years pro
- Biometric data: {biometrics} (if available)
- Performance trend: {performance_trend}

Assessment:
1. CURRENT INJURY RISK: Low/Medium/High/Critical
2. RISK FACTORS: Specific identified concerns
3. VULNERABLE AREAS: Body parts at elevated risk
4. WORKLOAD RECOMMENDATION: Safe load vs. current load
5. PREVENTION PROTOCOLS: Specific interventions
6. MONITORING METRICS: What to track daily

Statistical basis: Compare to historical injury patterns for similar profiles.
"""

# Workload monitoring formula
def calculate_acwr(chronic_workload: float, acute_workload: float) -> dict:
    """Acute:Chronic Workload Ratio — injury risk indicator"""
    acwr = acute_workload / chronic_workload if chronic_workload > 0 else 0
    risk = "Low" if 0.8 <= acwr <= 1.3 else "Elevated" if acwr < 0.8 or acwr <= 1.5 else "High"
    return {"acwr": round(acwr, 2), "risk": risk,
            "sweet_spot": "0.8-1.3 is optimal training load"}
```

## Fantasy Sports AI
```python
FANTASY_OPTIMIZER_PROMPT = """
Optimize a fantasy sports lineup.
Sport: {sport}
Platform: {platform} (DraftKings/FanDuel/Yahoo)
Contest type: {contest_type} (cash/GPP/showdown)
Salary cap: ${salary_cap}
Slate: {slate} (main/afternoon/prime time)

Player pool:
{player_pool_with_salaries}

For GPP (tournament):
- Prioritize upside over floor
- Target lower-owned players with paths to big games
- Stack QB with WR/TE from same team
- Correlate your lineup with a game you think goes high-scoring

For cash (50/50):
- Prioritize high floor, consistent players
- Avoid injury risks
- Minimize boom-or-bust picks

Output:
1. OPTIMAL LINEUP with salary used
2. OWNERSHIP PROJECTION for each player
3. KEY STACKS explained
4. GAME ENVIRONMENT NOTES (weather, pace, O/U)
5. ALTERNATE LINEUP (for diversification)
"""
```

## Sports Betting Analytics
```python
BETTING_ANALYSIS_PROMPT = """
Analyze this betting opportunity:
Sport: {sport}
Game: {matchup}
Line: {line} ({book})
Current market: {market_consensus}
Bet type: {bet_type} (spread/moneyline/total/props)

Analyze:
1. LINE MOVEMENT: Opening vs. current + direction
2. PUBLIC vs. SHARP: Betting percentages if available
3. KEY FACTORS:
   - Head-to-head history (relevant matchups only)
   - Rest/travel disadvantage
   - Injuries and their impact
   - Weather (outdoor sports)
   - Home/away splits
4. MODEL PROJECTION: Expected outcome with range
5. EDGE CALCULATION: (Our probability - implied probability)
6. KELLY CRITERION: Optimal bet size (bankroll management)
7. VERDICT: Bet / No Bet / Value if line improves

DISCLAIMER: Sports betting involves risk. Only bet what you can afford to lose.
"""

def kelly_criterion(win_prob: float, odds_decimal: float, 
                    bankroll: float, fraction: float = 0.25) -> dict:
    """Fractional Kelly for bankroll management"""
    b = odds_decimal - 1  # Net profit per unit
    q = 1 - win_prob
    kelly = (b * win_prob - q) / b
    fractional_kelly = max(0, kelly * fraction)  # Use 1/4 Kelly (safer)
    return {
        "kelly_pct": f"{kelly:.1%}",
        "recommended_bet_pct": f"{fractional_kelly:.1%}",
        "recommended_bet_amount": bankroll * fractional_kelly,
        "edge": (win_prob * odds_decimal - 1),
    }
```

## Sports Content Generation
```python
MATCH_RECAP_PROMPT = """
Write a match recap for:
Sport: {sport}
Game: {home_team} vs. {away_team}
Final score: {score}
Key events: {key_moments}
Stats: {box_score}

Write a compelling {length}-word recap:
- HEADLINE: Captures the story in one line
- LEDE: Most important news first (who won, how dramatically)
- TURNING POINT: The moment that decided the game
- STAR PERFORMERS: Top 3 performers with specific stats
- CONTEXT: What this means for standings/storylines
- QUOTES: [PLACEHOLDER — insert actual quotes from postgame]
- NEXT UP: Both teams' upcoming games

Style: {style} (ESPN-style analysis / casual fan / data-driven)
"""
```

## Sports Data APIs
```python
# Sports APIs
SPORTS_DATA_SOURCES = {
    "ESPN_API": "http://site.api.espn.com/apis/site/v2/sports/{sport}/{league}",
    "sportradar": "https://api.sportradar.com",
    "statmuse": "statmuse.com/q/ (web scrape or API)",
    "basketball_reference": "basketball-reference.com",
    "fbref": "fbref.com (soccer)",
    "baseball_reference": "baseball-reference.com",
    "pro_football_reference": "pro-football-reference.com",
    
    # Free options
    "nfl_data_py": "pip install nfl-data-py",
    "nba_api": "pip install nba-api",
    "pybaseball": "pip install pybaseball",
}

import nfl_data_py as nfl
import pandas as pd

def get_nfl_player_stats(year: int, stat_type: str = "passing"):
    weekly = nfl.import_weekly_data([year])
    return weekly[weekly["position_group"] == stat_type.upper()].groupby("player_name").sum()
```

## Models to Use
- **Performance analysis**: `claude-opus-4-6` (complex multi-variable analysis)
- **Scouting reports**: `claude-opus-4-6` (nuanced evaluation)
- **Fantasy optimization**: `gpt-4o` with code tools (data processing)
- **Betting analysis**: `gpt-4o` (structured analytical output)
- **Sports content writing**: `claude-sonnet-4-6` (engaging prose)
- **Real-time stats/scores**: `perplexity/sonar-pro` (live data)
- **Data analysis**: `gpt-4o` + pandas/code interpreter
