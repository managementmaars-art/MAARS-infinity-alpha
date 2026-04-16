import * as fs from "node:fs";
import * as path from "node:path";

export const DefaultBaseURL = "https://open.feishu.cn";
export const DefaultPageSize = 200;
export const MaxPageSize = 500;

export const TaskFieldEnvMap: Record<string, string> = {
  TASK_FIELD_TASKID: "TaskID",
  TASK_FIELD_BIZ_TASK_ID: "BizTaskID",
  TASK_FIELD_PARENT_TASK_ID: "ParentTaskID",
  TASK_FIELD_APP: "App",
  TASK_FIELD_SCENE: "Scene",
  TASK_FIELD_PARAMS: "Params",
  TASK_FIELD_ITEMID: "ItemID",
  TASK_FIELD_BOOKID: "BookID",
  TASK_FIELD_URL: "URL",
  TASK_FIELD_USERID: "UserID",
  TASK_FIELD_USERNAME: "UserName",
  TASK_FIELD_DATE: "Date",
  TASK_FIELD_STATUS: "Status",
  TASK_FIELD_LOGS: "Logs",
  TASK_FIELD_LAST_SCREEN_SHOT: "LastScreenShot",
  TASK_FIELD_GROUPID: "GroupID",
  TASK_FIELD_DEVICE_SERIAL: "DeviceSerial",
  TASK_FIELD_DISPATCHED_DEVICE: "DispatchedDevice",
  TASK_FIELD_DISPATCHED_AT: "DispatchedAt",
  TASK_FIELD_START_AT: "StartAt",
  TASK_FIELD_END_AT: "EndAt",
  TASK_FIELD_ELAPSED_SECONDS: "ElapsedSeconds",
  TASK_FIELD_ITEMS_COLLECTED: "ItemsCollected",
  TASK_FIELD_EXTRA: "Extra",
  TASK_FIELD_RETRYCOUNT: "RetryCount",
};

export type BitableRef = {
  RawURL: string;
  AppToken: string;
  TableID: string;
  ViewID: string;
  WikiToken: string;
};

export function Env(name: string, def: string) {
  const v = (process.env[name] || "").trim();
  return v === "" ? def : v;
}

export function ClampPageSize(size: number) {
  if (!size || size <= 0) return DefaultPageSize;
  if (size > MaxPageSize) return MaxPageSize;
  return size;
}

function firstQueryValue(q: URLSearchParams, keys: string[]) {
  for (const k of keys) {
    const vals = q.getAll(k);
    for (const v of vals) {
      const val = v.trim();
      if (val) return val;
    }
  }
  return "";
}

export function ParseBitableURL(raw: string): BitableRef {
  const trimmed = raw.trim();
  if (!trimmed) throw new Error("bitable url is empty");
  let normalized = trimmed.replace(/\\([?&=])/g, "$1");
  if (normalized !== trimmed) {
    // preserve original for error reporting
  }
  let u: URL;
  try {
    u = new URL(normalized);
  } catch (err) {
    // fallback to raw input if normalization breaks URL parsing
    u = new URL(trimmed);
  }
  if (!u.protocol) throw new Error("bitable url missing scheme");
  const segments = u.pathname.split("/").filter((s) => s);
  let appToken = "";
  let wikiToken = "";
  for (let i = 0; i < segments.length - 1; i++) {
    if (segments[i] === "base") {
      appToken = segments[i + 1];
      break;
    }
    if (segments[i] === "wiki") wikiToken = segments[i + 1];
  }
  if (!appToken && !wikiToken && segments.length > 0) appToken = segments[segments.length - 1];
  const q = u.searchParams;
  const tableID = firstQueryValue(q, ["table", "tableId", "table_id"]);
  const viewID = firstQueryValue(q, ["view", "viewId", "view_id"]);
  if (!tableID) throw new Error("missing table_id in bitable url query");
  return { RawURL: trimmed, AppToken: appToken, TableID: tableID, ViewID: viewID, WikiToken: wikiToken };
}

export function LoadTaskFieldsFromEnv() {
  const fields: Record<string, string> = {};
  for (const v of Object.values(TaskFieldEnvMap)) fields[v] = v;
  for (const [envName, defName] of Object.entries(TaskFieldEnvMap)) {
    const o = Env(envName, "");
    if (o) fields[defName] = o;
  }
  return fields;
}

