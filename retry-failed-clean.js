const fs = require("fs");
const path = require("path");

const failedFile = path.join(process.cwd(), "skills-installed-failed.txt");
const logDir = process.cwd();

if (!fs.existsSync(failedFile)) {
  console.error("Missing skills-installed-failed.txt");
  process.exit(1);
}

const failedCommands = fs.readFileSync(failedFile, "utf8")
  .split(/\r?\n/)
  .map(x => x.trim())
  .filter(Boolean);

function shouldRetry(log) {
  // ❌ skip permanent failures
  if (/No skills found/i.test(log)) return false;
  if (/No valid skills found/i.test(log)) return false;
  if (/Authentication failed/i.test(log)) return false;
  if (/invalid path/i.test(log)) return false;
  if (/Filename too long/i.test(log)) return false;

  // ✅ retry these
  if (/Failed to clone repository/i.test(log)) return true;
  if (/Cloning repository/i.test(log)) return true;
  if (/timeout/i.test(log)) return true;

  return true; // fallback: retry unknown failures
}

const retryList = [];

failedCommands.forEach((cmd, i) => {
  const logFile = path.join(logDir, `failed-${i + 1}.log`);

  if (!fs.existsSync(logFile)) return;

  const log = fs.readFileSync(logFile, "utf8");

  if (shouldRetry(log)) {
    retryList.push(cmd);
  }
});

const outputFile = path.join(process.cwd(), "retry-commands.txt");
fs.writeFileSync(outputFile, retryList.join("\n"), "utf8");

console.log("Total failed:", failedCommands.length);
console.log("Retryable:", retryList.length);
console.log("Saved to retry-commands.txt");