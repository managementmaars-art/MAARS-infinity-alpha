# kalopilot-sender

Skill untuk Claude AI yang bisa mengirim data TikTok Shop dari KaloPilot ke **WhatsApp** dan/atau **Telegram** secara otomatis terjadwal.

---

## 🎬 Tutorial Video Setup

[![Tonton Tutorial Setup](https://img.youtube.com/vi/19JmnfzTwMw/maxresdefault.jpg)](https://youtu.be/19JmnfzTwMw)

## 📋 Apa yang bisa dilakukan?

- Ambil data TikTok Shop (produk trending, creator, video viral, shop, livestream, kategori) lewat KaloPilot
- Kirim laporan otomatis ke grup WhatsApp dan/atau Telegram
- Bisa diatur jadwal: harian, mingguan, atau bulanan
- Setup mudah — cukup jawab pertanyaan di Claude, tidak perlu edit file apapun

---

## 🖥️ Kompatibel dengan

| Platform | Status |
|----------|--------|
| Claude CLI | ✅ |
| Claude Code | ✅ |
| OpenClaw | ✅ |
| Windows / Mac / Linux | ✅ |

---

## 📦 Kebutuhan Sebelum Install

Pastikan kamu sudah punya:

1. **Node.js** (versi 18 ke atas)
   - Download di: https://nodejs.org → pilih **LTS**
   - Cek sudah terinstall: buka terminal, ketik `node --version`

2. **Akun KaloData** dengan API token
   - Daftar di: https://kalodata.com

3. **Claude CLI atau OpenClaw** terinstall di komputer kamu

---

## 🚀 Cara Install (Langkah demi Langkah)

### Step 1 — Install kalopilot skill (wajib ada dulu)

Buka terminal dan ketik:

```bash
npx skills add https://github.com/sailtonight/kalopilot-skill --skill kalopilot
```

> Kalau muncul pertanyaan "proceed?" → ketik `y` lalu Enter

Setelah selesai, masukkan token KaloPilot kamu. Kalau belum punya token, login ke [kalodata.com](https://www.kalodata.com/explore?tc=adang24) → Settings → API Token.

kalau mau dapet diskon coba masukin kode promo :
Patungan / premium = "DMPREMIUM" diskon 30% 
Bukan Patungan = "Adang24" Diskon 10%

---

### Step 2 — Install kalopilot-sender skill ini

```bash
npx skills add https://github.com/adanghd/sender-kalopilot-skill --skill kalopilot-sender
```

---

### Step 3 — Install dependencies

```bash
node ~/skills/kalopilot-sender/scripts/install.js
```

Script ini akan otomatis:
- Install library WhatsApp yang dibutuhkan
- Install PM2 (untuk jadwal otomatis)
- Siapkan semua file yang diperlukan

---

### Step 4 — Setup di Claude

Buka Claude CLI, Claude Code, atau OpenClaw, lalu ketik:

```
setup sender
```

Claude akan menanyakan:
1. Mau kirim ke WhatsApp, Telegram, atau keduanya?
2. Nama grup WhatsApp / Chat ID Telegram tujuan
3. Data apa yang mau dikirim (produk, video, creator, dll)
4. Region TikTok Shop (ID untuk Indonesia)
5. Jadwal pengiriman (jam berapa, seberapa sering)

Selesai! Data akan terkirim otomatis sesuai jadwal. ✅

---

## 💬 Perintah yang Bisa Digunakan di Claude

Setelah setup selesai, kamu bisa mengetik perintah-perintah ini di Claude:

| Perintah | Fungsi |
|----------|--------|
| `setup sender` | Setup awal atau ubah konfigurasi |
| `kirim sekarang` | Kirim data ke WA/Telegram sekarang juga |
| `ubah jadwal` | Ganti jadwal pengiriman |
| `ubah channel` | Ganti tujuan kirim (WA / Telegram) |
| `stop jadwal` | Hentikan pengiriman otomatis |
| `cek status` | Lihat status dan konfigurasi aktif |

---

## 📊 Data yang Tersedia

| Pilihan | Data |
|---------|------|
| 1 | Produk Trending |
| 2 | Top Shop |
| 3 | Top Creator / Influencer |
| 4 | Video Viral |
| 5 | Livestream Terbaik |
| 6 | Kategori Trending |
| all | Semua data di atas |

---

## 🌏 Region yang Didukung

`ID` `US` `UK` `MY` `TH` `VN` `PH` `SG` `MX` `DE` `IT` `FR` `ES` `BR` `JP`

---

## ❓ Pertanyaan Umum

**Q: Apakah WhatsApp saya aman?**
A: Ya. Skill ini menggunakan library resmi whatsapp-web.js dan sesi tersimpan lokal di komputer kamu. Tidak ada data yang dikirim ke server pihak ketiga.

**Q: Bagaimana cara dapat Telegram bot token?**
A: Buka Telegram → cari @BotFather → ketik `/newbot` → ikuti instruksi → copy token yang diberikan.

**Q: Bagaimana cara dapat Chat ID Telegram?**
A: Tambahkan bot kamu ke grup, lalu ketik `/start` di grup tersebut. Atau cari @userinfobot di Telegram dan forward pesan dari grupmu.

**Q: Apakah bisa kirim ke lebih dari satu grup WA?**
A: Saat ini satu grup WA per config. Untuk multi-grup, jalankan setup ulang dengan grup berbeda.

**Q: Skill ini gratis?**
A: Skill ini gratis. Tapi penggunaan data KaloPilot memerlukan kredit KaloData.

---

## 🔧 Troubleshooting

**QR WhatsApp tidak muncul**
→ Hapus folder `~/.kalopilot/wa-session/` lalu jalankan `setup sender` ulang

**Pesan tidak terkirim ke WA**
→ Pastikan nomor WA kamu masih ada di grup tujuan
→ Coba `kirim sekarang` untuk test manual

**Token KaloPilot invalid**
→ Login ulang ke kalodata.com dan update token di `~/.kalopilot/token`

**PM2 tidak ditemukan**
→ Jalankan: `npm install -g pm2`

---

## 📄 Lisensi

MIT — bebas digunakan dan dimodifikasi.
