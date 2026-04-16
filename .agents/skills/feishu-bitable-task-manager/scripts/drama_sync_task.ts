#!/usr/bin/env node
import {
  BitableRef,
  ClampPageSize,
  DefaultBaseURL,
  Env,
  GetTenantAccessToken,
  LoadTaskFieldsFromEnv,
  CoerceDatePayload,
  NormalizeBitableValue,
  NormalizeExtra,
  ParseBitableURL,
  RequestJSON,
  ResolveWikiAppToken,
  readAllInput,
  detectInputFormat,
  parseJSONItems,
  parseJSONLItems,
} from "./bitable_common";
import * as fs from "node:fs";
import chalk from "chalk";
import { Command } from "commander";
import { fetchSourceRecords } from "./drama_fetch";

const createMaxBatchSize = 500;

type LogLevel = "info" | "error";

function createLogger(json: boolean, stream: NodeJS.WriteStream, color: boolean) {
  const useColor = color && !json;
  const levelColor = (value: string, level: LogLevel) => {
    if (!useColor) return value;
    return level === "error" ? chalk.red(value) : chalk.green(value);
  };
  const keyColor = (value: string) => (useColor ? chalk.blue(value) : value);
  const msgColor = (value: string) => (useColor ? chalk.green(value) : value);
  const valueColor = (value: string) => (useColor ? chalk.dim(value) : value);
  function formatValue(value: unknown): string {
    if (typeof value === "string") {
      if (value === "") return '""';
      if (/\s/.test(value) || value.includes("=") || value.includes("\"")) return JSON.stringify(value);
      return value;
    }
    if (value === null || value === undefined) return "null";
    if (typeof value === "number" || typeof value === "boolean") return String(value);
    return JSON.stringify(value);
  }
  function write(level: LogLevel, msg: string, fields?: Record<string, unknown>) {
    const time = new Date().toISOString();
    if (json) {
      const payload: Record<string, unknown> = { time, level: level.toUpperCase(), msg };
      if (fields) for (const [k, v] of Object.entries(fields)) payload[k] = v;
      stream.write(`${JSON.stringify(payload)}\n`);
      return;
    }
    const parts = [
      `${keyColor("time")}=${valueColor(time)}`,
      `${keyColor("level")}=${levelColor(level.toUpperCase(), level)}`,
      `${keyColor("msg")}=${msgColor(msg)}`,
    ];
    if (fields) {
      for (const [k, v] of Object.entries(fields)) {
        parts.push(`${keyColor(k)}=${valueColor(formatValue(v))}`);
      }
    }
    stream.write(parts.join(" ") + "\n");
  }
  return {
    info: (msg: string, fields?: Record<string, unknown>) => write("info", msg, fields),
    error: (msg: string, fields?: Record<string, unknown>) => write("error", msg, fields),
  };
}

let logger = createLogger(false, process.stdout, Boolean(process.stdout.isTTY));
let errLogger = createLogger(false, process.stderr, Boolean(process.stderr.isTTY));

function setLoggerJSON(enabled: boolean) {
  const outColor = Boolean(process.stdout.isTTY) && !enabled;
  const errColor = Boolean(process.stderr.isTTY) && !enabled;
  logger = createLogger(enabled, process.stdout, outColor);
  errLogger = createLogger(enabled, process.stderr, errColor);
}

function getGlobalOptions(program: Command) {
  const opts = program.opts<{ logJson?: boolean }>();
  setLoggerJSON(Boolean(opts.logJson));
  return { logJson: Boolean(opts.logJson) };
}

type SourceFieldMap = {
  bid: string;
  title: string;
  rightsScene: string;
  actor: string;
  paidTitle: string;
};

type SourceItem = {
  bid: string;
  title: string;
  rightsScene: string;
  actor: string;
  paidTitle: string;
};

function normalizeSourceFieldMap(opts: any): SourceFieldMap {
  return {
    bid: (opts.bidField || Env("SOURCE_FIELD_BID", "短剧id")).trim() || "短剧id",
    title: (opts.titleField || Env("SOURCE_FIELD_TITLE", "短剧名")).trim() || "短剧名",
    rightsScene: (opts.sceneField || Env("SOURCE_FIELD_RIGHTS_SCENE", "维权场景")).trim() || "维权场景",
    actor: (opts.actorField || Env("SOURCE_FIELD_ACTOR", "主角名")).trim() || "主角名",
    paidTitle: (opts.paidField || Env("SOURCE_FIELD_PAID_TITLE", "付费剧名")).trim() || "付费剧名",
  };
}

