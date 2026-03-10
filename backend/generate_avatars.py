"""
Generate human-like AI portrait avatars for all agents that currently have SVG avatars.
Uses OpenAI GPT Image 1 via emergentintegrations.
Runs as background task with concurrency and resume support.
"""
import os
import sys
import asyncio
import logging
import hashlib
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Add parent to path for imports
sys.path.insert(0, str(ROOT_DIR))

from motor.motor_asyncio import AsyncIOMotorClient
from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

MONGO_URL = os.environ.get("MONGO_URL")
DB_NAME = os.environ.get("DB_NAME", "maars_db")
LLM_KEY = os.environ.get("EMERGENT_LLM_KEY")
AVATAR_DIR = ROOT_DIR / "static" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)

# Backend URL for constructing avatar URLs
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL", "")

CONCURRENT_LIMIT = 3
semaphore = asyncio.Semaphore(CONCURRENT_LIMIT)

# Diverse appearance descriptors for variety
SKIN_TONES = ["light", "medium", "olive", "tan", "brown", "dark"]
HAIR_STYLES = ["short straight", "short wavy", "medium length", "long straight", "curly", "slicked back", "buzz cut", "shoulder length"]
HAIR_COLORS = ["black", "dark brown", "brown", "auburn", "blonde", "gray", "silver"]
ATTIRE = ["navy suit", "charcoal blazer", "white shirt", "gray turtleneck", "dark blue shirt", "black blazer", "burgundy top", "cream blouse"]
BACKGROUNDS = ["dark navy studio", "dark charcoal gradient", "deep slate gray", "dark teal gradient", "midnight blue"]


def get_appearance(agent_name, agent_role, idx):
    """Generate deterministic but diverse appearance based on agent name hash."""
    h = hashlib.md5(agent_name.encode()).hexdigest()
    n = int(h, 16)
    
    skin = SKIN_TONES[n % len(SKIN_TONES)]
    hair_style = HAIR_STYLES[(n >> 4) % len(HAIR_STYLES)]
    hair_color = HAIR_COLORS[(n >> 8) % len(HAIR_COLORS)]
    attire = ATTIRE[(n >> 12) % len(ATTIRE)]
    bg = BACKGROUNDS[(n >> 16) % len(BACKGROUNDS)]
    
    # Determine gender hint from common name patterns
    gender = "male" if n % 2 == 0 else "female"
    age_range = ["late 20s", "early 30s", "mid 30s", "early 40s", "mid 40s"][(n >> 20) % 5]
    
    return {
        "gender": gender,
        "age": age_range,
        "skin": skin,
        "hair_style": hair_style,
        "hair_color": hair_color,
        "attire": attire,
        "background": bg,
    }


def build_prompt(agent_name, agent_role, idx):
    """Build a prompt for a professional headshot portrait."""
    app = get_appearance(agent_name, agent_role, idx)
    
    return (
        f"Professional corporate headshot portrait photo of a {app['gender']} professional in their {app['age']}, "
        f"{app['skin']} skin tone, {app['hair_color']} {app['hair_style']} hair, "
        f"wearing a {app['attire']}, "
        f"confident and approachable expression, looking slightly off-camera, "
        f"studio lighting with soft shadows, {app['background']} background, "
        f"4K quality, photorealistic, sharp focus on face, shallow depth of field, "
        f"corporate business portrait style"
    )


async def generate_single_avatar(image_gen, agent, idx, total, db):
    """Generate a single avatar and save it."""
    agent_id = agent["agent_id"]
    name = agent["name"]
    role = agent.get("role", "")
    
    file_path = AVATAR_DIR / f"{agent_id}.png"
    
    # Skip if already generated
    if file_path.exists() and file_path.stat().st_size > 1000:
        logger.info(f"[{idx}/{total}] SKIP {name} - already exists")
        return True
    
    async with semaphore:
        try:
            prompt = build_prompt(name, role, idx)
            logger.info(f"[{idx}/{total}] Generating {name} ({role})...")
            
            images = await image_gen.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1,
            )
            
            if images and len(images) > 0:
                with open(file_path, "wb") as f:
                    f.write(images[0])
                
                # Update MongoDB with the new avatar URL
                avatar_url = f"/api/static/avatars/{agent_id}.png"
                await db.agents.update_one(
                    {"agent_id": agent_id},
                    {"$set": {"avatar": avatar_url}}
                )
                
                logger.info(f"[{idx}/{total}] OK {name} -> {file_path.name} ({len(images[0])} bytes)")
                return True
            else:
                logger.warning(f"[{idx}/{total}] EMPTY {name} - no image returned")
                return False
                
        except Exception as e:
            logger.error(f"[{idx}/{total}] FAIL {name}: {e}")
            return False


async def main():
    logger.info("=" * 60)
    logger.info("MAARS Avatar Generation Script")
    logger.info("=" * 60)
    
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get all agents with SVG avatars (base64 data URIs)
    cursor = db.agents.find(
        {"avatar": {"$regex": "^data:image/svg"}},
        {"_id": 0, "agent_id": 1, "name": 1, "role": 1, "avatar": 1}
    )
    agents = await cursor.to_list(length=500)
    
    # Also check for agents whose avatars might already be generated locally but DB not updated
    already_done = 0
    to_generate = []
    for a in agents:
        file_path = AVATAR_DIR / f"{a['agent_id']}.png"
        if file_path.exists() and file_path.stat().st_size > 1000:
            already_done += 1
            # Update DB if needed
            expected_url = f"/api/static/avatars/{a['agent_id']}.png"
            if a.get("avatar", "").startswith("data:"):
                await db.agents.update_one(
                    {"agent_id": a["agent_id"]},
                    {"$set": {"avatar": expected_url}}
                )
        else:
            to_generate.append(a)
    
    total = len(to_generate)
    logger.info(f"Total SVG agents: {len(agents)}")
    logger.info(f"Already generated: {already_done}")
    logger.info(f"To generate: {total}")
    logger.info(f"Concurrent limit: {CONCURRENT_LIMIT}")
    logger.info("-" * 60)
    
    if total == 0:
        logger.info("All avatars already generated!")
        client.close()
        return
    
    image_gen = OpenAIImageGeneration(api_key=LLM_KEY)
    
    # Process in batches
    batch_size = CONCURRENT_LIMIT * 2
    success = 0
    fail = 0
    
    for batch_start in range(0, total, batch_size):
        batch = to_generate[batch_start:batch_start + batch_size]
        tasks = []
        for i, agent in enumerate(batch):
            idx = batch_start + i + 1 + already_done
            tasks.append(generate_single_avatar(image_gen, agent, idx, len(agents), db))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if r is True:
                success += 1
            else:
                fail += 1
        
        logger.info(f"Batch complete: {batch_start + len(batch)}/{total} | Success: {success} | Failed: {fail}")
        
        # Small delay between batches to avoid rate limits
        if batch_start + batch_size < total:
            await asyncio.sleep(2)
    
    logger.info("=" * 60)
    logger.info(f"COMPLETE: {success} success, {fail} failed out of {total}")
    logger.info("=" * 60)
    
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
