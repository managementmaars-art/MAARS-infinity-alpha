---
name: kalopilot-sender
description: Kirim data TikTok Shop dari KaloPilot ke WhatsApp dan/atau Telegram secara terjadwal. Gunakan skill ini ketika user ingin setup pengiriman otomatis data kalopilot ke WA atau Telegram, mengubah jadwal, mengirim data sekarang, atau mengelola konfigurasi sender.
---

# KaloPilot Sender — Kirim Data TikTok Shop ke WA & Telegram

Skill ini mengirim data TikTok Shop dari KaloPilot ke WhatsApp dan/atau Telegram secara otomatis terjadwal.

## Prerequisites

Skill ini membutuhkan **kalopilot skill** terinstall terlebih dahulu:
```bash
npx skills add https://github.com/sailtonight/kalopilot-skill --skill kalopilot
```

## Data Directory

Semua runtime files disimpan di `~/.kalopilot/`:
- `sender-config.json` — konfigurasi sender (channel, jadwal, data)
- `wa-session/` — WhatsApp session (auto-created saat setup)
- `wa-pending.json` — antrian pesan sementara

## Install Dependencies

Sebelum pertama kali digunakan, jalankan:
```bash
node <skill-path>/scripts/install.js
```

Script ini akan:
- Install npm packages yang dibutuhkan (whatsapp-web.js, qrcode, dll)
- Copy script runtime ke `~/.kalopilot/`
- Install PM2 secara global jika belum ada

## Setup & Konfigurasi

### Cek konfigurasi existing
Sebelum setup, selalu cek apakah `~/.kalopilot/sender-config.json` sudah ada.
- Jika **sudah ada**: tanya user mau update bagian mana (channel, jadwal, atau data)
- Jika **belum ada**: jalankan setup lengkap dari awal

### Alur Setup (dari awal)

**Step 1 — Pilih channel**
Tanya user:
```
Mau kirim data ke mana?
  [1] WhatsApp saja
  [2] Telegram saja
  [3] WhatsApp + Telegram (keduanya)
```

**Step 2a — Setup WhatsApp** (jika pilih 1 atau 3)

Cek apakah `~/.kalopilot/wa-session/` sudah ada:
- Jika **sudah ada**: skip QR, konfirmasi ke user "Sesi WA sudah tersimpan ✅"
- Jika **belum ada**: jalankan `node ~/.kalopilot/wa-send.js` untuk scan QR

Tanya nama grup WhatsApp tujuan.

**Step 2b — Setup Telegram** (jika pilih 2 atau 3)

Cek apakah `~/.kalopilot/telegram.json` sudah ada:
- Jika **sudah ada**: tanya user mau pakai config existing atau input baru
- Jika **belum ada**: minta input:
  - Bot token (dari @BotFather)
  - Chat ID grup/channel tujuan

Simpan ke `~/.kalopilot/telegram.json`:
```json
{
  "botToken": "",
  "chatId": ""
}
```
**JANGAN timpa file yang sudah ada tanpa konfirmasi user.**

**Step 3 — Pilih data**
```
Data yang tersedia:
  [1] Produk Trending
  [2] Top Shop
  [3] Top Creator/Influencer
  [4] Video Viral
  [5] Livestream Terbaik
  [6] Kategori Trending
  [all] Semua data
```

**Step 4 — Region**
Tanya region: ID, US, UK, MY, TH, VN, PH, SG (default: ID)

**Step 5 — Jadwal**
```
Frekuensi:
  [1] Setiap hari
  [2] Setiap minggu
  [3] Setiap bulan
```
Tanya jam pengiriman (contoh: 19:00)

**Step 6 — Simpan & Aktifkan**

Simpan ke `~/.kalopilot/sender-config.json`:
```json
{
  "channels": [],
  "whatsapp": {
    "groupName": ""
  },
  "telegram": {
    "chatId": ""
  },
  "region": "ID",
  "dataTypes": [],
  "schedule": {
    "frequency": "daily",
    "time": "19:00",
    "cronExpr": "0 19 * * *"
  }
}
```

Setup PM2 cron:
```bash
pm2 delete kalopilot-sender 2>/dev/null; pm2 start ~/.kalopilot/sender.js --name kalopilot-sender --cron "<cronExpr>" --no-autorestart && pm2 save
```

## Perintah yang Dikenali

| User berkata | Aksi |
|---|---|
| "setup sender" / "setup kirim" | Jalankan setup lengkap |
| "kirim sekarang" | Fetch data + kirim langsung tanpa jadwal |
| "ubah jadwal" | Update schedule di config + restart PM2 |
| "ubah channel" | Update channels di config |
| "stop jadwal" | `pm2 delete kalopilot-sender` |
| "cek status" | `pm2 status` + tampilkan config aktif |

## Kirim Data Sekarang (Manual)

Jalankan scheduler secara langsung:
```bash
node ~/.kalopilot/sender.js
```

## Fetch Data dari KaloPilot

Gunakan `pilot.sh` dari kalopilot skill untuk fetch data:
```bash
bash ~/skills/kalopilot/scripts/pilot.sh query "<query>"
bash ~/skills/kalopilot/scripts/pilot.sh status
bash ~/skills/kalopilot/scripts/pilot.sh result
```

Query templates per data type (ganti `{REGION}` dan `{PERIOD}`):
- **products**: `Top 10 produk trending TikTok Shop {REGION} {PERIOD}, urutkan berdasarkan revenue. Tampilkan nama, revenue, unit, harga, komisi.`
- **shops**: `Top 10 shop TikTok Shop {REGION} {PERIOD} berdasarkan revenue.`
- **creators**: `Top 10 creator TikTok Shop {REGION} {PERIOD} berdasarkan GMV. Tampilkan nama, GMV, followers, engagement rate.`
- **videos**: `Top 10 video viral TikTok Shop {REGION} {PERIOD} berdasarkan views dan konversi. Tampilkan creator, views, revenue, link.`
- **livestreams**: `Top 10 livestream TikTok Shop {REGION} {PERIOD} berdasarkan revenue.`
- **categories**: `Kategori trending TikTok Shop {REGION} {PERIOD}, tampilkan market size dan growth.`

Period labels: daily=`hari ini`, weekly=`7 hari terakhir`, monthly=`30 hari terakhir`

## Format Pesan

Format pesan WA/Telegram:
```
🔥 *[LABEL DATA] TIKTOK SHOP {REGION}*
📅 {tanggal}

{isi dari KaloPilot text + report}

📊 Laporan lengkap: {report_url}

_Data: KaloData | {tanggal}_
```

## Rules

- **JANGAN** hardcode token, bot token, atau credentials apapun
- Selalu cek config existing sebelum overwrite
- Jika kalopilot skill tidak ditemukan di `~/skills/kalopilot/`, minta user install dulu
- Jika token `~/.kalopilot/token` tidak ada, minta user setup kalopilot skill dulu