function extractSourceItem(fieldsRaw: Record<string, any>, map: SourceFieldMap): SourceItem {
  const get = (name: string) => NormalizeBitableValue(fieldsRaw[name]).trim();
  return {
    bid: get(map.bid),
    title: get(map.title),
    rightsScene: get(map.rightsScene),
    actor: get(map.actor),
    paidTitle: get(map.paidTitle),
  };
}

function validSourceItem(item: SourceItem, opts?: { paramsActor?: boolean }) {
  if (!item.bid || item.bid === "暂无") return false;
  if (opts?.paramsActor) {
    if (!normalizeActor(item.actor)) return false;
    return true;
  }
  if (!item.title) return false;
  if (!item.rightsScene) return false;
  return true;
}

function normalizeActor(actor: string) {
  if (!actor) return "";
  let s = actor.trim();
  // Strip JSON-like array wrapping: ["a","b"] or ["a" "b"]
  if (s.startsWith("[") && s.endsWith("]")) {
    s = s.slice(1, -1);
  }
  // Remove surrounding quotes and escaped quotes
  s = s.replace(/\\?"/g, "");
  const replaced = s.replace(/[，,、;；/]+/g, " ");
  return replaced.replace(/\s+/g, " ").trim();
}

function normalizeTitleForCompare(value: string) {
  if (!value) return "";
  return value.replace(/[\p{P}\p{S}\s]+/gu, "").trim();
}

function buildParamsListValues(src: SourceItem): string[] {
  const values: string[] = [];
  const seen = new Set<string>();
  const push = (value: string, compareKey?: string) => {
    const v = value.trim();
    if (!v) return;
    const key = (compareKey || v).trim();
    if (seen.has(key)) return;
    seen.add(key);
    values.push(v);
  };
  const title = src.title.trim();
  const titleKey = normalizeTitleForCompare(title);
  if (title) push(title, titleKey || title);
  const actor = normalizeActor(src.actor);
  if (actor) push(actor, actor);
  const paidTitle = src.paidTitle.trim();
  const paidKey = normalizeTitleForCompare(paidTitle);
  if (paidTitle && paidKey && paidKey !== titleKey) push(paidTitle, paidKey);
  return values;
}

function buildParamsListPayload(src: SourceItem) {
  return JSON.stringify(buildParamsListValues(src));
}

async function resolveBitableRef(baseURL: string, token: string, ref: BitableRef) {
  if (ref.AppToken) return ref;
  if (!ref.WikiToken) throw new Error("bitable URL missing app_token and wiki_token");
  ref.AppToken = await ResolveWikiAppToken(baseURL, token, ref.WikiToken);
  return ref;
}

async function fetchAllRecords(baseURL: string, token: string, ref: BitableRef, pageSize: number, viewID: string, useView: boolean, filterObj?: any, limit?: number) {
  const items: any[] = [];
  let pageToken = "";
  const size = ClampPageSize(pageSize);
  while (true) {
    const q = new URLSearchParams();
    q.set("page_size", String(size));
    if (pageToken) q.set("page_token", pageToken);
    const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/search?${q.toString()}`;
    const body: any = {};
    if (useView && viewID) body.view_id = viewID;
    if (filterObj) body.filter = filterObj;
    // Some Feishu tables reject POST /records/search without a JSON body (null/empty body => code 9499).
    const resp = await RequestJSON("POST", urlStr, token, body, true);
    if (resp.code !== 0) throw new Error(`search records failed: code=${resp.code} msg=${resp.msg}`);
    const batch = resp.data?.items || [];
    items.push(...batch);
    if (limit && items.length >= limit) return items.slice(0, limit);
    if (!resp.data?.has_more) break;
    pageToken = resp.data?.page_token || "";
    if (!pageToken) break;
  }
  return items;
}

async function fetchTableFieldNames(baseURL: string, token: string, ref: BitableRef) {
  const out: string[] = [];
  let pageToken = "";
  while (true) {
    const q = new URLSearchParams();
    q.set("page_size", "500");
    if (pageToken) q.set("page_token", pageToken);
    const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/fields?${q.toString()}`;
    const resp = await RequestJSON("GET", urlStr, token, null, true);
    if (resp.code !== 0) throw new Error(`list fields failed: code=${resp.code} msg=${resp.msg}`);
    const items = resp.data?.items || [];
    for (const item of items) {
      const name = NormalizeBitableValue(item?.field_name).trim();
      if (name) out.push(name);
    }
    if (!resp.data?.has_more) break;
    pageToken = String(resp.data?.page_token || "").trim();
    if (!pageToken) break;
  }
  return out;
}

function resolveFieldName(fieldNames: string[], preferred: string, candidates: string[]) {
  const byLower = new Map<string, string>();
  for (const name of fieldNames) {
    const key = name.trim().toLowerCase();
    if (key && !byLower.has(key)) byLower.set(key, name);
  }
  const tryList = [preferred, ...candidates].map((x) => x.trim()).filter(Boolean);
  for (const item of tryList) {
    const hit = byLower.get(item.toLowerCase());
    if (hit) return hit;
  }
  return "";
}

function resolveFilterDate(preset: string) {
  const trimmed = (preset || "").trim();
  if (!trimmed) return "";
  if (trimmed === "Today") return "Today";
  if (trimmed === "Yesterday") return "Yesterday";
  if (trimmed === "Any") return "";
  return trimmed;
}

function resolveFilterDayForCompare(preset: string) {
  const trimmed = (preset || "").trim();
  if (!trimmed) return "";
  if (trimmed === "Today") return todayDateString();
  if (trimmed === "Yesterday") {
    const now = new Date();
    const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1, 0, 0, 0, 0);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  }
  if (trimmed === "Any") return "";
  return trimmed;
}

