import fs from "node:fs/promises";
import path from "node:path";

export async function ensureDir(targetPath) {
  await fs.mkdir(targetPath, { recursive: true });
}

export async function pathExists(targetPath) {
  try {
    await fs.access(targetPath);
    return true;
  } catch {
    return false;
  }
}

export async function writeTextFile(filePath, contents) {
  const dir = path.dirname(filePath);
  await ensureDir(dir);
  await fs.writeFile(filePath, contents, "utf8");
}

export async function writeJsonFile(filePath, payload) {
  const dir = path.dirname(filePath);
  await ensureDir(dir);
  await fs.writeFile(filePath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
}

export function countLines(text) {
  if (!text) {
    return 0;
  }
  return text.split(/\r?\n/).length;
}

export function formatDate(dateInput) {
  if (!dateInput || dateInput === "unknown") return "unknown";
  const d = new Date(dateInput);
  if (isNaN(d.getTime())) return dateInput;

  const offsetMinutes = -d.getTimezoneOffset();
  const offsetHours = Math.floor(Math.abs(offsetMinutes) / 60);
  const offsetMins = Math.abs(offsetMinutes) % 60;
  const sign = offsetMinutes >= 0 ? "+" : "-";

  const pad = (n) => String(n).padStart(2, "0");
  const year = d.getFullYear();
  const month = pad(d.getMonth() + 1);
  const day = pad(d.getDate());
  const hours = pad(d.getHours());
  const minutes = pad(d.getMinutes());
  const seconds = pad(d.getSeconds());
  const milliseconds = String(d.getMilliseconds()).padStart(3, "0");
  const offset = `${sign}${pad(offsetHours)}:${pad(offsetMins)}`;

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}.${milliseconds} ${offset}`;
}

export function getTimestampPrefix() {
  const now = new Date();
  const pad = (n) => String(n).padStart(2, "0");
  return (
    now.getFullYear() +
    pad(now.getMonth() + 1) +
    pad(now.getDate()) +
    "-" +
    pad(now.getHours()) +
    pad(now.getMinutes()) +
    pad(now.getSeconds())
  );
}
