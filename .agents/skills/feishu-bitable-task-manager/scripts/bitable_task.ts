#!/usr/bin/env node
import {
  BitableRef,
  ClampPageSize,
  CoerceDatePayload,
  CoerceInt,
  CoerceMillis,
  DefaultBaseURL,
  Env,
  FieldInt,
  GetTenantAccessToken,
  LoadTaskFieldsFromEnv,
  NormalizeExtra,
  NormalizeBitableValue,
  ParseBitableURL,
  RequestJSON,
  ResolveWikiAppToken,
  BitableValueToString,
  MaxPageSize,
  readAllInput,
  detectInputFormat,
  parseJSONItems,
  parseJSONLItems,
} from "./bitable_common";
import chalk from "chalk";
import { Command } from "commander";

const updateMaxBatchSize = 500;
const updateMaxFilterValues = 50;
const createMaxBatchSize = 500;
const createMaxFilterValues = 50;

const appGroupLabels: Record<string, string> = {
  "com.smile.gifmaker": "快手",
};

type LogLevel = "debug" | "info" | "error";
const levelRank: Record<LogLevel, number> = { debug: 10, info: 20, error: 30 };

function createLogger(json: boolean, stream: NodeJS.WriteStream, color: boolean, minLevel: LogLevel) {
  const useColor = color && !json;
  const levelColor = (value: string, level: LogLevel) => {
    if (!useColor) return value;
    if (level === "error") return chalk.red(value);
    if (level === "debug") return chalk.gray(value);
    return chalk.green(value);
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
    if (levelRank[level] < levelRank[minLevel]) return;
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
    debug: (msg: string, fields?: Record<string, unknown>) => write("debug", msg, fields),
    info: (msg: string, fields?: Record<string, unknown>) => write("info", msg, fields),
    error: (msg: string, fields?: Record<string, unknown>) => write("error", msg, fields),
  };
}

let logger = createLogger(false, process.stdout, Boolean(process.stdout.isTTY), "info");
let errLogger = createLogger(false, process.stderr, Boolean(process.stderr.isTTY), "info");

function normalizeLogLevel(raw: string | undefined) {
  const v = (raw || "").trim().toLowerCase();
  if (v === "debug") return "debug" as LogLevel;
  if (v === "error") return "error" as LogLevel;
  return "info" as LogLevel;
}

function setLoggerJSON(enabled: boolean, level: LogLevel) {
  const outColor = Boolean(process.stdout.isTTY) && !enabled;
  const errColor = Boolean(process.stderr.isTTY) && !enabled;
  logger = createLogger(enabled, process.stdout, outColor, level);
  errLogger = createLogger(enabled, process.stderr, errColor, level);
}

function getGlobalOptions(program: Command) {
  const opts = program.opts<{ logJson?: boolean; logLevel?: string }>();
  const level = normalizeLogLevel(opts.logLevel);
  setLoggerJSON(Boolean(opts.logJson), level);
  return { logJson: Boolean(opts.logJson), logLevel: level };
}

type Task = {
  task_id: number;
  biz_task_id: string;
  parent_task_id: string;
  app: string;
  scene: string;
  params: string;
  item_id: string;
  book_id: string;
  url: string;
  user_id: string;
  user_name: string;
  date: string;
  status: string;
  extra: string;
  logs: string;
  last_screenshot: string;
  group_id: string;
  device_serial: string;
  dispatched_device: string;
  dispatched_at: string;
  start_at: string;
  end_at: string;
  elapsed_seconds: string;
  items_collected: string;
  retry_count: string;
  record_id: string;
  raw_fields?: any;
};

function resolveExactDateMs(day: string) {
  const trimmed = (day || "").trim();
  if (!/^\d{4}-\d{2}-\d{2}$/.test(trimmed)) return "";
  const ms = Date.parse(`${trimmed}T00:00:00`);
  if (Number.isNaN(ms)) return "";
  return String(ms);
}

function buildFilter(fields: Record<string, string>, app: string, scene: string, status: string, datePreset: string) {
  const conds: any[] = [];
  const add = (fieldKey: string, value: string) => {
    const name = (fields[fieldKey] || "").trim();
    const val = value.trim();
    if (val === "Any") return;
    if (name && val) conds.push({ field_name: name, operator: "is", value: [val] });
  };
  add("App", app);
  add("Scene", scene);
  add("Status", status);
  if (datePreset && datePreset !== "Any") {
    const ms = resolveExactDateMs(datePreset);
    if (ms) {
      const name = (fields["Date"] || "").trim();
      if (name) conds.push({ field_name: name, operator: "is", value: ["ExactDate", ms] });
    } else {
      add("Date", datePreset);
    }
  }
  if (!conds.length) return null;
  return { conjunction: "and", conditions: conds };
}

function parseListArg(raw: any): string[] {
  const s = String(raw ?? "").trim();
  if (!s) return [];
  try {
    const j = JSON.parse(s);
    if (Array.isArray(j)) return j.map((x) => String(x)).map((x) => x.trim()).filter(Boolean);
  } catch {
    // ignore
  }
  return s
    .split(/[\s,，]+/g)
    .map((x) => x.trim())
    .filter(Boolean);
}

function parseCSVOnlyArg(raw: any, flag: string): string[] {
  const s = String(raw ?? "").trim();
  if (!s) return [];
  if (s.startsWith("[") || s.startsWith("{")) {
    throw new Error(`${flag} must be a comma-separated string, e.g. 111,222,333`);
  }
  return s
    .split(/[\s,，]+/g)
    .map((x) => x.trim())
    .filter(Boolean);
}

function parsePositiveIntCSVOnlyArg(raw: any, flag: string): number[] {
  const out: number[] = [];
  for (const v of parseCSVOnlyArg(raw, flag)) {
    const n = Math.trunc(Number(v));
    if (Number.isFinite(n) && n > 0) out.push(n);
  }
  return Array.from(new Set(out));
}

function parseIntListArg(raw: any): number[] {
  const out: number[] = [];
  for (const v of parseListArg(raw)) {
    const n = Math.trunc(Number(v));
    if (Number.isFinite(n) && n > 0) out.push(n);
  }
  return Array.from(new Set(out));
}

function mergeAndFilter(a: any, b: any) {
  if (!a) return b;
  if (!b) return a;
  const out: any = { conjunction: "and", conditions: [], children: [] as any[] };
  if (a.conjunction === "and") {
    if (Array.isArray(a.conditions)) out.conditions.push(...a.conditions);
    if (Array.isArray(a.children)) out.children.push(...a.children);
  } else {
    out.children.push(a);
  }
  if (b.conjunction === "and") {
    if (Array.isArray(b.conditions)) out.conditions.push(...b.conditions);
    if (Array.isArray(b.children)) out.children.push(...b.children);
  } else {
    out.children.push(b);
  }
  if (!out.children.length) delete out.children;
  return out;
}

function decodeTask(fieldsRaw: Record<string, any>, mapping: Record<string, string>): [Task, boolean] {
  if (!fieldsRaw || !Object.keys(fieldsRaw).length) return [{} as Task, false];
  const taskID = FieldInt(fieldsRaw, mapping["TaskID"]);
  if (taskID === 0) return [{} as Task, false];
  const get = (name: string) => NormalizeBitableValue(fieldsRaw[mapping[name]]).trim();
  const t: Task = {
    task_id: taskID,
    biz_task_id: get("BizTaskID"),
    parent_task_id: get("ParentTaskID"),
    app: get("App"),
    scene: get("Scene"),
    params: get("Params"),
    item_id: get("ItemID"),
    book_id: get("BookID"),
    url: get("URL"),
    user_id: get("UserID"),
    user_name: get("UserName"),
    date: get("Date"),
    status: get("Status"),
    extra: get("Extra"),
    logs: get("Logs"),
    last_screenshot: get("LastScreenShot"),
    group_id: get("GroupID"),
    device_serial: get("DeviceSerial"),
    dispatched_device: get("DispatchedDevice"),
    dispatched_at: get("DispatchedAt"),
    start_at: get("StartAt"),
    end_at: get("EndAt"),
    elapsed_seconds: get("ElapsedSeconds"),
    items_collected: get("ItemsCollected"),
    retry_count: get("RetryCount"),
    record_id: "",
  };
  if (!t.params && !t.item_id && !t.book_id && !t.url && !t.user_id && !t.user_name) return [{} as Task, false];
  return [t, true];
}

type FetchResult = { tasks: Task[]; elapsedSeconds: number; hasMore: boolean; nextPageToken: string; pages: number };

