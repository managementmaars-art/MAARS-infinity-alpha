#!/usr/bin/env node

import { cpSync, mkdirSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { homedir } from 'os';

const __dirname = dirname(fileURLToPath(import.meta.url));
const srcDir = join(__dirname, '..');
const skillName = 'qiaomu-music-player-spotify';
const skillDir = join(homedir(), '.claude', 'skills', skillName);

console.log(`\n🎵 Installing ${skillName} for Claude Code...\n`);

// Copy skill files
mkdirSync(skillDir, { recursive: true });

const filesToCopy = ['SKILL.md', 'spotify.py', 'auth_setup.py', '.env.example'];
for (const file of filesToCopy) {
  const src = join(srcDir, file);
  if (existsSync(src)) {
    cpSync(src, join(skillDir, file));
    console.log(`  ✓ ${file}`);
  }
}

// Copy references directory (genre database)
const refsSrc = join(srcDir, 'references');
if (existsSync(refsSrc)) {
  cpSync(refsSrc, join(skillDir, 'references'), { recursive: true });
  console.log('  ✓ references/ (5,947 music genres)');
}

console.log(`
✅ Skill installed to: ${skillDir}

Next steps:
  1. Set environment variables:
     export SPOTIFY_CLIENT_ID="your_client_id"
     export SPOTIFY_CLIENT_SECRET="your_client_secret"

  2. Run OAuth authorization:
     python3 ${skillDir}/auth_setup.py

  3. Restart Claude Code to activate the skill.

Get your Spotify credentials at: https://developer.spotify.com/dashboard
`);
