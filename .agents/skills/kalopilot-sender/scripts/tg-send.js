/**
 * KaloPilot Sender — Telegram Send Script
 * Reads ~/.kalopilot/tg-pending.json and sends to Telegram chat
 *
 * Config: ~/.kalopilot/telegram.json
 * {
 *   "botToken": "",
 *   "chatId": ""
 * }
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');

const HOME       = os.homedir();
const BASE_DIR   = path.join(HOME, '.kalopilot');
const TG_CONFIG  = path.join(BASE_DIR, 'telegram.json');
const MSG_FILE   = path.join(BASE_DIR, 'tg-pending.json');

function sendTelegram(botToken, chatId, message) {
    return new Promise((resolve, reject) => {
        const body = JSON.stringify({
            chat_id: chatId,
            text: message,
            parse_mode: 'Markdown',
            disable_web_page_preview: false
        });
        const req = https.request({
            hostname: 'api.telegram.org',
            path: `/bot${botToken}/sendMessage`,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(body)
            }
        }, res => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const result = JSON.parse(data);
                    if (result.ok) {
                        resolve(result);
                    } else {
                        reject(new Error(result.description || 'Telegram API error'));
                    }
                } catch (e) {
                    reject(new Error('Invalid response: ' + data.slice(0, 100)));
                }
            });
        });
        req.on('error', reject);
        req.write(body);
        req.end();
    });
}

async function main() {
    if (!fs.existsSync(TG_CONFIG)) {
        console.error('❌ Telegram config tidak ditemukan di ~/.kalopilot/telegram.json');
        process.exit(1);
    }
    if (!fs.existsSync(MSG_FILE)) {
        console.log('ℹ️  Tidak ada pesan pending untuk Telegram.');
        process.exit(0);
    }

    const { botToken, chatId } = JSON.parse(fs.readFileSync(TG_CONFIG, 'utf8'));
    const { message } = JSON.parse(fs.readFileSync(MSG_FILE, 'utf8'));

    if (!botToken || !chatId) {
        console.error('❌ botToken atau chatId kosong di telegram.json');
        process.exit(1);
    }

    console.log(`📤 Mengirim ke Telegram (chat: ${chatId})...`);
    try {
        await sendTelegram(botToken, chatId, message);
        console.log('✅ Pesan terkirim ke Telegram!');
        fs.unlinkSync(MSG_FILE);
        process.exit(0);
    } catch (err) {
        console.error('❌ Gagal kirim Telegram:', err.message);
        process.exit(1);
    }
}

main();
