const fs = require("fs");

const input = "C:\\Users\\Yaleena Yara\\Desktop\\skills-export\\skills-merged.txt";
const output = "C:\\Users\\Yaleena Yara\\Desktop\\skills-export\\skills-repos-only.txt";

const lines = fs.readFileSync(input, "utf8")
  .split(/\r?\n/)
  .map(x => x.trim())
  .filter(Boolean);

const repos = new Set();

for (const line of lines) {
  const m = line.match(/^npx skills add (https:\/\/github\.com\/[^ ]+)/i);
  if (m) repos.add(`npx skills add ${m[1]}`);
}

const out = Array.from(repos).sort();
fs.writeFileSync(output, out.join("\n"), "utf8");

console.log(`Input commands: ${lines.length}`);
console.log(`Unique repos: ${out.length}`);
console.log(`Wrote: ${output}`);
