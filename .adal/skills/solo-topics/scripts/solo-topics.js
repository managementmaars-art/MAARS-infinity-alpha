#!/usr/bin/env node

/**
 * mixdao 专题 API：topics / articles / add（Markdown → 自动拼 JSON POST）。
 * 环境：MIXDAO_API_KEY 或 API_KEY；BASE_URL 可选。详见 `references/api-details.md` 或运行无参/--help。
 */

import { createHash } from "crypto";
import { readFileSync, existsSync } from "fs";

/** 正文 SHA-256 十六进制截取长度，用作请求体里的 `id` */
const SHORT_HASH_HEX_LEN = 12;

const apiKey = process.env.MIXDAO_API_KEY || process.env.API_KEY || "";
const baseUrl = (process.env.BASE_URL || "https://www.mixdao.world").replace(
  /\/$/,
  ""
);

const CMD = "node scripts/solo-topics.js";

function printJson(data, compact) {
  console.log(compact ? JSON.stringify(data) : JSON.stringify(data, null, 2));
}

function usage(exitCode = 0) {
  console.log(`用法（在含 SKILL.md 的 skill 根下执行 ${CMD}，或 node 指向本脚本）:

  ${CMD} [--compact] topics
  ${CMD} [--compact] articles [TOPIC_ID]
  ${CMD} [--compact] add TOPIC_ID <FILE.md | ->

  --compact   单行 JSON，减少输出体积
  add         Markdown 文件或 -（stdin）；自动拼 JSON：id=正文 SHA256 前 ${SHORT_HASH_HEX_LEN} 位 hex、date=本地 YYYY-MM-DD 等
  路径相对当前工作目录

环境变量: MIXDAO_API_KEY 或 API_KEY（必填）, BASE_URL（可选）, TOPIC_ID（articles 省略参数时用）
详细说明（相对 skill 根）: references/api-details.md`);
  process.exit(exitCode);
}

function die(msg) {
  console.error(msg);
  process.exit(1);
}

function contentShortId(md) {
  const hex = createHash("sha256").update(md, "utf8").digest("hex");
  return hex.slice(0, SHORT_HASH_HEX_LEN);
}

/** 本地时区日历日期 YYYY-MM-DD */
function localDateYmd() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** 优先第一个一级标题 # ，否则第一行非空文本 */
function titleFromMarkdown(md) {
  const h = md.match(/^#\s+(.+)$/m);
  if (h) return h[1].trim();
  const line = md.split(/\r?\n/).find((l) => l.trim().length > 0);
  return line ? line.trim().slice(0, 500) : "";
}

/** 去掉首个 # 标题行后取一段纯文本摘要 */
function summaryFromMarkdown(md) {
  let rest = md.replace(/^#\s+.+$/m, "").trim();
  if (!rest) rest = md.trim();
  const plain = rest
    .replace(/```[\s\S]*?```/g, " ")
    .replace(/\[([^\]]*)]\([^)]*\)/g, "$1")
    .replace(/[#*_`>|]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  return plain.slice(0, 280);
}

function bodyFromMarkdown(md) {
  const trimmed = md.replace(/^\uFEFF/, "");
  if (!trimmed.trim()) die("Markdown 正文为空");
  const title = titleFromMarkdown(trimmed);
  if (!title) die("无法从 Markdown 推断标题：请写 # 标题 或至少一行非空正文");
  const id = contentShortId(trimmed);
  const date = localDateYmd();
  const summary = summaryFromMarkdown(trimmed) || title.slice(0, 200);
  return {
    id,
    title,
    content: trimmed,
    date,
    summary,
    url: `https://article.local/md/${id}`,
    source: "markdown-cli",
    sortOrder: 0,
  };
}

function readMarkdown(fileArg) {
  let raw;
  if (fileArg === "-") {
    raw = readFileSync(0, "utf8");
  } else {
    if (!existsSync(fileArg)) die(`找不到文件: ${fileArg}`);
    raw = readFileSync(fileArg, "utf8");
  }
  return bodyFromMarkdown(raw);
}

async function parseJsonResponse(res) {
  const text = await res.text();
  let data;
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    die(`非 JSON 响应 (HTTP ${res.status})`);
  }
  if (data && typeof data.error === "string") {
    die(`错误: ${data.error}`);
  }
  if (!res.ok) {
    die(`HTTP ${res.status}${data ? ` ${JSON.stringify(data)}` : ""}`);
  }
  return data;
}

function authHeaders(extra = {}) {
  return {
    Authorization: `Bearer ${apiKey}`,
    Accept: "application/json",
    ...extra,
  };
}

async function getTopics(compact) {
  const res = await fetch(`${baseUrl}/api/topics`, {
    headers: authHeaders(),
  });
  const data = await parseJsonResponse(res);
  printJson(data, compact);
}

async function getArticles(topicId, compact) {
  const res = await fetch(`${baseUrl}/api/topics/${topicId}/articles`, {
    headers: authHeaders(),
  });
  const data = await parseJsonResponse(res);
  printJson(data, compact);
}

async function postArticle(topicId, body, compact) {
  const res = await fetch(`${baseUrl}/api/topics/${topicId}/articles`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  const data = await parseJsonResponse(res);
  printJson(data, compact);
}

async function main() {
  const raw = process.argv.slice(2);
  const compact = raw.includes("--compact");
  const args = raw.filter((a) => a !== "--compact");
  const [cmd, a, b] = args;

  if (!cmd || cmd === "-h" || cmd === "--help") usage(0);

  if (!apiKey) die("请设置 MIXDAO_API_KEY 或 API_KEY");

  switch (cmd) {
    case "topics":
      await getTopics(compact);
      break;
    case "articles": {
      const topicId = a || process.env.TOPIC_ID || "";
      if (!topicId) {
        die("用法: articles <TOPIC_ID> 或设置环境变量 TOPIC_ID");
      }
      await getArticles(topicId, compact);
      break;
    }
    case "add": {
      if (!a || !b) {
        die("用法: add <TOPIC_ID> <FILE.md | ->");
      }
      await postArticle(a, readMarkdown(b), compact);
      break;
    }
    default:
      console.error(`未知子命令: ${cmd}`);
      usage(1);
  }
}

main().catch((e) => {
  console.error(e instanceof Error ? e.message : e);
  process.exit(1);
});