export async function RequestJSON(method: string, urlStr: string, token: string, payload: any, out?: any) {
  const body = payload != null ? JSON.stringify(payload) : undefined;
  const resp = await fetch(urlStr, {
    method,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body,
  });
  const raw = await resp.text();
  if (Math.floor(resp.status / 100) !== 2) {
    throw new Error(`http ${resp.status}: ${raw}`);
  }
  if (!out) return null;
  return JSON.parse(raw);
}

export async function GetTenantAccessToken(baseURL: string, appID: string, appSecret: string) {
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/auth/v3/tenant_access_token/internal`;
  const payload = { app_id: appID, app_secret: appSecret };
  const resp = (await RequestJSON("POST", urlStr, "", payload, true)) as any;
  if (resp.code !== 0) throw new Error(`tenant token error: code=${resp.code} msg=${resp.msg}`);
  const tok = String(resp.tenant_access_token || "").trim();
  if (!tok) throw new Error("tenant token missing in response");
  return tok;
}

export async function ResolveWikiAppToken(baseURL: string, token: string, wikiToken: string) {
  const wt = wikiToken.trim();
  if (!wt) throw new Error("wiki token is empty");
  const urlStr = `${baseURL.replace(/\/+$/, "")}/open-apis/wiki/v2/spaces/get_node?token=${encodeURIComponent(wt)}`;
  const resp = (await RequestJSON("GET", urlStr, token, null, true)) as any;
  if (resp.code !== 0) throw new Error(`wiki node error: code=${resp.code} msg=${resp.msg}`);
  const objType = String(resp?.data?.node?.obj_type || "").trim();
  if (objType !== "bitable") throw new Error(`wiki node obj_type is ${objType}, not bitable`);
  const objToken = String(resp?.data?.node?.obj_token || "").trim();
  if (!objToken) throw new Error("wiki node obj_token missing");
  return objToken;
}

export function NormalizeBitableValue(v: any): string {
  if (v === null || v === undefined) return "";
  if (typeof v === "string") return v.trim();
  if (Buffer.isBuffer(v)) return v.toString().trim();
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "number") {
    if (Number.isFinite(v) && Math.floor(v) === v) return String(v);
    return String(v);
  }
  if (Array.isArray(v)) {
    if (isRichTextArray(v)) return joinRichText(v);
    const parts = v.map((it) => NormalizeBitableValue(it).trim()).filter(Boolean);
    return parts.join(",");
  }
  if (typeof v === "object") {
    for (const k of ["value", "values", "elements", "content"]) {
      if (k in v) {
        const s = NormalizeBitableValue((v as any)[k]).trim();
        if (s) return s;
      }
    }
    if (typeof (v as any).text === "string") {
      const s = (v as any).text.trim();
      if (s) return s;
    }
    for (const k of ["link", "name", "en_name", "email", "id", "user_id", "url", "tmp_url", "file_token"]) {
      if (k in v) {
        const s = NormalizeBitableValue((v as any)[k]).trim();
        if (s) return s;
      }
    }
    if ((v as any).address !== undefined || (v as any).location != null || (v as any).pname != null || (v as any).cityname != null || (v as any).adname != null) {
      const parts = [
        NormalizeBitableValue((v as any).location).trim(),
        NormalizeBitableValue((v as any).pname).trim(),
        NormalizeBitableValue((v as any).cityname).trim(),
        NormalizeBitableValue((v as any).adname).trim(),
      ].filter(Boolean);
      if (parts.length) return parts.join(",");
    }
    return marshalJSONNoEscape(v as any);
  }
  return String(v).trim();
}

export function BitableValueToString(v: any) {
  return NormalizeBitableValue(v).trim();
}

function isRichTextArray(items: any[]) {
  return items.some((it) => typeof it === "object" && it !== null && "text" in it);
}

function joinRichText(items: any[]) {
  const parts: string[] = [];
  for (const it of items) {
    if (typeof it === "object" && it !== null) {
      if (typeof (it as any).text === "string" && (it as any).text.trim()) {
        parts.push((it as any).text.trim());
        continue;
      }
      if ((it as any).value !== undefined) {
        const s = NormalizeBitableValue((it as any).value).trim();
        if (s) {
          parts.push(s);
          continue;
        }
      }
    }
    const s = NormalizeBitableValue(it).trim();
    if (s) parts.push(s);
  }
  return parts.join(" ");
}

export function FieldInt(fields: Record<string, any>, name: string) {
  const raw = BitableValueToString(fields[name]);
  if (!raw) return 0;
  const f = Number(raw);
  if (!Number.isFinite(f)) return 0;
  return Math.trunc(f);
}

export function CoerceInt(v: any): [number, boolean] {
  if (v === null || v === undefined) return [0, false];
  if (typeof v === "boolean") return [0, false];
  if (typeof v === "number") return [Math.trunc(v), true];
  if (typeof v === "string") {
    const s = v.trim();
    if (!s) return [0, false];
    const n = Number(s);
    if (!Number.isFinite(n)) return [0, false];
    return [Math.trunc(n), true];
  }
  return [0, false];
}

function parseDateLocal(raw: string): Date | null {
  const m1 = raw.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (m1) {
    const [_, y, mo, d] = m1;
    return new Date(Number(y), Number(mo) - 1, Number(d), 0, 0, 0);
  }
  const m2 = raw.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2}):(\d{2})(?:\.(\d+))?$/);
  if (m2) {
    const [_, y, mo, d, hh, mm, ss, ms] = m2;
    const msNum = ms ? Number(ms.slice(0, 3).padEnd(3, "0")) : 0;
    return new Date(Number(y), Number(mo) - 1, Number(d), Number(hh), Number(mm), Number(ss), msNum);
  }
  return null;
}

export function ParseDatetime(raw: string): [Date, boolean] {
  const t = raw.trim();
  if (!t) return [new Date(0), false];
  let val = t;
  if (val.endsWith("Z")) val = val.slice(0, -1) + "+00:00";
  let dt = new Date(val);
  if (!Number.isNaN(dt.getTime())) return [dt, true];
  const local = parseDateLocal(t);
  if (local) return [local, true];
  return [new Date(0), false];
}

function normalizeEpochMillis(n: number) {
  if (n < 100000000000) return n * 1000;
  return n;
}

export function CoerceMillis(v: any): [number, boolean] {
  if (v === null || v === undefined) return [0, false];
  if (typeof v === "boolean") return [0, false];
  if (typeof v === "number") return [normalizeEpochMillis(Math.trunc(v)), true];
  if (typeof v === "string") {
    const s = v.trim();
    if (!s) return [0, false];
    if (s.toLowerCase() === "now") return [Date.now(), true];
    if (/^\d+$/.test(s)) return [normalizeEpochMillis(Number(s)), true];
    const [dt, ok] = ParseDatetime(s);
    if (ok) return [dt.getTime(), true];
    return [0, false];
  }
  return [0, false];
}

export function CoerceDatePayload(v: any): [any, boolean] {
  if (v === null || v === undefined) return [null, false];
  if (typeof v === "boolean") return [null, false];
  if (typeof v === "number") return [normalizeEpochMillis(Math.trunc(v)), true];
  if (typeof v === "string") {
    const s = v.trim();
    if (!s) return [null, false];
    if (s.toLowerCase() === "now") return [Date.now(), true];
    if (/^\d+$/.test(s)) return [normalizeEpochMillis(Number(s)), true];
    const [dt, ok] = ParseDatetime(s);
    if (ok) return [dt.getTime(), true];
    return [s, true];
  }
  return [null, false];
}

export function NormalizeExtra(extra: any) {
  if (extra === null || extra === undefined) return "";
  if (typeof extra === "string") return extra.trim();
  return marshalJSONNoEscape(extra);
}

export function marshalJSONNoEscape(v: any) {
  try {
    return JSON.stringify(v);
  } catch {
    return "";
  }
}

export function readAllInput(pathStr: string) {
  if (!pathStr) return Buffer.from("");
  if (pathStr === "-") return fs.readFileSync(0);
  return fs.readFileSync(pathStr);
}

export function detectInputFormat(pathStr: string, raw: Buffer) {
  if (pathStr && pathStr !== "-") {
    const ext = path.extname(pathStr).toLowerCase();
    if (ext === ".jsonl") return "jsonl";
  }
  const stripped = raw.toString().trim();
  if (stripped.startsWith("[") || stripped.startsWith("{")) return "json";
  return "jsonl";
}

export function parseJSONItems(raw: Buffer) {
  const v = JSON.parse(raw.toString());
  if (Array.isArray(v)) return v.filter((it) => it && typeof it === "object");
  if (v && typeof v === "object") {
    if (Array.isArray((v as any).tasks)) return (v as any).tasks.filter((it: any) => it && typeof it === "object");
    return [v];
  }
  return [];
}

export function parseJSONLItems(raw: Buffer) {
  const lines = raw.toString().split(/\r?\n/);
  const out: any[] = [];
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;
    out.push(JSON.parse(trimmed));
  }
  return out;
}