async function FetchTasksOnce(opts: any): Promise<FetchResult | { err: true; code: number }> {
  const taskURL = (opts.task_url || "").trim();
  if (!taskURL) {
    errLogger.error("TASK_BITABLE_URL is required");
    return { err: true, code: 2 };
  }
  const appID = Env("FEISHU_APP_ID", "");
  const appSecret = Env("FEISHU_APP_SECRET", "");
  if (!appID || !appSecret) {
    errLogger.error("FEISHU_APP_ID/FEISHU_APP_SECRET are required");
    return { err: true, code: 2 };
  }
  const baseURL = Env("FEISHU_BASE_URL", DefaultBaseURL);
  let ref: BitableRef;
  try {
    ref = ParseBitableURL(taskURL);
  } catch (err: any) {
    errLogger.error("parse bitable URL failed", { err: err?.message || String(err) });
    return { err: true, code: 2 };
  }
  const fields = LoadTaskFieldsFromEnv();
  let filterObj = buildFilter(fields, opts.app || "", opts.scene || "", opts.status || "", opts.date || "");
  if (opts.task_id != null && String(opts.task_id).trim()) {
    let ids: number[] = [];
    try {
      ids = parsePositiveIntCSVOnlyArg(opts.task_id, "--task-id");
    } catch (err: any) {
      errLogger.error(err?.message || String(err));
      return { err: true, code: 2 };
    }
    filterObj = buildIDFilter(fields["TaskID"], ids.map((n) => String(n)));
  } else if (opts.biz_task_id != null && String(opts.biz_task_id).trim()) {
    const bizID = String(opts.biz_task_id || "").trim();
    if (bizID) filterObj = buildIDFilter(fields["BizTaskID"], [bizID]);
  }
  if (opts.group_id != null && String(opts.group_id).trim()) {
    let gids: string[] = [];
    try {
      gids = parseCSVOnlyArg(opts.group_id, "--group-id");
    } catch (err: any) {
      errLogger.error(err?.message || String(err));
      return { err: true, code: 2 };
    }
    const name = (fields["GroupID"] || "").trim();
    if (name && gids.length) {
      if (gids.length === 1) {
        const groupFilter = { conjunction: "and", conditions: [{ field_name: name, operator: "is", value: [gids[0]] }] };
        filterObj = mergeAndFilter(filterObj, groupFilter);
      } else {
        const orFilter = {
          conjunction: "or",
          conditions: gids.map((x) => ({ field_name: name, operator: "is", value: [x] })),
        };
        filterObj = mergeAndFilter(filterObj, orFilter);
      }
    }
  }
  let token: string;
  try {
    token = await GetTenantAccessToken(baseURL, appID, appSecret);
  } catch (err: any) {
    errLogger.error("get tenant access token failed", { err: err?.message || String(err) });
    return { err: true, code: 2 };
  }
  if (!ref.AppToken) {
    if (!ref.WikiToken) {
      errLogger.error("bitable URL missing app_token and wiki_token");
      return { err: true, code: 2 };
    }
    try {
      ref.AppToken = await ResolveWikiAppToken(baseURL, token, ref.WikiToken);
    } catch (err: any) {
      errLogger.error("resolve wiki app token failed", { err: err?.message || String(err) });
      return { err: true, code: 2 };
    }
  }
  let viewID = (opts.view_id || "").trim();
  if (!viewID) viewID = ref.ViewID;

  let pageSize = ClampPageSize(Number(opts.page_size || 0));
  if (opts.limit && Number(opts.limit) > 0 && Number(opts.limit) < pageSize) pageSize = Number(opts.limit);

  const items: any[] = [];
  let pageToken = "";
  let pages = 0;
  const start = Date.now();

  while (true) {
    const q = new URLSearchParams();
    q.set("page_size", String(pageSize));
    if (pageToken) q.set("page_token", pageToken);
    const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/search?${q.toString()}`;
    let body: any = null;
    if ((!opts.ignore_view && viewID) || filterObj) {
      body = {};
      if (!opts.ignore_view && viewID) body.view_id = viewID;
      if (filterObj) body.filter = filterObj;
    }
    let resp: any;
    try {
      resp = await RequestJSON("POST", urlStr, token, body, true);
    } catch (err: any) {
      errLogger.error("search records request failed", { err: err?.message || String(err) });
      return { err: true, code: 2 };
    }
    if (resp.code !== 0) {
      errLogger.error("search records failed", { code: resp.code, msg: resp.msg });
      return { err: true, code: 2 };
    }
    items.push(...(resp.data?.items || []));
    pages++;
    pageToken = String(resp.data?.page_token || "").trim();
    if (opts.limit && items.length >= Number(opts.limit)) {
      items.splice(Number(opts.limit));
      break;
    }
    if (opts.max_pages && pages >= Number(opts.max_pages)) break;
    if (!resp.data?.has_more || !pageToken) break;
  }
  const elapsed = Math.floor(((Date.now() - start) / 1000) * 1000) / 1000;

  const tasks: Task[] = [];
  for (const it of items) {
    const recordID = String(it.record_id || "").trim();
    const fieldsRaw = it.fields || {};
    const [t, ok] = decodeTask(fieldsRaw, fields);
    if (!ok) continue;
    t.record_id = recordID;
    if (opts.raw) t.raw_fields = fieldsRaw;
    tasks.push(t);
  }

  return {
    tasks,
    elapsedSeconds: elapsed,
    hasMore: Boolean(pageToken),
    nextPageToken: pageToken,
    pages,
  };
}

async function FetchTasksForStatuses(opts: any, statusList: string[], limit: number) {
  const tasks: Task[] = [];
  let totalElapsed = 0;
  let lastPageInfo = { hasMore: false, nextPageToken: "", pages: 0 };
  for (const status of statusList) {
    const remaining = limit > 0 ? Math.max(limit - tasks.length, 0) : 0;
    if (limit > 0 && remaining <= 0) break;
    const perOpts = { ...opts, status };
    if (limit > 0) perOpts.limit = remaining;
    const res = await FetchTasksOnce(perOpts);
    if ("err" in res) return { err: true, code: res.code };
    tasks.push(...res.tasks);
    totalElapsed += res.elapsedSeconds;
    lastPageInfo = { hasMore: res.hasMore, nextPageToken: res.nextPageToken, pages: res.pages };
    if (limit > 0 && tasks.length >= limit) {
      tasks.splice(limit);
      break;
    }
  }
  return {
    tasks,
    elapsedSeconds: totalElapsed,
    pageInfo: lastPageInfo,
  };
}

async function FetchTasksForScenesAndStatuses(opts: any, sceneList: string[], statusList: string[], limit: number) {
  const scenes = sceneList.length ? sceneList : [opts.scene || ""];
  const tasks: Task[] = [];
  let totalElapsed = 0;
  let lastPageInfo = { hasMore: false, nextPageToken: "", pages: 0 };
  for (const scene of scenes) {
    const trimmed = (scene || "").trim();
    if (!trimmed) continue;
    const remaining = limit > 0 ? Math.max(limit - tasks.length, 0) : 0;
    if (limit > 0 && remaining <= 0) break;
    const perOpts = { ...opts, scene: trimmed };
    if (limit > 0) perOpts.limit = remaining;
    const res = await FetchTasksForStatuses(perOpts, statusList, limit > 0 ? remaining : 0);
    if ("err" in res) return { err: true, code: res.code };
    tasks.push(...res.tasks);
    totalElapsed += res.elapsedSeconds;
    lastPageInfo = res.pageInfo;
    if (limit > 0 && tasks.length >= limit) {
      tasks.splice(limit);
      break;
    }
  }
  return { tasks, elapsedSeconds: totalElapsed, pageInfo: lastPageInfo };
}

function parseCSVSet(raw: string) {
  const out: Record<string, boolean> = {};
  for (const part of raw.split(",")) {
    const p = part.trim().toLowerCase();
    if (p) out[p] = true;
  }
  return out;
}

function parseCSVList(raw: string) {
  const out: string[] = [];
  const seen: Record<string, boolean> = {};
  for (const part of raw.split(",")) {
    const p = part.trim();
    if (!p) continue;
    const key = p.toLowerCase();
    if (seen[key]) continue;
    seen[key] = true;
    out.push(p);
  }
  return out;
}

function parseStaleMillis(value: string) {
  const [ms, ok] = CoerceMillis(value);
  if (ok && ms > 0) return ms;
  return 0;
}

async function FetchTasks(opts: any) {
  const sceneList = parseCSVList(opts.scene || "");
  const statuses = parseCSVList(opts.status || "");
  const statusList = statuses.length ? statuses : ["pending"];
  const limit = Number(opts.limit || 0);
  const hasDirectIDFilter =
    (opts.task_id != null && String(opts.task_id).trim() !== "") ||
    (opts.biz_task_id != null && String(opts.biz_task_id).trim() !== "") ||
    (opts.group_id != null && String(opts.group_id).trim() !== "");
  const res = hasDirectIDFilter
    ? await FetchTasksForStatuses(opts, statusList, limit > 0 ? limit : 0)
    : await FetchTasksForScenesAndStatuses(opts, sceneList, statusList, limit > 0 ? limit : 0);
  if ("err" in res) return res.code;
  const tasks = res.tasks;
  const totalElapsed = res.elapsedSeconds;
  const lastPageInfo = res.pageInfo;

  if (opts.jsonl) {
    for (const t of tasks) logger.info("task", { task: t });
    return 0;
  }

  logger.info("tasks", {
    data: {
      tasks,
      count: tasks.length,
      elapsed_seconds: Math.floor(totalElapsed * 1000) / 1000,
      page_info: lastPageInfo,
    },
  });
  return 0;
}

function buildIDFilter(fieldName: string, values: string[]) {
  const name = fieldName.trim();
  if (!name) return null;
  const seen: Record<string, boolean> = {};
  const conds: any[] = [];
  for (const v of values) {
    const val = v.trim();
    if (!val || seen[val]) continue;
    seen[val] = true;
    conds.push({ field_name: name, operator: "is", value: [val] });
  }
  if (!conds.length) return null;
  return { conjunction: "or", conditions: conds };
}

async function searchItems(baseURL: string, token: string, ref: BitableRef, filterObj: any, pageSize: number, ignoreView: boolean, viewID: string) {
  const size = ClampPageSize(pageSize);
  const q = new URLSearchParams();
  q.set("page_size", String(size));
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/search?${q.toString()}`;
  let body: any = null;
  if ((!ignoreView && viewID) || filterObj) {
    body = {};
    if (!ignoreView && viewID) body.view_id = viewID;
    if (filterObj) body.filter = filterObj;
  }
  const resp = await RequestJSON("POST", urlStr, token, body, true);
  if (resp.code !== 0) throw new Error(`search records failed: code=${resp.code} msg=${resp.msg}`);
  return resp.data?.items || [];
}

function extractStatusesFromItems(items: any[], statusField: string) {
  const out: Record<string, string> = {};
  for (const item of items) {
    const recordID = BitableValueToString(item.record_id).trim();
    const fieldsRaw = item.fields || {};
    const status = BitableValueToString(fieldsRaw[statusField]).trim();
    if (recordID && status) out[recordID] = status;
  }
  return out;
}

async function resolveRecordIDsByTaskID(baseURL: string, token: string, ref: BitableRef, fieldsMap: Record<string, string>, taskIDs: number[], ignoreView: boolean, viewID: string) {
  const result: Record<number, string> = {};
  const statuses: Record<string, string> = {};
  const values = taskIDs.filter((id) => id > 0).map((id) => String(id));
  if (!values.length) return { result, statuses };
  const taskField = fieldsMap["TaskID"];
  const statusField = fieldsMap["Status"];
  for (const batch of chunkStrings(values, updateMaxFilterValues)) {
    const filterObj = buildIDFilter(taskField, batch);
    if (!filterObj) continue;
    const items = await searchItems(baseURL, token, ref, filterObj, Math.min(MaxPageSize, Math.max(batch.length, 1)), ignoreView, viewID);
    for (const item of items) {
      const recordID = BitableValueToString(item.record_id).trim();
      const fieldsRaw = item.fields || {};
      const taskID = FieldInt(fieldsRaw, taskField);
      if (recordID && taskID > 0 && !(taskID in result)) result[taskID] = recordID;
    }
    Object.assign(statuses, extractStatusesFromItems(items, statusField));
  }
  return { result, statuses };
}

async function resolveRecordIDsByBizTaskID(baseURL: string, token: string, ref: BitableRef, fieldsMap: Record<string, string>, bizIDs: string[], ignoreView: boolean, viewID: string) {
  const result: Record<string, string> = {};
  const statuses: Record<string, string> = {};
  const values = bizIDs.map((id) => id.trim()).filter(Boolean);
  if (!values.length) return { result, statuses };
  const bizField = fieldsMap["BizTaskID"];
  const statusField = fieldsMap["Status"];
  for (const batch of chunkStrings(values, updateMaxFilterValues)) {
    const filterObj = buildIDFilter(bizField, batch);
    if (!filterObj) continue;
    const items = await searchItems(baseURL, token, ref, filterObj, Math.min(MaxPageSize, Math.max(batch.length, 1)), ignoreView, viewID);
    for (const item of items) {
      const recordID = BitableValueToString(item.record_id).trim();
      const fieldsRaw = item.fields || {};
      const bizID = BitableValueToString(fieldsRaw[bizField]).trim();
      if (recordID && bizID && !(bizID in result)) result[bizID] = recordID;
    }
    Object.assign(statuses, extractStatusesFromItems(items, statusField));
  }
  return { result, statuses };
}

async function fetchRecordStatuses(baseURL: string, token: string, ref: BitableRef, recordIDs: string[], statusField: string) {
  const out: Record<string, string> = {};
  for (const rid of recordIDs.map((r) => r.trim()).filter(Boolean)) {
    if (rid in out) continue;
    const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/${encodeURIComponent(rid)}`;
    const resp = await RequestJSON("GET", urlStr, token, null, true);
    if (resp.code !== 0) throw new Error(`get record failed: code=${resp.code} msg=${resp.msg}`);
    const status = BitableValueToString(resp.data?.record?.fields?.[statusField]).trim();
    if (status) out[rid] = status;
  }
  return out;
}

function hasCdnURL(extra: any) {
  const raw = NormalizeExtra(extra);
  if (!raw.trim()) return false;
  try {
    const payload = JSON.parse(raw);
    const v = payload?.cdn_url;
    return typeof v === "string" && v.trim() !== "";
  } catch {
    return false;
  }
}

function buildUpdateFields(fieldsMap: Record<string, string>, upd: Record<string, any>) {
  const out: Record<string, any> = {};
  const status = BitableValueToString(upd.status).trim();
  if (status && fieldsMap["Status"]) out[fieldsMap["Status"]] = status;
  if (fieldsMap["Date"] && upd.date != null) {
    const [payload, ok] = CoerceDatePayload(upd.date);
    if (ok) out[fieldsMap["Date"]] = payload;
  }
  const deviceSerial = BitableValueToString(upd.device_serial).trim();
  if (deviceSerial && fieldsMap["DispatchedDevice"]) out[fieldsMap["DispatchedDevice"]] = deviceSerial;

  let dispatchedMS: number | null = null;
  if (upd.dispatched_at != null && fieldsMap["DispatchedAt"]) {
    const [ms, ok] = CoerceMillis(upd.dispatched_at);
    if (ok) {
      dispatchedMS = ms;
      out[fieldsMap["DispatchedAt"]] = ms;
    }
  }

  let startMS: number | null = null;
  if (upd.start_at != null && fieldsMap["StartAt"]) {
    const [ms, ok] = CoerceMillis(upd.start_at);
    if (ok) {
      startMS = ms;
      out[fieldsMap["StartAt"]] = ms;
    }
  }
  if (startMS == null && dispatchedMS != null && fieldsMap["StartAt"]) {
    out[fieldsMap["StartAt"]] = dispatchedMS;
    startMS = dispatchedMS;
  }

  let endMS: number | null = null;
  if (upd.completed_at != null) {
    const [ms, ok] = CoerceMillis(upd.completed_at);
    if (ok) endMS = ms;
  }
  if (endMS == null && upd.end_at != null) {
    const [ms, ok] = CoerceMillis(upd.end_at);
    if (ok) endMS = ms;
  }
  if (endMS != null && fieldsMap["EndAt"]) out[fieldsMap["EndAt"]] = endMS;

  let [elapsed, hasElapsed] = CoerceInt(upd.elapsed_seconds);
  if (!hasElapsed && startMS != null && endMS != null) {
    let derived = Math.trunc((endMS - startMS) / 1000);
    if (derived < 0) derived = 0;
    elapsed = derived;
    hasElapsed = true;
  }
  if (hasElapsed && fieldsMap["ElapsedSeconds"]) out[fieldsMap["ElapsedSeconds"]] = elapsed;

  const [itemsCollected, okItems] = CoerceInt(upd.items_collected);
  if (okItems && fieldsMap["ItemsCollected"]) out[fieldsMap["ItemsCollected"]] = itemsCollected;

  const logs = BitableValueToString(upd.logs).trim();
  if (logs && fieldsMap["Logs"]) out[fieldsMap["Logs"]] = logs;

  const [retryCount, okRetry] = CoerceInt(upd.retry_count);
  if (okRetry && fieldsMap["RetryCount"]) out[fieldsMap["RetryCount"]] = retryCount;

  const extra = upd.extra;
  const forceExtra = Boolean(upd.force_extra);
  if (fieldsMap["Extra"] && extra != null) {
    if (forceExtra || (status === "success" && hasCdnURL(extra))) {
      const payload = NormalizeExtra(extra);
      if (payload.trim()) out[fieldsMap["Extra"]] = payload;
    }
  }

  if (upd.fields && typeof upd.fields === "object") {
    for (const [k, v] of Object.entries(upd.fields)) {
      if (k.trim() && v != null) out[k] = v;
    }
  }
  return out;
}

function resolveUpdateRecordID(upd: any, resolvedTask: Record<number, string>, resolvedBiz: Record<string, string>) {
  const recordID = BitableValueToString(upd.record_id).trim();
  if (recordID) return recordID;
  const [taskID, ok] = CoerceInt(upd.task_id);
  if (ok && taskID > 0) return (resolvedTask[taskID] || "").trim();
  const bizID = BitableValueToString(upd.biz_task_id).trim();
  if (bizID) return (resolvedBiz[bizID] || "").trim();
  return "";
}

function parseInputItems(inputPath: string) {
  const raw = readAllInput(inputPath);
  const mode = detectInputFormat(inputPath, raw);
  if (mode === "jsonl") return parseJSONLItems(raw);
  return parseJSONItems(raw);
}

async function UpdateTasks(opts: any) {
  const taskURL = (opts.task_url || "").trim();
  if (!taskURL) {
    errLogger.error("TASK_BITABLE_URL is required");
    return 2;
  }
  const appID = Env("FEISHU_APP_ID", "");
  const appSecret = Env("FEISHU_APP_SECRET", "");
  if (!appID || !appSecret) {
    errLogger.error("FEISHU_APP_ID/FEISHU_APP_SECRET are required");
    return 2;
  }
  const baseURL = Env("FEISHU_BASE_URL", DefaultBaseURL);
  const fieldsMap = LoadTaskFieldsFromEnv();

  let updates: any[] = [];
  if ((opts.input || "").trim()) {
    updates = parseInputItems(opts.input.trim());
  } else {
    updates = [
      {
        task_id: opts.task_id,
        biz_task_id: opts.biz_task_id,
        record_id: opts.record_id,
        status: opts.status,
        device_serial: opts.device_serial,
        dispatched_at: opts.dispatched_at,
        start_at: opts.start_at,
        completed_at: opts.completed_at,
        end_at: opts.end_at,
        elapsed_seconds: opts.elapsed_seconds,
        items_collected: opts.items_collected,
        logs: opts.logs,
        retry_count: opts.retry_count,
        extra: opts.extra,
        date: opts.date,
      },
    ];
  }
  if (!updates.length) {
    errLogger.error("no updates provided");
    return 2;
  }

  let ref: BitableRef;
  try {
    ref = ParseBitableURL(taskURL);
  } catch (err: any) {
    errLogger.error("parse bitable URL failed", { err: err?.message || String(err) });
    return 2;
  }

  let token: string;
  try {
    token = await GetTenantAccessToken(baseURL, appID, appSecret);
  } catch (err: any) {
    errLogger.error("get tenant access token failed", { err: err?.message || String(err) });
    return 2;
  }
  if (!ref.AppToken) {
    if (!ref.WikiToken) {
      errLogger.error("bitable URL missing app_token and wiki_token");
      return 2;
    }
    try {
      ref.AppToken = await ResolveWikiAppToken(baseURL, token, ref.WikiToken);
    } catch (err: any) {
      errLogger.error("resolve wiki app token failed", { err: err?.message || String(err) });
      return 2;
    }
  }

  let viewID = (opts.view_id || "").trim();
  if (!viewID) viewID = ref.ViewID;

  const taskIDsToResolve: number[] = [];
  const bizIDsToResolve: string[] = [];
  for (const upd of updates) {
    const recordID = BitableValueToString(upd.record_id).trim();
    const [taskID, okTask] = CoerceInt(upd.task_id);
    const bizID = BitableValueToString(upd.biz_task_id).trim();
    if (!recordID && okTask && taskID > 0) taskIDsToResolve.push(taskID);
    if (!recordID && !okTask && bizID) bizIDsToResolve.push(bizID);
  }

  let resolvedTask: Record<number, string> = {};
  let resolvedBiz: Record<string, string> = {};
  const statusByRecord: Record<string, string> = {};

  if (taskIDsToResolve.length) {
    try {
      const res = await resolveRecordIDsByTaskID(baseURL, token, ref, fieldsMap, taskIDsToResolve, opts.ignore_view, viewID);
      resolvedTask = res.result;
      Object.assign(statusByRecord, res.statuses);
    } catch (err: any) {
      errLogger.error("resolve record IDs by task id failed", { err: err?.message || String(err) });
      return 2;
    }
  }
  if (bizIDsToResolve.length) {
    try {
      const res = await resolveRecordIDsByBizTaskID(baseURL, token, ref, fieldsMap, bizIDsToResolve, opts.ignore_view, viewID);
      resolvedBiz = res.result;
      Object.assign(statusByRecord, res.statuses);
    } catch (err: any) {
      errLogger.error("resolve record IDs by biz task id failed", { err: err?.message || String(err) });
      return 2;
    }
  }

  const skipStatuses = parseCSVSet(opts.skip_status || "");
  if (Object.keys(skipStatuses).length) {
    const recordIDsNeeded: string[] = [];
    for (const upd of updates) {
      const recordID = resolveUpdateRecordID(upd, resolvedTask, resolvedBiz);
      if (recordID && !(recordID in statusByRecord)) recordIDsNeeded.push(recordID);
    }
    if (recordIDsNeeded.length) {
      try {
        const fetched = await fetchRecordStatuses(baseURL, token, ref, recordIDsNeeded, fieldsMap["Status"]);
        Object.assign(statusByRecord, fetched);
      } catch (err: any) {
        errLogger.error("fetch record statuses failed", { err: err?.message || String(err) });
        return 2;
      }
    }
  }

  const records: { record_id: string; fields: any }[] = [];
  const errorsList: string[] = [];
  let skipped = 0;

  for (const upd of updates) {
    const recordID = resolveUpdateRecordID(upd, resolvedTask, resolvedBiz);
    if (!recordID) {
      const taskID = BitableValueToString(upd.task_id).trim();
      const bizID = BitableValueToString(upd.biz_task_id).trim();
      if (taskID) {
        errorsList.push(`task-id ${taskID} not found`);
      } else if (bizID) {
        errorsList.push(`biz-task-id ${bizID} not found`);
      } else {
        errorsList.push("missing record_id for update");
      }
      continue;
    }
    if (Object.keys(skipStatuses).length) {
      const cur = (statusByRecord[recordID] || "").trim().toLowerCase();
      if (cur && skipStatuses[cur]) {
        skipped++;
        continue;
      }
    }
    const fields = buildUpdateFields(fieldsMap, upd);
    if (!Object.keys(fields).length) {
      errorsList.push(`record ${recordID}: no fields to update`);
      continue;
    }
    records.push({ record_id: recordID, fields });
  }

  const start = Date.now();
  let updated = 0;
  if (records.length) {
    if (records.length === 1) {
      try {
        await updateRecord(baseURL, token, ref, records[0].record_id, records[0].fields);
        updated = 1;
      } catch (err: any) {
        errorsList.push(err?.message || String(err));
      }
    } else {
      for (let i = 0; i < records.length; i += updateMaxBatchSize) {
        const batch = records.slice(i, i + updateMaxBatchSize).map((r) => ({ record_id: r.record_id, fields: r.fields }));
        try {
          await batchUpdateRecords(baseURL, token, ref, batch);
          updated += batch.length;
        } catch (err: any) {
          errorsList.push(err?.message || String(err));
          break;
        }
      }
    }
  }

  const elapsed = Math.floor(((Date.now() - start) / 1000) * 1000) / 1000;
  logger.info("result", {
    data: {
      updated,
      requested: records.length,
      skipped,
      failed: errorsList.length,
      errors: errorsList,
      elapsed_seconds: elapsed,
    },
  });
  return errorsList.length ? 1 : 0;
}

async function getRecordFields(baseURL: string, token: string, ref: BitableRef, recordID: string) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/${encodeURIComponent(recordID)}`;
  const resp = await RequestJSON("GET", urlStr, token, null, true);
  if (resp.code !== 0) throw new Error(`get record failed: code=${resp.code} msg=${resp.msg}`);
  return resp.data?.record?.fields || {};
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function getRecordFieldsByTaskID(baseURL: string, token: string, ref: BitableRef, fieldsMap: Record<string, string>, taskID: number, ignoreView: boolean, viewID: string) {
  if (!taskID || taskID <= 0) return null;
  const taskField = (fieldsMap["TaskID"] || "").trim();
  const filterObj = buildIDFilter(taskField, [String(taskID)]);
  if (!filterObj) return null;
  const items = await searchItems(baseURL, token, ref, filterObj, 1, ignoreView, viewID);
  if (!items.length) return null;
  return items[0]?.fields || null;
}

async function ClaimTask(opts: any) {
  const taskURL = (opts.task_url || "").trim();
  if (!taskURL) {
    errLogger.error("TASK_BITABLE_URL is required");
    return 2;
  }
  const appID = Env("FEISHU_APP_ID", "");
  const appSecret = Env("FEISHU_APP_SECRET", "");
  if (!appID || !appSecret) {
    errLogger.error("FEISHU_APP_ID/FEISHU_APP_SECRET are required");
    return 2;
  }
  const app = (opts.app || "").trim();
  const scene = (opts.scene || "").trim();
  if (!app || !scene) {
    errLogger.error("--app and --scene are required");
    return 2;
  }
  const deviceSerial = (opts.device_serial || "").trim();
  if (!deviceSerial) {
    errLogger.error("--device-serial is required");
    return 2;
  }

  const baseURL = Env("FEISHU_BASE_URL", DefaultBaseURL);
  const fieldsMap = LoadTaskFieldsFromEnv();
  let ref: BitableRef;
  try {
    ref = ParseBitableURL(taskURL);
  } catch (err: any) {
    errLogger.error("parse bitable URL failed", { err: err?.message || String(err) });
    return 2;
  }
  let token: string;
  try {
    token = await GetTenantAccessToken(baseURL, appID, appSecret);
  } catch (err: any) {
    errLogger.error("get tenant access token failed", { err: err?.message || String(err) });
    return 2;
  }
  if (!ref.AppToken) {
    if (!ref.WikiToken) {
      errLogger.error("bitable URL missing app_token and wiki_token");
      return 2;
    }
    try {
      ref.AppToken = await ResolveWikiAppToken(baseURL, token, ref.WikiToken);
    } catch (err: any) {
      errLogger.error("resolve wiki app token failed", { err: err?.message || String(err) });
      return 2;
    }
  }

  let viewID = (opts.view_id || "").trim();
  if (!viewID) viewID = ref.ViewID;

  const statusList = parseCSVList(opts.status || "");
  const candidateStatuses = statusList.length ? statusList : ["pending", "failed"];
  const sceneList = parseCSVList(opts.scene || "");
  const date = (opts.date || "").trim() || "Today";
  const candidateLimit = Number(opts.candidate_limit || 0) > 0 ? Number(opts.candidate_limit) : 5;

  const staleMinutes = Number(opts.stale_minutes || 0) > 0 ? Number(opts.stale_minutes) : 45;
  const staleActionRaw = String(opts.stale_action || "").trim().toLowerCase();
  const staleAction = ["failed", "pending", "log", "skip"].includes(staleActionRaw) ? staleActionRaw : "failed";
  const staleLimit = Number(opts.stale_limit || 0) >= 0 ? Number(opts.stale_limit) : 200;
  const ignoreView = Boolean(opts.ignore_view);
  const fallbackWaitMs = 1000;

  const commonOpts = {
    task_url: taskURL,
    app,
    scene,
    date,
    page_size: 200,
    ignore_view: ignoreView,
    view_id: viewID,
  };

  if (staleMinutes > 0 && staleAction !== "skip") {
    logger.debug("claim: scan stale running tasks", {
      stale_minutes: staleMinutes,
      stale_action: staleAction,
      stale_limit: staleLimit,
    });
    const staleFetch = await FetchTasksForScenesAndStatuses({ ...commonOpts }, sceneList, ["running"], staleLimit);
    if ("err" in staleFetch) return staleFetch.code;
    logger.debug("claim: running tasks fetched", { count: staleFetch.tasks.length });
    const now = Date.now();
    const staleUpdates: { record_id: string; fields: any }[] = [];
    for (const t of staleFetch.tasks) {
      const startValue = t.start_at || t.dispatched_at;
      if (!startValue) continue;
      const ms = parseStaleMillis(startValue);
      if (!ms) continue;
      const ageMinutes = (now - ms) / 60000;
      if (ageMinutes < staleMinutes) continue;
      if (staleAction === "log") continue;
      const fields = buildUpdateFields(fieldsMap, {
        status: staleAction === "pending" ? "pending" : "failed",
        end_at: now,
        logs: "stale running timeout",
      });
      if (Object.keys(fields).length) staleUpdates.push({ record_id: t.record_id, fields });
    }
    for (let i = 0; i < staleUpdates.length; i += updateMaxBatchSize) {
      const batch = staleUpdates.slice(i, i + updateMaxBatchSize);
      try {
        logger.debug("claim: update stale running batch", { count: batch.length });
        await batchUpdateRecords(baseURL, token, ref, batch);
      } catch (err: any) {
        errLogger.error("update stale running tasks failed", { err: err?.message || String(err) });
        return 2;
      }
    }
  }

  logger.debug("claim: fetch candidates", {
    scene: sceneList.length ? sceneList.join(",") : scene,
    status: candidateStatuses.join(","),
    candidate_limit: candidateLimit,
    date,
  });
  const candidates = await FetchTasksForScenesAndStatuses({ ...commonOpts }, sceneList, candidateStatuses, candidateLimit);
  if ("err" in candidates) return candidates.code;
  logger.debug("claim: candidates fetched", { count: candidates.tasks.length });

  for (const t of candidates.tasks) {
    logger.debug("claim: try candidate", { task_id: t.task_id, record_id: t.record_id });
    const updFields = buildUpdateFields(fieldsMap, {
      status: "running",
      device_serial: deviceSerial,
      dispatched_at: "now",
      start_at: "now",
    });
    if (!Object.keys(updFields).length) continue;
    try {
      logger.debug("claim: update candidate", { task_id: t.task_id, record_id: t.record_id });
      await updateRecord(baseURL, token, ref, t.record_id, updFields);
    } catch (err: any) {
      errLogger.error("claim update failed", { err: err?.message || String(err), record_id: t.record_id });
      continue;
    }
    let fields: any = {};
    try {
      logger.debug("claim: verify candidate", { task_id: t.task_id, record_id: t.record_id });
      fields = await getRecordFields(baseURL, token, ref, t.record_id);
    } catch (err: any) {
      errLogger.error("claim verify failed", { err: err?.message || String(err), record_id: t.record_id });
      try {
        logger.debug("claim: verify fallback wait", { task_id: t.task_id, record_id: t.record_id, wait_ms: fallbackWaitMs });
        await sleep(fallbackWaitMs);
        logger.debug("claim: verify fallback search", { task_id: t.task_id, record_id: t.record_id });
        const fallback = await getRecordFieldsByTaskID(baseURL, token, ref, fieldsMap, t.task_id, ignoreView, viewID);
        if (fallback) fields = fallback;
      } catch (fallbackErr: any) {
        errLogger.error("claim verify fallback failed", { err: fallbackErr?.message || String(fallbackErr), record_id: t.record_id });
        continue;
      }
      if (!fields || !Object.keys(fields).length) continue;
    }
    const status = NormalizeBitableValue(fields[fieldsMap["Status"]]).trim().toLowerCase();
    const dispatchedDevice = NormalizeBitableValue(fields[fieldsMap["DispatchedDevice"]]).trim();
    logger.debug("claim: verify result", { task_id: t.task_id, status, dispatched_device: dispatchedDevice });
    if (status === "running" && dispatchedDevice === deviceSerial) {
      logger.info("claimed", { task: t });
      return 0;
    }
  }

  logger.info("claimed", { task: null });
  return 0;
}

async function updateRecord(baseURL: string, token: string, ref: BitableRef, recordID: string, fields: any) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/${encodeURIComponent(recordID)}`;
  const payload = { fields };
  const resp = await RequestJSON("PUT", urlStr, token, payload, true);
  if (resp.code !== 0) throw new Error(`update record failed: code=${resp.code} msg=${resp.msg}`);
}

async function batchUpdateRecords(baseURL: string, token: string, ref: BitableRef, records: any[]) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/batch_update`;
  const payload = { records };
  const resp = await RequestJSON("POST", urlStr, token, payload, true);
  if (resp.code !== 0) throw new Error(`batch update failed: code=${resp.code} msg=${resp.msg}`);
}

function normalizeSkipFields(raw: string) {
  const cleaned = raw.trim();
  if (!cleaned) return [] as string[];
  const parts = cleaned.split(",").map((p) => p.trim()).filter(Boolean);
  const aliases: Record<string, string> = {
    task_id: "TaskID",
    taskid: "TaskID",
    biz_task_id: "BizTaskID",
    biztaskid: "BizTaskID",
    record_id: "RecordID",
    recordid: "RecordID",
    book_id: "BookID",
    bookid: "BookID",
    user_id: "UserID",
    userid: "UserID",
    app: "App",
    scene: "Scene",
  };
  const seen: Record<string, boolean> = {};
  const out: string[] = [];
  for (const p of parts) {
    const key = aliases[p.toLowerCase()] || p;
    if (!key || seen[key]) continue;
    seen[key] = true;
    out.push(key);
  }
  return out;
}

function extractItemValue(item: any, fieldName: string) {
  switch (fieldName) {
    case "TaskID": {
      const [id, ok] = CoerceInt(item.task_id);
      return ok && id > 0 ? String(id) : "";
    }
    case "BizTaskID":
      return BitableValueToString(item.biz_task_id).trim();
    case "RecordID":
      return BitableValueToString(item.record_id).trim();
    case "BookID":
      return BitableValueToString(item.book_id).trim();
    case "UserID":
      return BitableValueToString(item.user_id).trim();
    case "App":
      return BitableValueToString(item.app).trim();
    case "Scene":
      return BitableValueToString(item.scene).trim();
    default:
      return BitableValueToString(item[fieldName]).trim();
  }
}

async function CreateTasks(opts: any) {
  const taskURL = (opts.task_url || "").trim();
  if (!taskURL) {
    errLogger.error("TASK_BITABLE_URL is required");
    return 2;
  }
  const appID = Env("FEISHU_APP_ID", "");
  const appSecret = Env("FEISHU_APP_SECRET", "");
  if (!appID || !appSecret) {
    errLogger.error("FEISHU_APP_ID/FEISHU_APP_SECRET are required");
    return 2;
  }
  const baseURL = Env("FEISHU_BASE_URL", DefaultBaseURL);
  const fieldsMap = LoadTaskFieldsFromEnv();

  let creates: any[] = [];
  if ((opts.input || "").trim()) {
    creates = parseInputItems(opts.input.trim());
  } else {
    creates = [
      {
        biz_task_id: opts.biz_task_id,
        parent_task_id: opts.parent_task_id,
        app: opts.app,
        scene: opts.scene,
        params: opts.params,
        item_id: opts.item_id,
        book_id: opts.book_id,
        url: opts.url,
        user_id: opts.user_id,
        user_name: opts.user_name,
        date: opts.date,
        status: opts.status,
        device_serial: opts.device_serial,
        dispatched_device: opts.dispatched_device,
        dispatched_at: opts.dispatched_at,
        start_at: opts.start_at,
        completed_at: opts.completed_at,
        end_at: opts.end_at,
        elapsed_seconds: opts.elapsed_seconds,
        items_collected: opts.items_collected,
        logs: opts.logs,
        retry_count: opts.retry_count,
        last_screenshot: opts.last_screenshot,
        group_id: opts.group_id,
        extra: opts.extra,
        record_id: "",
      },
    ];
  }
  if (!creates.length) {
    errLogger.error("no tasks provided");
    return 2;
  }

  let ref: BitableRef;
  try {
    ref = ParseBitableURL(taskURL);
  } catch (err: any) {
    errLogger.error("parse bitable URL failed", { err: err?.message || String(err) });
    return 2;
  }
  let token: string;
  try {
    token = await GetTenantAccessToken(baseURL, appID, appSecret);
  } catch (err: any) {
    errLogger.error("get tenant access token failed", { err: err?.message || String(err) });
    return 2;
  }
  if (!ref.AppToken) {
    if (!ref.WikiToken) {
      errLogger.error("bitable URL missing app_token and wiki_token");
      return 2;
    }
    try {
      ref.AppToken = await ResolveWikiAppToken(baseURL, token, ref.WikiToken);
    } catch (err: any) {
      errLogger.error("resolve wiki app token failed", { err: err?.message || String(err) });
      return 2;
    }
  }

  const skipFields = normalizeSkipFields(opts.skip_existing || "");
  const existingByField: Record<string, Record<string, string>> = {};
  const existingRecordIDs: Record<string, boolean> = {};

  if (skipFields.length) {
    const fieldMap: Record<string, string> = {};
    for (const f of skipFields) {
      if (f === "RecordID") continue;
      fieldMap[f] = fieldsMap[f] || f;
    }
    for (const item of creates) {
      for (const f of skipFields) {
        if (f === "RecordID") {
          const rid = BitableValueToString(item.record_id).trim();
          if (rid && !existingRecordIDs[rid]) {
            if (await recordExists(baseURL, token, ref, rid)) existingRecordIDs[rid] = true;
          }
          continue;
        }
        const val = extractItemValue(item, f);
        if (!val) continue;
        if (!existingByField[f]) existingByField[f] = {};
        existingByField[f][val] = "";
      }
    }
    for (const [f, valuesMap] of Object.entries(existingByField)) {
      const values = Object.keys(valuesMap);
      const mappedField = fieldMap[f];
      const resolved = await resolveExistingByField(baseURL, token, ref, mappedField, values);
      existingByField[f] = resolved;
    }
  }

  const records: { fields: any }[] = [];
  const errorsList: string[] = [];
  let skipped = 0;

  for (const item of creates) {
    if (skipFields.length) {
      let allMatch = true;
      for (const f of skipFields) {
        if (f === "RecordID") {
          const rid = BitableValueToString(item.record_id).trim();
          if (!rid || !existingRecordIDs[rid]) {
            allMatch = false;
            break;
          }
          continue;
        }
        const val = extractItemValue(item, f);
        if (!val || !existingByField[f]?.[val]) {
          allMatch = false;
          break;
        }
      }
      if (allMatch) {
        skipped++;
        continue;
      }
    }
    const fields = buildCreateFields(fieldsMap, item);
    if (!Object.keys(fields).length) {
      errorsList.push("task: no fields to create");
      continue;
    }
    records.push({ fields });
  }

  const start = Date.now();
  let created = 0;
  if (records.length) {
    if (records.length === 1) {
      try {
        await createRecord(baseURL, token, ref, records[0].fields);
        created = 1;
      } catch (err: any) {
        errorsList.push(err?.message || String(err));
      }
    } else {
      for (let i = 0; i < records.length; i += createMaxBatchSize) {
        const batch = records.slice(i, i + createMaxBatchSize).map((r) => ({ fields: r.fields }));
        try {
          await batchCreateRecords(baseURL, token, ref, batch);
          created += batch.length;
        } catch (err: any) {
          errorsList.push(err?.message || String(err));
          break;
        }
      }
    }
  }

  const elapsed = Math.floor(((Date.now() - start) / 1000) * 1000) / 1000;
  logger.info("result", {
    data: {
      created,
      requested: records.length,
      skipped,
      failed: errorsList.length,
      errors: errorsList,
      elapsed_seconds: elapsed,
    },
  });
  return errorsList.length ? 1 : 0;
}

function buildCreateFields(fieldsMap: Record<string, string>, item: any) {
  const out: Record<string, any> = {};
  const setStr = (jsonKey: string, colKey: string) => {
    const v = BitableValueToString(item[jsonKey]).trim();
    if (!v) return;
    const col = (fieldsMap[colKey] || "").trim();
    if (!col) return;
    out[col] = v;
  };
  setStr("biz_task_id", "BizTaskID");
  setStr("parent_task_id", "ParentTaskID");

  const appValue = BitableValueToString(item.app).trim();
  const sceneValue = BitableValueToString(item.scene).trim();
  const paramsValue = BitableValueToString(item.params).trim();
  const itemIDValue = BitableValueToString(item.item_id).trim();
  const bookIDValue = BitableValueToString(item.book_id).trim();
  const urlValue = BitableValueToString(item.url).trim();
  const userIDValue = BitableValueToString(item.user_id).trim();
  const userNameValue = BitableValueToString(item.user_name).trim();
  const statusValue = BitableValueToString(item.status).trim();
  const logsValue = BitableValueToString(item.logs).trim();
  const lastScreenshotValue = BitableValueToString(item.last_screenshot).trim();
  const groupIDValue = BitableValueToString(item.group_id).trim();

  const kvs: Array<[string, string]> = [
    ["App", appValue],
    ["Scene", sceneValue],
    ["Params", paramsValue],
    ["ItemID", itemIDValue],
    ["BookID", bookIDValue],
    ["URL", urlValue],
    ["UserID", userIDValue],
    ["UserName", userNameValue],
    ["Status", statusValue],
    ["Logs", logsValue],
    ["LastScreenShot", lastScreenshotValue],
    ["GroupID", groupIDValue],
  ];
  for (const [field, value] of kvs) {
    if (!value) continue;
    const col = (fieldsMap[field] || "").trim();
    if (col) out[col] = value;
  }

  if (!groupIDValue && appValue && bookIDValue && userIDValue && (fieldsMap["GroupID"] || "").trim()) {
    const label = appGroupLabels[appValue] || appValue;
    out[fieldsMap["GroupID"]] = `${label}_${bookIDValue}_${userIDValue}`;
  }

  if (fieldsMap["Date"] && item.date != null) {
    const [payload, ok] = CoerceDatePayload(item.date);
    if (ok) out[fieldsMap["Date"]] = payload;
  }

  const deviceSerial = BitableValueToString(item.device_serial).trim();
  if (deviceSerial && fieldsMap["DeviceSerial"]) out[fieldsMap["DeviceSerial"]] = deviceSerial;

  let dispatchedDevice = BitableValueToString(item.dispatched_device).trim();
  if (!dispatchedDevice) dispatchedDevice = deviceSerial;
  if (dispatchedDevice && fieldsMap["DispatchedDevice"]) out[fieldsMap["DispatchedDevice"]] = dispatchedDevice;

  let dispatchedMS: number | null = null;
  if (item.dispatched_at != null && fieldsMap["DispatchedAt"]) {
    const [ms, ok] = CoerceMillis(item.dispatched_at);
    if (ok) {
      dispatchedMS = ms;
      out[fieldsMap["DispatchedAt"]] = ms;
    }
  }

  let startMS: number | null = null;
  if (item.start_at != null && fieldsMap["StartAt"]) {
    const [ms, ok] = CoerceMillis(item.start_at);
    if (ok) {
      startMS = ms;
      out[fieldsMap["StartAt"]] = ms;
    }
  }
  if (startMS == null && dispatchedMS != null && fieldsMap["StartAt"]) {
    out[fieldsMap["StartAt"]] = dispatchedMS;
    startMS = dispatchedMS;
  }

  let endMS: number | null = null;
  if (item.completed_at != null) {
    const [ms, ok] = CoerceMillis(item.completed_at);
    if (ok) endMS = ms;
  }
  if (endMS == null && item.end_at != null) {
    const [ms, ok] = CoerceMillis(item.end_at);
    if (ok) endMS = ms;
  }
  if (endMS != null && fieldsMap["EndAt"]) out[fieldsMap["EndAt"]] = endMS;

  let [elapsed, hasElapsed] = CoerceInt(item.elapsed_seconds);
  if (!hasElapsed && startMS != null && endMS != null) {
    let derived = Math.trunc((endMS - startMS) / 1000);
    if (derived < 0) derived = 0;
    elapsed = derived;
    hasElapsed = true;
  }
  if (hasElapsed && fieldsMap["ElapsedSeconds"]) out[fieldsMap["ElapsedSeconds"]] = elapsed;

  const [itemsCollected, okItems] = CoerceInt(item.items_collected);
  if (okItems && fieldsMap["ItemsCollected"]) out[fieldsMap["ItemsCollected"]] = itemsCollected;

  const [retryCount, okRetry] = CoerceInt(item.retry_count);
  if (okRetry && fieldsMap["RetryCount"]) out[fieldsMap["RetryCount"]] = retryCount;

  const extra = item.extra;
  const forceExtra = Boolean(item.force_extra);
  if (fieldsMap["Extra"] && extra != null) {
    const payload = NormalizeExtra(extra);
    if (payload.trim() || forceExtra) out[fieldsMap["Extra"]] = payload;
  }

  if (item.fields && typeof item.fields === "object") {
    for (const [k, v] of Object.entries(item.fields)) {
      if (k.trim() && v != null) out[k] = v;
    }
  }
  return out;
}

async function batchCreateRecords(baseURL: string, token: string, ref: BitableRef, records: any[]) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/batch_create`;
  const payload = { records };
  const resp = await RequestJSON("POST", urlStr, token, payload, true);
  if (resp.code !== 0) throw new Error(`batch create failed: code=${resp.code} msg=${resp.msg}`);
}

async function createRecord(baseURL: string, token: string, ref: BitableRef, fields: any) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records`;
  const payload = { fields };
  const resp = await RequestJSON("POST", urlStr, token, payload, true);
  if (resp.code !== 0) throw new Error(`create record failed: code=${resp.code} msg=${resp.msg}`);
}

async function resolveExistingByField(baseURL: string, token: string, ref: BitableRef, fieldName: string, values: string[]) {
  const out: Record<string, string> = {};
  if (!values.length) return out;
  for (const batch of chunkStrings(values, createMaxFilterValues)) {
    const filterObj = buildIDFilter(fieldName, batch);
    if (!filterObj) continue;
    const items = await fetchRecordsForCreate(baseURL, token, ref, filterObj, Math.min(MaxPageSize, Math.max(batch.length, 1)));
    for (const item of items) {
      const recordID = BitableValueToString(item.record_id).trim();
      const fieldsRaw = item.fields || {};
      const val = BitableValueToString(fieldsRaw[fieldName]).trim();
      if (recordID && val && !(val in out)) out[val] = recordID;
    }
  }
  return out;
}

async function fetchRecordsForCreate(baseURL: string, token: string, ref: BitableRef, filterObj: any, pageSize: number) {
  const size = ClampPageSize(pageSize);
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/search?page_size=${size}`;
  const body = filterObj ? { filter: filterObj } : null;
  const resp = await RequestJSON("POST", urlStr, token, body, true);
  if (resp.code !== 0) throw new Error(`search records failed: code=${resp.code} msg=${resp.msg}`);
  return resp.data?.items || [];
}

async function recordExists(baseURL: string, token: string, ref: BitableRef, recordID: string) {
  const rid = recordID.trim();
  if (!rid) return false;
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/bitable/v1/apps/${ref.AppToken}/tables/${ref.TableID}/records/${encodeURIComponent(rid)}`;
  try {
    const resp = await RequestJSON("GET", urlStr, token, null, true);
    return resp.code === 0;
  } catch {
    return false;
  }
}

function chunkStrings(values: string[], size: number) {
  if (size <= 0) return [values];
  const out: string[][] = [];
  for (let i = 0; i < values.length; i += size) out.push(values.slice(i, i + size));
  return out;
}

async function main() {
  const argv = process.argv.slice(2);
  const program = new Command();
  program
    .name("bitable-task")
    .description("Feishu Bitable task manager")
    .showHelpAfterError()
    .showSuggestionAfterError()
    .option("--log-json", "Output logs in JSON")
    .option("--log-level <level>", "Log level: debug|info|error (default: info)");

  const ensureGlobal = () => {
    getGlobalOptions(program);
  };

  program
    .command("fetch")
    .description("Fetch tasks from Bitable")
    .option("--task-url <url>", "Bitable task table URL")
    .option("--task-id <csv>", "Fetch by TaskID(s), comma-separated (e.g. 111 or 111,222,333)")
    .option("--biz-task-id <id>", "Fetch by biz task id")
    .option("--group-id <csv>", "Fetch by GroupID(s), comma-separated (e.g. g1 or g1,g2)")
    .option("--app <value>", "App value for filter (required)")
    .option("--scene <value>", "Scene value for filter (required)")
    .option("--status <value>", "Task status filter; supports comma-separated priority list (default: pending)")
    .option("--date <value>", "Date preset: Today/Yesterday/Any")
    .option("--limit <n>", "Max tasks to return (0 = no cap)")
    .option("--page-size <n>", "Page size (max 500)")
    .option("--max-pages <n>", "Max pages to fetch (0 = no cap)")
    .option("--ignore-view", "Ignore view_id when searching (default: true)")
    .option("--use-view", "Use view_id from URL")
    .option("--view-id <id>", "Override view_id when searching")
    .option("--jsonl", "Output JSONL (one task per line)")
    .option("--raw", "Include raw fields in output")
    .action(async (options) => {
      ensureGlobal();
      const opts: any = {
        task_url: process.env.TASK_BITABLE_URL || "",
        status: "pending",
        date: "Today",
        page_size: 200,
        ignore_view: true,
      };
      if (options.taskUrl) opts.task_url = options.taskUrl;
      if (options.status) opts.status = options.status;
      if (options.date) opts.date = options.date;
      if (options.pageSize) opts.page_size = options.pageSize;
      if (options.limit) opts.limit = options.limit;
      if (options.maxPages) opts.max_pages = options.maxPages;
      if (options.ignoreView) opts.ignore_view = true;
      if (options.useView) opts.ignore_view = false;
      if (options.viewId) opts.view_id = options.viewId;
      if (options.jsonl) opts.jsonl = true;
      if (options.raw) opts.raw = true;
      if (options.app) opts.app = options.app;
      if (options.scene) opts.scene = options.scene;
      if (options.taskId) opts.task_id = options.taskId;
      if (options.bizTaskId) opts.biz_task_id = options.bizTaskId;
      if (options.groupId) opts.group_id = options.groupId;
      if (!opts.app || !opts.scene) {
        if (!opts.task_id && !opts.biz_task_id && !opts.group_id) {
          errLogger.error("--app and --scene are required (or use --task-id/--biz-task-id/--group-id)");
          process.exit(2);
        }
      }
      process.exit(await FetchTasks(opts));
    });

  program
    .command("update")
    .description("Update tasks in Bitable")
    .option("--task-url <url>", "Bitable task table URL")
    .option("--input <path>", "Input JSON/JSONL file (use - for stdin)")
    .option("--task-id <id>", "Single task id to update")
    .option("--biz-task-id <id>", "Single biz task id to update")
    .option("--record-id <id>", "Single record id to update")
    .option("--status <value>", "Status to set")
    .option("--date <value>", "Date to set (string or epoch/ISO)")
    .option("--device-serial <val>", "Dispatched device serial")
    .option("--dispatched-at <val>", "Dispatch time (ms/seconds/ISO/now)")
    .option("--start-at <val>", "Start time (ms/seconds/ISO)")
    .option("--completed-at <val>", "Completion time (ms/seconds/ISO)")
    .option("--end-at <val>", "End time (ms/seconds/ISO)")
    .option("--elapsed-seconds <val>", "Elapsed seconds (int)")
    .option("--items-collected <val>", "Items collected (int)")
    .option("--logs <val>", "Logs path or identifier")
    .option("--retry-count <val>", "Retry count (int)")
    .option("--extra <json>", "Extra JSON string")
    .option("--skip-status <csv>", "Skip updates when current status matches")
    .option("--ignore-view", "Ignore view_id when searching (default: true)")
    .option("--use-view", "Use view_id from URL")
    .option("--view-id <id>", "Override view_id when searching")
    .action(async (options) => {
      ensureGlobal();
      const opts: any = {
        task_url: process.env.TASK_BITABLE_URL || "",
        ignore_view: true,
      };
      if (options.taskUrl) opts.task_url = options.taskUrl;
      if (options.input) opts.input = options.input;
      if (options.taskId) opts.task_id = options.taskId;
      if (options.bizTaskId) opts.biz_task_id = options.bizTaskId;
      if (options.recordId) opts.record_id = options.recordId;
      if (options.status) opts.status = options.status;
      if (options.date) opts.date = options.date;
      if (options.deviceSerial) opts.device_serial = options.deviceSerial;
      if (options.dispatchedAt) opts.dispatched_at = options.dispatchedAt;
      if (options.startAt) opts.start_at = options.startAt;
      if (options.completedAt) opts.completed_at = options.completedAt;
      if (options.endAt) opts.end_at = options.endAt;
      if (options.elapsedSeconds) opts.elapsed_seconds = options.elapsedSeconds;
      if (options.itemsCollected) opts.items_collected = options.itemsCollected;
      if (options.logs) opts.logs = options.logs;
      if (options.retryCount) opts.retry_count = options.retryCount;
      if (options.extra) opts.extra = options.extra;
      if (options.skipStatus) opts.skip_status = options.skipStatus;
      if (options.ignoreView) opts.ignore_view = true;
      if (options.useView) opts.ignore_view = false;
      if (options.viewId) opts.view_id = options.viewId;
      process.exit(await UpdateTasks(opts));
    });

  program
    .command("create")
    .description("Create tasks in Bitable")
    .option("--task-url <url>", "Bitable task table URL")
    .option("--input <path>", "Input JSON/JSONL file (use - for stdin)")
    .option("--biz-task-id <id>", "Biz task id to create")
    .option("--parent-task-id <id>", "Parent task id")
    .option("--app <value>", "App value")
    .option("--scene <value>", "Scene value")
    .option("--params <value>", "Task params")
    .option("--item-id <value>", "Item id")
    .option("--book-id <value>", "Book id")
    .option("--url <value>", "URL")
    .option("--user-id <value>", "User id")
    .option("--user-name <value>", "User name")
    .option("--date <value>", "Date value (string or epoch/ISO)")
    .option("--status <value>", "Status")
    .option("--device-serial <val>", "Dispatched device serial")
    .option("--dispatched-device <val>", "Dispatched device (override device-serial)")
    .option("--dispatched-at <val>", "Dispatch time (ms/seconds/ISO/now)")
    .option("--start-at <val>", "Start time (ms/seconds/ISO)")
    .option("--completed-at <val>", "Completion time (ms/seconds/ISO)")
    .option("--end-at <val>", "End time (ms/seconds/ISO)")
    .option("--elapsed-seconds <val>", "Elapsed seconds (int)")
    .option("--items-collected <val>", "Items collected (int)")
    .option("--logs <val>", "Logs path or identifier")
    .option("--retry-count <val>", "Retry count (int)")
    .option("--last-screenshot <val>", "Last screenshot reference")
    .option("--group-id <val>", "Group id")
    .option("--extra <json>", "Extra JSON string")
    .option("--skip-existing <csv>", "Skip create when existing records match fields")
    .option("--ignore-view", "Ignore view_id when searching (default: true)")
    .option("--use-view", "Use view_id from URL")
    .option("--view-id <id>", "Override view_id when searching")
    .action(async (options) => {
      ensureGlobal();
      const opts: any = {
        task_url: process.env.TASK_BITABLE_URL || "",
      };
      if (options.taskUrl) opts.task_url = options.taskUrl;
      if (options.input) opts.input = options.input;
      if (options.bizTaskId) opts.biz_task_id = options.bizTaskId;
      if (options.parentTaskId) opts.parent_task_id = options.parentTaskId;
      if (options.app) opts.app = options.app;
      if (options.scene) opts.scene = options.scene;
      if (options.params) opts.params = options.params;
      if (options.itemId) opts.item_id = options.itemId;
      if (options.bookId) opts.book_id = options.bookId;
      if (options.url) opts.url = options.url;
      if (options.userId) opts.user_id = options.userId;
      if (options.userName) opts.user_name = options.userName;
      if (options.date) opts.date = options.date;
      if (options.status) opts.status = options.status;
      if (options.deviceSerial) opts.device_serial = options.deviceSerial;
      if (options.dispatchedDevice) opts.dispatched_device = options.dispatchedDevice;
      if (options.dispatchedAt) opts.dispatched_at = options.dispatchedAt;
      if (options.startAt) opts.start_at = options.startAt;
      if (options.completedAt) opts.completed_at = options.completedAt;
      if (options.endAt) opts.end_at = options.endAt;
      if (options.elapsedSeconds) opts.elapsed_seconds = options.elapsedSeconds;
      if (options.itemsCollected) opts.items_collected = options.itemsCollected;
      if (options.logs) opts.logs = options.logs;
      if (options.retryCount) opts.retry_count = options.retryCount;
      if (options.lastScreenshot) opts.last_screenshot = options.lastScreenshot;
      if (options.groupId) opts.group_id = options.groupId;
      if (options.extra) opts.extra = options.extra;
      if (options.skipExisting) opts.skip_existing = options.skipExisting;
      if (options.ignoreView) opts.ignore_view = true;
      if (options.useView) opts.ignore_view = false;
      if (options.viewId) opts.view_id = options.viewId;
      process.exit(await CreateTasks(opts));
    });

  program
    .command("claim")
    .description("Claim one task with optimistic lock and device binding")
    .option("--task-url <url>", "Bitable task table URL")
    .option("--app <value>", "App value for filter (required)")
    .option("--scene <value>", "Scene value for filter (required)")
    .option("--status <value>", "Task status filter; supports comma-separated priority list (default: pending,failed)")
    .option("--date <value>", "Date preset: Today/Yesterday/Any")
    .option("--device-serial <val>", "Device serial to bind (required)")
    .option("--candidate-limit <n>", "Max candidates to attempt (default: 5)")
    .option("--stale-minutes <n>", "Minutes to mark running tasks as stale (default: 45)")
    .option("--stale-action <value>", "Stale action: failed|pending|log|skip (default: failed)")
    .option("--stale-limit <n>", "Max running tasks to scan (default: 200; 0 = no cap)")
    .option("--ignore-view", "Ignore view_id when searching (default: true)")
    .option("--use-view", "Use view_id from URL")
    .option("--view-id <id>", "Override view_id when searching")
    .action(async (options) => {
      ensureGlobal();
      const opts: any = {
        task_url: process.env.TASK_BITABLE_URL || "",
        status: "pending,failed",
        date: "Today",
        candidate_limit: 5,
        stale_minutes: 45,
        stale_action: "failed",
        stale_limit: 200,
        ignore_view: true,
      };
      if (options.taskUrl) opts.task_url = options.taskUrl;
      if (options.app) opts.app = options.app;
      if (options.scene) opts.scene = options.scene;
      if (options.status) opts.status = options.status;
      if (options.date) opts.date = options.date;
      if (options.deviceSerial) opts.device_serial = options.deviceSerial;
      if (options.candidateLimit) opts.candidate_limit = options.candidateLimit;
      if (options.staleMinutes) opts.stale_minutes = options.staleMinutes;
      if (options.staleAction) opts.stale_action = options.staleAction;
      if (options.staleLimit != null) opts.stale_limit = options.staleLimit;
      if (options.ignoreView) opts.ignore_view = true;
      if (options.useView) opts.ignore_view = false;
      if (options.viewId) opts.view_id = options.viewId;
      process.exit(await ClaimTask(opts));
    });

  if (argv.length === 0) {
    program.outputHelp();
    process.exit(0);
  }
  await program.parseAsync(process.argv);
}
main().catch((err) => {
  errLogger.error("unhandled error", { err: err?.message || String(err) });
  process.exit(1);
});
