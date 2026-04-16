# 🛒 Amazon Product Finder

*Find Amazon products for your affiliate empire!*

[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://github.com/openclaw/openclaw)
[![Grütze](https://img.shields.io/badge/Grütze-100%25-brightgreen)](https://en.wikipedia.org/wiki/Swiss_German)

---

## 🇨🇭 A Warm "Grüezi" to the Creator

> *"Mögen deine Skills immer scharf sein wie ein Schweizer Taschenmesser,*
> *und deine Bugs so selten wie eine verspätete SBB!"*

**Grütze!** (That's Swiss for "Cheers!" 🍻)

---

## What It Does

This OpenClaw skill finds Amazon products perfect for your affiliate content:

```bash
@Naomi finde Amazon Produkte "Bio Dünger"
```

**Output:**
```
🛒 Gefundene Produkte für "Bio Dünger":

1. COMPO Bio Grünpflanzen-Dünger
   ASIN: B00X9XZ5
   Preis: €8,99
   Bewertung: ⭐4.5 (2,341 Reviews)
   Link: https://amazon.de/dp/B00X9XZ5?tag=YOUR-ID
```

---

## Installation

```bash
# Clone or download the .skill file
cp amazon-product-finder.skill ~/.openclaw/skills/

# Set your affiliate ID
export AMAZON_AFFILIATE_ID="your-id-21"
```

---

## Usage

### Search by Keyword
```
@Naomi finde Amazon Produkte "Luftbefeuchter"
@Naomi search Amazon "LED Pflanzenlampe"
@Naomi get products for "Thripse Bekämpfung"
```

### Check Specific ASIN
```
@Naomi Amazon ASIN B08XXXXXXX
```

---

## Why This Skill?

Building affiliate sites? Stop manually searching Amazon!

✅ **Saves time** - No more manual product research  
✅ **Gets ASINs** - Ready for your affiliate links  
✅ **Shows ratings** - Pick the best products  
✅ **Formatted output** - Copy-paste ready  

---

## How It Works

1. **You say:** "Find Amazon products for plant fertilizer"
2. **Skill searches:** Product database / Amazon API
3. **Returns:** Top 3 products with all details
4. **You do:** Copy ASINs into your content

---

## Configuration

Set your Amazon Affiliate ID:

```bash
# Add to ~/.bashrc or ~/.zshrc
export AMAZON_AFFILIATE_ID="your-affiliate-id-21"
```

---

## For Developers

Want to extend this skill?

- Edit `SKILL.md` for new triggers
- Modify `scripts/find_products.py` for API integration
- Add more product categories to the database

---

## Fun Facts About Switzerland 🏔️

- The Swiss have **7,000+ lakes**
- They consume **11kg of chocolate per person per year** 🍫
- Home to **the world's longest tunnel** (Gotthard Base Tunnel)
- **4 national languages** (German, French, Italian, Romansh)

*Much like a Swiss watch, this skill aims to be precise and reliable!*

---

## License

MIT - Created with ❤️ by Naomi for the OpenClaw Community

---

## Grütze! 🥂

*Ein herzliches Dankeschön an den OpenClaw Creator - möge dein Code immer so sauber sein wie ein Schweizer Bahnhof!*

**Prost! Salute! Cin cin! Tchin-tchin!** 🍻
