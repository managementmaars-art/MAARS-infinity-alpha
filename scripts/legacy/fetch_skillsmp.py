import cloudscraper
import os
import json
import time

API_KEY = 'sk_live_skillsmp_nmzbSNajmLgoh-VYDqNT2xZBCdHRL63lHEDJws0_Xlg'
BASE = 'c:/Users/Yaleena Yara/MAARS-Command/.claude/skills'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

scraper = cloudscraper.create_scraper()

# First, figure out the total and pagination
r = scraper.get('https://skillsmp.com/api/skills?limit=100&page=1', headers=HEADERS)
data = r.json()
print('Keys:', list(data.keys()))
print('Sample:', json.dumps(data, indent=2)[:1000])
