const fs = require("fs");
const { chromium } = require("playwright");

const MAX_RANK = parseInt(process.argv[2] || "9788", 10);

function uniqBy(items, keyFn) {
  const seen = new Set();
  const out = [];
  for (const item of items) {
    const k = keyFn(item);
    if (!seen.has(k)) {
      seen.add(k);
      out.push(item);
    }
  }
  return out;
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 2200 } });

  await page.goto("https://skills.sh/", { waitUntil: "domcontentloaded", timeout: 120000 });
  await page.waitForTimeout(3000);

  let lastCount = 0;
  let stableRounds = 0;

  for (let i = 0; i < 500; i++) {
    const entries = await page.evaluate(() => {
      const bodyText = document.body.innerText || "";
      const lines = bodyText
        .split(/\r?\n/)
        .map(s => s.trim())
        .filter(Boolean);

      const out = [];

      for (let idx = 0; idx < lines.length - 2; idx++) {
        const rank = lines[idx];
        const skill = lines[idx + 1];
        const repo = lines[idx + 2];

        if (/^\d+$/.test(rank) && repo.includes("/") && !repo.startsWith("http")) {
          out.push({
            rank: parseInt(rank, 10),
            skill,
            repo
          });
        }
      }

      return out;
    });

    const filtered = uniqBy(
      entries.filter(e =>
        Number.isInteger(e.rank) &&
        e.rank >= 1 &&
        e.rank <= MAX_RANK &&
        /^[A-Za-z0-9._-]+\/[A-Za-z0-9._-]+$/.test(e.repo)
      ),
      e => `${e.rank}|${e.repo}|${e.skill}`
    );

    if (filtered.length === lastCount) {
      stableRounds += 1;
    } else {
      stableRounds = 0;
      lastCount = filtered.length;
    }

    const hasTarget = filtered.some(e => e.rank === MAX_RANK);
    if (hasTarget || stableRounds >= 8) {
      fs.writeFileSync("skills-top.json", JSON.stringify(filtered.sort((a, b) => a.rank - b.rank), null, 2));
      break;
    }

    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1800);
  }

  await browser.close();
})();
