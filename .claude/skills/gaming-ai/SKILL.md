---
name: gaming-ai
description: AI gaming skills — NPC dialogue, procedural generation, game design, Unity/Unreal integration, player behavior analysis, anti-cheat, esports analytics for MAARS gaming agents
---

# Gaming AI — MAARS Reference

## NPC Dialogue System
```python
NPC_DIALOGUE_PROMPT = """
You are generating dynamic NPC dialogue for: {game_name}
Genre: {genre}
NPC: {npc_name} — {npc_role} — Personality: {personality}
Player context: {player_history}
Current situation: {current_situation}
Player action/statement: {player_input}

Generate response considering:
- NPC's knowledge limitations (they don't know everything)
- Personality consistency (gruff guard talks differently than wise sage)
- Player's relationship level with NPC (0-100): {relationship_level}
- Quest state: {active_quests}
- World state: {world_events}

Response format:
DIALOGUE: [NPC speech — 1-3 sentences, in character]
EMOTION: [neutral/friendly/suspicious/hostile/scared/excited]
ACTION: [optional: NPC action gesture]
MEMORY_UPDATE: [what NPC remembers from this interaction]
"""

# Conversation memory system
class NPCMemory:
    def __init__(self, npc_id: str):
        self.npc_id = npc_id
        self.player_interactions = []
        self.relationship_score = 0
        self.known_facts = []
    
    def update(self, interaction: dict):
        self.player_interactions.append(interaction)
        self.relationship_score = max(-100, min(100, 
            self.relationship_score + interaction.get("relationship_delta", 0)))
        if interaction.get("revealed_info"):
            self.known_facts.extend(interaction["revealed_info"])
```

## Procedural Content Generation
```python
WORLD_GENERATION_PROMPT = """
Generate a procedural {location_type} for a {genre} game.

Seed: {seed}
Theme: {theme}
Difficulty: {difficulty}/10
Player level: {player_level}
Previous area: {previous_area}

Generate:
1. LAYOUT DESCRIPTION: Map topology, key areas (3-5)
2. ENCOUNTERS: Enemy types, quantities, placement rationale
3. LOOT TABLES: Items with rarity weights
4. ENVIRONMENTAL STORYTELLING: 3 details that imply backstory
5. HIDDEN SECRETS: 1-2 optional discoveries
6. BOSS ROOM: Unique encounter design
7. AMBIENT DETAILS: Sound, weather, lighting mood

Ensure:
- Difficulty curve feels earned, not random
- Loot worth the challenge at this level
- Area tells a micro-story
"""

import random
import json

def generate_loot_table(player_level: int, area_difficulty: float) -> list:
    """Procedural loot generation"""
    rarities = {
        "common": 0.60 - (area_difficulty * 0.05),
        "uncommon": 0.25,
        "rare": 0.10 + (area_difficulty * 0.03),
        "epic": 0.04 + (area_difficulty * 0.01),
        "legendary": 0.01 + (area_difficulty * 0.005),
    }
    item_count = random.randint(2, 5)
    return [{"rarity": random.choices(list(rarities.keys()), 
                                      weights=list(rarities.values()))[0],
             "item_level": player_level + random.randint(-2, 3)}
            for _ in range(item_count)]
```

## Unity Integration
```csharp
// Unity C# — AI dialogue integration
using UnityEngine;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

public class AIDialogueManager : MonoBehaviour
{
    private static readonly HttpClient client = new HttpClient();
    private const string API_URL = "https://your-maars-api.com/v1/npc-dialogue";
    
    public async Task<DialogueResponse> GetNPCResponse(
        string npcId, string playerInput, NPCState state)
    {
        var payload = new {
            npc_id = npcId,
            player_input = playerInput,
            npc_state = state,
            context = GetWorldContext()
        };
        
        var content = new StringContent(
            JsonConvert.SerializeObject(payload),
            Encoding.UTF8, "application/json");
        
        var response = await client.PostAsync(API_URL, content);
        var json = await response.Content.ReadAsStringAsync();
        return JsonConvert.DeserializeObject<DialogueResponse>(json);
    }
    
    // Cache responses for common interactions
    private Dictionary<string, DialogueResponse> _cache = new();
    
    public async Task<DialogueResponse> GetCachedResponse(string key, 
        System.Func<Task<DialogueResponse>> generator)
    {
        if (_cache.TryGetValue(key, out var cached)) return cached;
        var result = await generator();
        _cache[key] = result;
        return result;
    }
}
```

