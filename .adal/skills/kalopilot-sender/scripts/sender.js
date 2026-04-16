/**
 * KaloPilot Sender — Main Scheduler
 * Fetches data from KaloPilot API and sends to configured channels (WA and/or Telegram)
 *
 * Config: ~/.kalopilot/sender-config.json
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { spawnSync } = require('child_process');

const HOME          = os.homedir();
const BASE_DIR      = path.join(HOME, '.kalopilot');
const CONFIG_FILE   = path.join(BASE_DIR, 'sender-config.json');
const TOKEN_FILE    = path.join(BASE_DIR, 'token');
const WA_PENDING    = path.join(BASE_DIR, 'wa-pending.json');
const TG_PENDING    = path.join(BASE_DIR, 'tg-pending.json');
const WA_SEND       = path.join(BASE_DIR, 'wa-send.js');
const TG_SEND       = path.join(BASE_DIR, 'tg-send.js');

// Query templates per data type
const QUERIES = {
    products:    (r, p) => `Top 10 produk trending TikTok Shop ${r} ${p}, urutkan berdasarkan revenue. Tampilkan nama, revenue, unit terjual, harga, komisi.`,
    shops:       (r, p) => `Top 10 shop TikTok Shop ${r} ${p} berdasarkan revenue. Tampilkan nama toko, revenue, jumlah produk.`,
    creators:    (r, p) => `Top 10 creator TikTok Shop ${r} ${p} berdasarkan GMV. Tampilkan nama, GMV, followers, engagement rate.`,
    videos:      (r, p) => `Top 10 video viral TikTok Shop ${r} ${p} berdasarkan views dan konversi. Tampilkan creator, views, revenue, link video.`,
    livestreams: (r, p) => `Top 10 livestream TikTok Shop ${r} ${p} berdasarkan revenue. Tampilkan nama, revenue, jumlah penonton.`,
    categories:  (r, p) => `Kategori trending TikTok Shop ${r} ${p}, tampilkan market size, growth, dan kompetisi.`,
};

const LABELS = {
    products:    '🛒 PRODUK TRENDING',
    shops:       '🏪 TOP SHOP',
    creators:    '👤 TOP CREATOR',
    videos:      '🎥 VIDEO VIRAL',
    livestreams: '📺 LIVESTREAM TERBAIK',
    categories:  '📂 KATEGORI TRENDING',
};

function periodLabel(frequency) {
    if (frequency === 'daily')  return 'hari ini';
    if (frequency === 'weekly') return '7 hari terakhir';
    return '30 hari terakhir';
}

function callKalopilot(query, token) {
    return new Promise((resolve, reject) => {
        const body = JSON.stringify({ query });
        const req = https.request({
            hostname: 'staging.kalodata.com',
            path: '/api/pilot/skill/ext/v1/chat/sync',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'Content-Length': Buffer.byteLength(body),
            },
            timeout: 600000,
        }, res => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (e) { reject(new Error('Invalid JSON response')); }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('Request timeout (10 min)')); });
        req.write(body);
        req.end();
    });
}

async function main() {
    if (!fs.existsSync(CONFIG_FILE)) {
        console.error('❌ Config tidak ditemukan. Setup dulu di Claude: "setup sender"');
        process.exit(1);
    }
    if (!fs.existsSync(TOKEN_FILE)) {
        console.error('❌ Token KaloPilot tidak ditemukan di ~/.kalopilot/token');
        process.exit(1);
    }

    const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
    const token  = fs.readFileSync(TOKEN_FILE, 'utf8').trim();
    const { channels, whatsapp, telegram, region, dataTypes, schedule } = config;
    const period = periodLabel(schedule.frequency);

    const today = new Date().toLocaleDateString('id-ID', {
        weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
    });

    console.log(`\n🚀 KaloPilot Sender — ${today}`);
    console.log(`📌 Channel: ${channels.join(', ')} | Region: ${region} | Data: ${dataTypes.join(', ')}\n`);

    const sections = [];

    for (const type of dataTypes) {
        if (!QUERIES[type]) continue;
        const query = QUERIES[type](region, period);
        console.log(`🔍 Fetching ${type}...`);
        try {
            const res = await callKalopilot(query, token);
            if (res.message && !res.text) {
                console.error(`  ❌ API error: ${res.message}`);
                continue;
            }
            let content = (res.text || '').trim();
            if (res.report) content += '\n\n' + res.report.trim();
            if (content) {
                let section = `*${LABELS[type]}*\n${content}`;
                if (res.report_url) section += `\n\n📊 Laporan lengkap: ${res.report_url}`;
                sections.push(section);
                console.log(`  ✅ OK`);
            }
        } catch (err) {
            console.error(`  ❌ Gagal: ${err.message}`);
        }
    }

    if (sections.length === 0) {
        console.error('\n❌ Tidak ada data yang berhasil diambil.');
        process.exit(1);
    }

    const message = `📊 *LAPORAN TIKTOK SHOP ${region}*\n📅 ${today}\n\n` +
        sections.join('\n\n━━━━━━━━━━━━━━━━━━━\n\n') +
        `\n\n_Data: KaloData | ${today}_`;

    let allSuccess = true;

    // Kirim ke WhatsApp
    if (channels.includes('whatsapp') && whatsapp?.groupName) {
        console.log('\n📱 Mengirim ke WhatsApp...');
        fs.writeFileSync(WA_PENDING, JSON.stringify({ groupName: whatsapp.groupName, message }, null, 2));
        const result = spawnSync('node', [WA_SEND], { stdio: 'inherit', timeout: 180000 });
        if (result.status !== 0) {
            console.error('❌ Gagal kirim ke WhatsApp');
            allSuccess = false;
        }
    }

    // Kirim ke Telegram
    if (channels.includes('telegram') && telegram?.chatId) {
        console.log('\n✈️  Mengirim ke Telegram...');
        fs.writeFileSync(TG_PENDING, JSON.stringify({ message }, null, 2));
        const result = spawnSync('node', [TG_SEND], { stdio: 'inherit', timeout: 30000 });
        if (result.status !== 0) {
            console.error('❌ Gagal kirim ke Telegram');
            allSuccess = false;
        }
    }

    console.log(allSuccess ? '\n✅ Selesai!' : '\n⚠️  Selesai dengan error.');
    process.exit(allSuccess ? 0 : 1);
}

main().catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
});
