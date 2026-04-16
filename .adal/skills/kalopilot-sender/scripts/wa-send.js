/**
 * KaloPilot Sender — WhatsApp Send Script
 * Reads ~/.kalopilot/wa-pending.json and sends to WhatsApp group
 *
 * Usage:
 *   node wa-send.js                    → send from wa-pending.json
 *   node wa-send.js --list-groups      → list all WA groups
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const QRCode = require('qrcode');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const HOME        = os.homedir();
const BASE_DIR    = path.join(HOME, '.kalopilot');
const SESSION_DIR = path.join(BASE_DIR, 'wa-session');
const MSG_FILE    = path.join(BASE_DIR, 'wa-pending.json');
const QR_HTML     = path.join(BASE_DIR, 'qr.html');
const LIST_MODE   = process.argv.includes('--list-groups');

let browserOpened = false;

async function showQRInBrowser(qr) {
    const dataUrl = await QRCode.toDataURL(qr, { width: 300 });
    const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Scan WA QR Code</title>
  <style>
    body { font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; background: #f0f0f0; }
    .card { background: white; padding: 32px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); text-align: center; }
    h2 { color: #128C7E; margin-bottom: 4px; }
    p { color: #666; font-size: 14px; margin-top: 4px; }
    img { margin: 16px 0; display: block; }
    .badge { background: #25D366; color: white; padding: 6px 14px; border-radius: 20px; font-size: 13px; }
  </style>
</head>
<body>
  <div class="card">
    <h2>WhatsApp QR Code</h2>
    <p>Scan dengan WhatsApp kamu</p>
    <img src="${dataUrl}" />
    <br>
    <span class="badge">QR berlaku ~20 detik — refresh jika expired</span>
  </div>
</body>
</html>`;
    fs.writeFileSync(QR_HTML, html);
    if (!browserOpened) {
        // Cross-platform open browser
        const openCmd = process.platform === 'win32' ? `start "" "${QR_HTML}"`
                      : process.platform === 'darwin' ? `open "${QR_HTML}"`
                      : `xdg-open "${QR_HTML}"`;
        exec(openCmd);
        browserOpened = true;
        console.log('🌐 Browser dibuka dengan QR code.');
    } else {
        console.log('🔄 QR diperbarui — refresh browser kamu.');
    }
}

function clearChromeLocks() {
    const lockFiles = ['SingletonLock', 'SingletonCookie', 'SingletonSocket'];
    const sessionPath = path.join(SESSION_DIR, 'session');
    for (const f of lockFiles) {
        const p = path.join(sessionPath, f);
        if (fs.existsSync(p)) {
            try { fs.unlinkSync(p); } catch {}
        }
    }
}

const client = new Client({
    authStrategy: new LocalAuth({ dataPath: SESSION_DIR }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
        protocolTimeout: 120000
    }
});

client.on('qr', (qr) => { showQRInBrowser(qr); });

client.on('authenticated', () => {
    console.log('✅ Authenticated! Sesi tersimpan.');
    if (fs.existsSync(QR_HTML)) fs.unlinkSync(QR_HTML);
});

client.on('ready', async () => {
    console.log('✅ WhatsApp siap!');
    await new Promise(r => setTimeout(r, 3000));

    if (LIST_MODE) {
        const chats = await client.getChats();
        const groups = chats.filter(c => c.isGroup);
        console.log('\n=== DAFTAR WA GROUP ===');
        groups.forEach((g, i) => console.log(`[${i}] ${g.name} (${g.id._serialized})`));
        console.log('======================\n');
        await client.destroy();
        process.exit(0);
        return;
    }

    if (!fs.existsSync(MSG_FILE)) {
        console.log('ℹ️  Tidak ada pesan pending.');
        await client.destroy();
        process.exit(0);
        return;
    }

    const { groupName, message } = JSON.parse(fs.readFileSync(MSG_FILE, 'utf8'));
    const success = await sendToGroup(groupName, message);
    if (success) {
        fs.unlinkSync(MSG_FILE);
        await new Promise(r => setTimeout(r, 5000));
    }
    await client.destroy();
    process.exit(success ? 0 : 1);
});

async function sendToGroup(groupName, message) {
    const chats = await client.getChats();
    const group = chats.find(c => c.isGroup && c.name.toLowerCase().includes(groupName.toLowerCase()));
    if (!group) {
        console.error(`❌ Group "${groupName}" tidak ditemukan.`);
        const groups = chats.filter(c => c.isGroup);
        console.log('Grup tersedia:', groups.map(g => g.name).join(', '));
        return false;
    }
    console.log(`📤 Mengirim ke: "${group.name}"`);
    const delay = Math.floor(Math.random() * 4000) + 3000;
    await new Promise(r => setTimeout(r, delay));
    try {
        await group.sendMessage(message);
        console.log(`✅ Pesan terkirim ke "${group.name}"`);
        return true;
    } catch (err) {
        console.error(`❌ Gagal kirim:`, err.message);
        return false;
    }
}

client.on('auth_failure', () => {
    console.error('❌ Auth gagal. Hapus folder wa-session dan coba lagi.');
    process.exit(1);
});

clearChromeLocks();
client.initialize();