## Player Behavior Analysis
```python
PLAYER_ANALYTICS = {
    "engagement_metrics": [
        "session_length", "sessions_per_week", "return_rate_D1/D7/D30",
        "feature_usage_depth", "progression_speed", "social_interactions",
    ],
    "churn_signals": [
        "session_length decline >30%",
        "progression stall (same area 3+ sessions)",
        "failed attempts spike (frustration)",
        "social feature abandonment",
        "decreased purchase frequency",
    ],
    "monetization_signals": [
        "High engagement + slow progression = conversion candidate",
        "Cosmetic focus = battlepass candidate",
        "Competitive player = tournament/ranked pass candidate",
        "Social player = clan/guild features candidate",
    ],
}

PLAYER_SEGMENTATION_PROMPT = """
Analyze this player's behavior data:
{player_data}

Segment by:
1. PLAYER TYPE: Killer/Achiever/Explorer/Socializer (Bartle taxonomy)
2. SPEND PROPENSITY: Non-spender/Minnow/Dolphin/Whale
3. CHURN RISK: Low/Medium/High + primary reason
4. OPTIMAL INTERVENTION: What would re-engage this player?

Recommend:
- Personalized push notification copy
- Optimal re-engagement offer
- Feature to highlight in next session
"""
```

## Anti-Cheat & Fair Play
```python
ANTI_CHEAT_SIGNALS = {
    "aim_assist_detection": [
        "Sub-1ms reaction time (human floor: ~100ms)",
        "Impossible angle snaps (>180°/frame)",
        "100% headshot rate over 50+ kills",
        "Tracking through walls (pre-aim before visibility)",
    ],
    "speed_hack_detection": [
        "Movement speed exceeds server-side max",
        "Position delta between frames > physics max",
        "Teleportation (position jump > 10m instantaneous)",
    ],
    "economy_exploit": [
        "Currency gain rate > 3σ above mean",
        "Impossible crafting sequences (missing intermediate steps)",
        "Duplicate item signatures in inventory",
    ],
    "response_pattern": {
        "shadow_ban": "Let cheater play but match with other cheaters",
        "soft_ban": "Restricted features, warning message",
        "hard_ban": "Account + device fingerprint ban",
        "appeal_window": "7 days for false positive appeals",
    }
}
```

## Game Design AI Assistant
```python
GAME_DESIGN_PROMPT = """
Game design consultant for: {game_concept}
Target audience: {audience}
Monetization model: {model} (F2P/premium/subscription/battlepass)
Platform: {platform}

Analyze and improve:
1. CORE LOOP: Is it fun in 30 seconds? 3 minutes? 30 minutes?
2. PROGRESSION SYSTEM: Power curve, unlock pacing
3. SOCIAL HOOKS: Multiplayer/sharing/competition features
4. RETENTION MECHANICS: Daily/weekly/seasonal systems
5. MONETIZATION ALIGNMENT: Does it feel fair or pay-to-win?
6. COMPETITIVE POSITIONING: What makes this unique?

Identify:
- Player friction points
- Drop-off risks by player type
- Monetization without exploitation
"""
```

## Models to Use
- **NPC dialogue**: `claude-sonnet-4-6` (creative, consistent personality)
- **Procedural world gen**: `claude-opus-4-6` (complex systemic thinking)
- **Player analytics**: `gpt-4o` (data pattern recognition)
- **Anti-cheat logic**: `claude-opus-4-6` (subtle pattern detection)
- **Game design review**: `claude-opus-4-6` + `gpt-4o`
- **Localization (100+ languages)**: `gpt-4o` (multilingual)