function resolveExactDateMs(day: string) {
  const trimmed = (day || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return "";
  const ms = Date.parse(`${trimmed}T00:00:00`);
  if (Number.isNaN(ms)) return "";
  return String(ms);
}

function parseCSVList(raw: string) {
  return raw
    .split(/[\s,，]+/g)
    .map((x) => x.trim())
    .filter(Boolean);
}

function buildORIsFilter(fieldName: string, values: string[]) {
  const name = fieldName.trim();
  if (!name) return null;
  const seen = new Set<string>();
  const conds: any[] = [];
  for (const v of values) {
    const val = v.trim();
    if (!val || seen.has(val)) continue;
    seen.add(val);
    conds.push({ field_name: name, operator: "is", value: [val] });
  }
  if (!conds.length) return null;
  return conds.length === 1 ? { conjunction: "and", conditions: conds } : { conjunction: "or", conditions: conds };
}

function buildTaskFilter(fieldsMap: Record<string, string>, app: string, scene: string, datePreset: string) {
  const conds: any[] = [];
  const add = (fieldKey: string, value: string) => {
    const name = (fieldsMap[fieldKey] || "").trim();
    const val = value.trim();
    if (name && val) conds.push({ field_name: name, operator: "is", value: [val] });
  };
  add("App", app);
  add("Scene", scene);
  const dateField = (fieldsMap["Date"] || "").trim();
  if (dateField) {
    const preset = resolveFilterDate(datePreset);
    if (preset) {
      if (/^\d{4}-\d{2}-\d{2}$/.test(preset)) {
        const ms = resolveExactDateMs(preset);
        if (ms) {
          conds.push({ field_name: dateField, operator: "is", value: ["ExactDate", ms] });
        } else {
          conds.push({ field_name: dateField, operator: "is", value: [preset] });
        }
      } else {
        conds.push({ field_name: dateField, operator: "is", value: [preset] });
      }
    }
  }
  if (!conds.length) return null;
  return { conjunction: "and", conditions: conds };
}

function parseInputItems(pathStr: string) {
  const raw = readAllInput(pathStr);
  const format = detectInputFormat(pathStr, raw);
  if (format === "jsonl") return parseJSONLItems(raw);
  return parseJSONItems(raw);
}

function simplifyValue(value: any): any {
  if (value === null || value === undefined) return "";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return value;
  if (Array.isArray(value)) {
    if (value.length === 0) return "";
    if (value.every((it) => it && typeof it === "object" && "text" in it)) {
      const texts = value
        .map((it) => (typeof (it as any).text === "string" ? (it as any).text.trim() : ""))
        .filter((s) => s);
      return texts.join(",");
    }
    if (value.every((it) => it && typeof it === "object" && "link" in it)) {
      const links = value
        .map((it) => (typeof (it as any).link === "string" ? (it as any).link.trim() : ""))
        .filter((s) => s);
      if (links.length) return links.join(",");
    }
    const parts = value.map((it) => simplifyValue(it)).filter((s) => s !== "");
    if (parts.length === 0) return "";
    if (parts.every((it) => typeof it === "string")) return (parts as string[]).join(",");
    return parts;
  }
  if (typeof value === "object") {
    if ("text" in value && typeof (value as any).text === "string") return (value as any).text.trim();
    if ("link" in value && typeof (value as any).link === "string") return (value as any).link.trim();
    if ("value" in value) return simplifyValue((value as any).value);
  }
  return NormalizeBitableValue(value);
}

function simplifyFields(fieldsRaw: Record<string, any>) {
  const out: Record<string, any> = {};
  for (const [k, v] of Object.entries(fieldsRaw)) {
    out[k] = simplifyValue(v);
  }
  return out;
}

function todayDateString() {
  const now = new Date();
  const y = now.getFullYear();
  const m = String(now.getMonth() + 1).padStart(2, "0");
  const d = String(now.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

function normalizeDateToYMD(value: any): string {
  if (value === null || value === undefined) return "";
  if (typeof value === "number") {
    const ms = value < 100000000000 ? value * 1000 : value;
    const dt = new Date(ms);
    if (Number.isNaN(dt.getTime())) return "";
    return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
  }
  if (typeof value === "string") {
    const s = value.trim();
    if (!s) return "";
    if (/^\d+$/.test(s)) {
      const n = Number(s);
      if (!Number.isFinite(n)) return "";
      const ms = n < 100000000000 ? n * 1000 : n;
      const dt = new Date(ms);
      if (Number.isNaN(dt.getTime())) return "";
      return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
    }
    const m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (m) return `${m[1]}-${m[2]}-${m[3]}`;
    const dt = new Date(s);
    if (!Number.isNaN(dt.getTime())) {
      return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, "0")}-${String(dt.getDate()).padStart(2, "0")}`;
    }
    return "";
  }
  const asStr = NormalizeBitableValue(value).trim();
  if (!asStr) return "";
  return normalizeDateToYMD(asStr);
}

function buildTaskFields(fieldsMap: Record<string, string>, item: { app: string; scene: string; date: string; status: string; extra: string; book_id: string; params: string }) {
  const out: Record<string, any> = {};
  const set = (key: string, value: string) => {
    const col = (fieldsMap[key] || "").trim();
    if (!col || !value) return;
    out[col] = value;
  };
  set("App", item.app);
  set("Scene", item.scene);
  if (fieldsMap["Date"] && item.date != null) {
    const [payload, ok] = CoerceDatePayload(item.date);
    if (ok) out[fieldsMap["Date"]] = payload;
  }
  set("Status", item.status);
  set("BookID", item.book_id);
  set("Params", item.params);
  const extraVal = NormalizeExtra(item.extra);
  if (extraVal && (fieldsMap["Extra"] || "").trim()) out[fieldsMap["Extra"]] = extraVal;
  return out;
}

async function batchCreate(baseURL: string, token: string, ref: BitableRef, records: Array<{ fields: any }>) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/batch_create`;
  const payload = { records };
  const resp = await RequestJSON("POST", urlStr, token, payload, true);
  if (resp.code !== 0) throw new Error(`batch create failed: code=${resp.code} msg=${resp.msg}`);
}

function deriveTasksFromSource(items: Array<Record<string, any>>, sourceFieldMap: SourceFieldMap, opts: any) {
  const derived: Array<{ app: string; scene: string; date: string; status: string; extra: string; book_id: string; params: string }> = [];
  let filtered = 0;
  const useParamsList = Boolean(opts.paramsList);
  const useParamsSplit = Boolean(opts.paramsSplit);
  const useParamsActor = Boolean(opts.paramsActor);
  for (const fieldsRaw of items) {
    const src = extractSourceItem(fieldsRaw, sourceFieldMap);
    if (!validSourceItem(src, { paramsActor: useParamsActor })) continue;
    filtered++;
    if (useParamsActor) {
      const actor = normalizeActor(src.actor);
      if (!actor) continue;
      derived.push({
        app: opts.app,
        scene: opts.scene,
        date: opts.date,
        status: opts.status,
        extra: opts.extra,
        book_id: src.bid,
        params: actor,
      });
      continue;
    }
    if (useParamsList) {
      derived.push({
        app: opts.app,
        scene: opts.scene,
        date: opts.date,
        status: opts.status,
        extra: opts.extra,
        book_id: src.bid,
        params: buildParamsListPayload(src),
      });
      continue;
    }
    // --params-split: one task per search term; default: title only
    const terms = useParamsSplit ? buildParamsListValues(src) : [src.title.trim()].filter(Boolean);
    for (const term of terms) {
      derived.push({
        app: opts.app,
        scene: opts.scene,
        date: opts.date,
        status: opts.status,
        extra: opts.extra,
        book_id: src.bid,
        params: term,
      });
    }
  }
  return { derived, filtered };
}

async function loadExistingBookIDs(baseURL: string, token: string, taskRef: BitableRef, fieldsMap: Record<string, string>, opts: any, pageSize: number, useView: boolean) {
  const existingBookIDs = new Set<string>();
  const dateCol = (fieldsMap["Date"] || "").trim();
  const targetDay = resolveFilterDayForCompare(opts.date || "Today");

  const taskFilter = buildTaskFilter(fieldsMap, opts.app, opts.scene, opts.date);
  const taskItems = await fetchAllRecords(baseURL, token, taskRef, pageSize, taskRef.ViewID, useView, taskFilter);

  for (const item of taskItems) {
    const fieldsRaw = item.fields || {};
    const bookID = NormalizeBitableValue(fieldsRaw[fieldsMap["BookID"]]).trim();
    if (!bookID) continue;
    if (!dateCol) {
      existingBookIDs.add(bookID);
      continue;
    }
    const dateValue = fieldsRaw[dateCol];
    const ymd = normalizeDateToYMD(dateValue);
    if (!targetDay || !ymd) continue;
    if (ymd === targetDay) existingBookIDs.add(bookID);
  }
  return existingBookIDs;
}

async function runCreateOrSync(opts: any) {
  const inputPath = (opts.input || "").trim();
  const sourceURL = (opts.bitableUrl || "").trim();
  if (!inputPath && !sourceURL) {
    errLogger.error("one source is required", { hint: "--input <path> or --bitable-url <url>" });
    process.exit(2);
  }
  const taskURL = (opts.taskUrl || Env("TASK_BITABLE_URL", "")).trim();
  if (!taskURL) {
    errLogger.error("task url is required", { hint: "--task-url or TASK_BITABLE_URL" });
    process.exit(2);
  }
  const appID = Env("FEISHU_APP_ID", "");
  const appSecret = Env("FEISHU_APP_SECRET", "");
  if (!appID || !appSecret) {
    errLogger.error("FEISHU_APP_ID/FEISHU_APP_SECRET are required");
    process.exit(2);
  }
  const baseURL = Env("FEISHU_BASE_URL", DefaultBaseURL);
  const fieldsMap = LoadTaskFieldsFromEnv();
  const sourceFieldMap = normalizeSourceFieldMap(opts);
  const modeFlags = [Boolean(opts.paramsList), Boolean(opts.paramsSplit), Boolean(opts.paramsActor)].filter(Boolean).length;
  if (modeFlags > 1) {
    errLogger.error("invalid options", { hint: "--params-list, --params-split, --params-actor are mutually exclusive" });
    process.exit(2);
  }
  let taskRef: BitableRef;
  try {
    taskRef = ParseBitableURL(taskURL);
  } catch (err: any) {
    errLogger.error("parse bitable URL failed", { err: err?.message || String(err) });
    process.exit(2);
  }
  let token: string;
  try {
    token = await GetTenantAccessToken(baseURL, appID, appSecret);
  } catch (err: any) {
    errLogger.error("get tenant access token failed", { err: err?.message || String(err) });
    process.exit(2);
  }
  try {
    taskRef = await resolveBitableRef(baseURL, token, taskRef);
  } catch (err: any) {
    errLogger.error("resolve bitable app token failed", { err: err?.message || String(err) });
    process.exit(2);
  }
  const useView = false;
  const pageSize = 200;
  const limit = Number.isFinite(opts.limit) ? Math.max(0, Number(opts.limit)) : 0;

  let sourceFields: Array<Record<string, any>> = [];
  let sourceTotal = 0;
  if (inputPath) {
    sourceFields = parseInputItems(inputPath).map((it: any) => (it && typeof it === "object" && (it as any).fields ? (it as any).fields : it));
    if (limit > 0) sourceFields = sourceFields.slice(0, limit);
    sourceTotal = sourceFields.length;
  } else {
    const bookIDs = parseCSVList(String(opts.bookId || "").trim());
    const priorities = parseCSVList(String(opts.priority || "").trim());
    try {
      const res = await fetchSourceRecords({
        bitableURL: sourceURL,
        bookIDs,
        bidField: String(opts.bidField || ""),
        priorities,
        priorityField: String(opts.priorityField || ""),
        pageSize,
        limit,
        appID,
        appSecret,
        baseURL,
      });
      sourceFields = res.items.map((it: any) => it.fields || {});
      sourceTotal = res.items.length;
    } catch (err: any) {
      errLogger.error("fetch source rows failed", { err: err?.message || String(err) });
      process.exit(2);
    }
  }

  const userDate = (opts.date || "").trim();
  const isExplicitDate = /^\d{4}-\d{2}-\d{2}$/.test(userDate);
  const dateFilter = isExplicitDate ? userDate : "Today";
  const createDate = isExplicitDate ? userDate : todayDateString();
  const fixedOpts = { ...opts, scene: "综合页搜索", date: dateFilter, status: "pending" };
  const { derived, filtered } = deriveTasksFromSource(sourceFields, sourceFieldMap, fixedOpts);
  let existingBookIDs = new Set<string>();
  const skipExisting = Boolean(opts.skipExisting);
  if (skipExisting) {
    existingBookIDs = await loadExistingBookIDs(baseURL, token, taskRef, fieldsMap, fixedOpts, pageSize, useView);
  }
  let skipped = 0;
  const records = derived
    .filter((item) => {
      if (!skipExisting) return true;
      const exists = existingBookIDs.has(item.book_id);
      if (exists) skipped++;
      return !exists;
    })
    .map((item) => buildTaskFields(fieldsMap, { ...item, date: createDate }))
    .filter((fields) => Object.keys(fields).length)
    .map((fields) => ({ fields }));
  if (!records.length) {
    logger.info("result", { data: { source_total: sourceTotal, derived: derived.length, filtered, created: 0, skipped } });
    process.exit(0);
  }
  let created = 0;
  const start = Date.now();
  const errors: string[] = [];
  for (let i = 0; i < records.length; i += createMaxBatchSize) {
    const batch = records.slice(i, i + createMaxBatchSize);
    try {
      await batchCreate(baseURL, token, taskRef, batch);
      created += batch.length;
    } catch (err: any) {
      errors.push(err?.message || String(err));
      break;
    }
  }
  const elapsed = Math.floor(((Date.now() - start) / 1000) * 1000) / 1000;
  logger.info("result", {
    data: { source_total: sourceTotal, filtered, derived: derived.length, created, skipped, failed: errors.length, errors, elapsed_seconds: elapsed },
  });
  process.exit(errors.length ? 1 : 0);
}

async function main() {
  const program = new Command();
  program
    .name("drama-sync-task")
    .description("Create tasks from --input JSON/JSONL or source Bitable (--bitable-url)")
    .option("--log-json", "Output logs as JSON lines")
    .allowExcessArguments(false)
    .option("--input <path>", "Input JSONL path (or - for stdin)")
    .option("--bitable-url <url>", "Source Bitable URL (original table)")
    .option("--book-id <value>", "Optional source BookID/BID filter (single value or comma-separated list)")
    .option("--task-url <url>", "Task Bitable URL (default: TASK_BITABLE_URL)")
    .option("--limit <count>", "Limit number of source rows to process", (v) => Number.parseInt(v, 10))
    .option("--app <app>", "Task app", "com.smile.gifmaker")
    .option("--extra <extra>", "Task extra", "")
    .option("--params-list", "Store [短剧名, 主角名, 付费剧名] as a JSON list in Params (one task per source row)")
    .option("--params-split", "Create one task per search term (短剧名, 主角名, 付费剧名) with dedup")
    .option("--params-actor", "Store only 主角名 in Params (one task per source row)")
    .option("--date <date>", "Task date in YYYY-MM-DD format (default: today)")
    .option("--skip-existing", "Skip creating tasks when BookID already exists for the target date")
    .option("--bid-field <name>", "Source field name for BID")
    .option("--title-field <name>", "Source field name for 短剧名")
    .option("--scene-field <name>", "Source field name for 维权场景")
    .option("--actor-field <name>", "Source field name for 主角名")
    .option("--paid-field <name>", "Source field name for 付费剧名")
    .option("--priority <value>", "Optional Priority filter (single value or comma-separated list)")
    .option("--priority-field <name>", "Preferred source field name for Priority")
    .helpOption(true);
  program.action(async (opts) => {
    setLoggerJSON(Boolean(program.opts()?.logJson));
    await runCreateOrSync(opts);
  });

  await program.parseAsync(process.argv);
}

if (require.main === module) {
  main().catch((err: any) => {
    errLogger.error("fatal", { err: err?.message || String(err) });
    process.exit(1);
  });
}
