/**
 * KaloPilot Sender — Install Script
 * Installs dependencies and copies runtime scripts to ~/.kalopilot/
 */

const { execSync, spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const HOME = process.env.HOME || process.env.USERPROFILE;
const KALOPILOT_DIR = path.join(HOME, '.kalopilot');
const SKILL_SCRIPTS = path.join(__dirname);

function log(msg) { console.log(msg); }
function ok(msg)  { console.log(`✅ ${msg}`); }
function err(msg) { console.error(`❌ ${msg}`); }
function info(msg){ console.log(`   ${msg}`); }

// Files to copy from skill/scripts → ~/.kalopilot/
const RUNTIME_FILES = ['wa-send.js', 'tg-send.js', 'sender.js'];

function ensureDir(dir) {
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
        ok(`Created ${dir}`);
    }
}

function copyIfNotExists(src, dest) {
    if (fs.existsSync(dest)) {
        info(`Skip (already exists): ${path.basename(dest)}`);
    } else {
        fs.copyFileSync(src, dest);
        ok(`Copied: ${path.basename(dest)}`);
    }
}

function checkCommand(cmd) {
    try {
        execSync(`${cmd} --version`, { stdio: 'ignore' });
        return true;
    } catch {
        return false;
    }
}

function main() {
    log('\n🚀 KaloPilot Sender — Installing...\n');

    // 1. Ensure ~/.kalopilot exists
    ensureDir(KALOPILOT_DIR);

    // 2. Check Node.js
    if (!checkCommand('node')) {
        err('Node.js tidak ditemukan. Install dari https://nodejs.org');
        process.exit(1);
    }
    ok('Node.js tersedia');

    // 3. Check kalopilot skill
    const kalopilotSkill = path.join(HOME, 'skills', 'kalopilot');
    if (!fs.existsSync(kalopilotSkill)) {
        err('kalopilot skill tidak ditemukan!');
        info('Install dulu: npx skills add https://github.com/sailtonight/kalopilot-skill --skill kalopilot');
        process.exit(1);
    }
    ok('kalopilot skill ditemukan');

    // 4. Check KaloPilot token
    const tokenFile = path.join(KALOPILOT_DIR, 'token');
    if (!fs.existsSync(tokenFile)) {
        err('Token KaloPilot tidak ditemukan di ~/.kalopilot/token');
        info('Setup kalopilot skill dulu dan masukkan token kamu.');
        process.exit(1);
    }
    ok('Token KaloPilot ditemukan');

    // 5. Copy runtime scripts (skip if already exists — don't overwrite)
    log('\n📄 Copying runtime scripts...');
    for (const file of RUNTIME_FILES) {
        const src = path.join(SKILL_SCRIPTS, file);
        const dest = path.join(KALOPILOT_DIR, file);
        if (fs.existsSync(src)) {
            copyIfNotExists(src, dest);
        } else {
            err(`Script tidak ditemukan: ${file}`);
        }
    }

    // 6. Install npm packages
    log('\n📦 Installing npm packages...');
    const pkgFile = path.join(HOME, 'package.json');
    const nodeModules = path.join(HOME, 'node_modules');

    const requiredPkgs = ['whatsapp-web.js', 'qrcode'];
    const missingPkgs = requiredPkgs.filter(pkg => {
        return !fs.existsSync(path.join(nodeModules, pkg));
    });

    if (missingPkgs.length > 0) {
        log(`   Installing: ${missingPkgs.join(', ')}`);
        const result = spawnSync('npm', ['install', '--prefix', HOME, ...missingPkgs], {
            stdio: 'inherit',
            cwd: HOME
        });
        if (result.status !== 0) {
            err('npm install gagal');
            process.exit(1);
        }
        ok('npm packages installed');
    } else {
        ok('npm packages sudah tersedia');
    }

    // 7. Check/install PM2
    log('\n⚙️  Checking PM2...');
    if (!checkCommand('pm2')) {
        log('   Installing PM2 globally...');
        const result = spawnSync('npm', ['install', '-g', 'pm2'], { stdio: 'inherit' });
        if (result.status !== 0) {
            err('Gagal install PM2. Coba manual: npm install -g pm2');
        } else {
            ok('PM2 installed');
        }
    } else {
        ok('PM2 sudah tersedia');
    }

    log('\n================================================');
    log('✅ Instalasi selesai!');
    log('');
    log('Langkah selanjutnya:');
    log('  Di Claude: ketik "setup sender" untuk mulai konfigurasi');
    log('================================================\n');
}

main();
