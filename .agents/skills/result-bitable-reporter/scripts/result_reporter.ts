#!/usr/bin/env -S npx tsx

import { execFileSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";
import { URL } from "node:url";
import { Command } from "commander";

type CaptureRow = {
  id: number;
  Datetime: number | null;
  DeviceSerial: string | null;
  App: string | null;
  Scene: string | null;
  Params: string | null;
  ItemID: string | null;
  ItemCaption: string | null;
  ItemCDNURL: string | null;
  ItemURL: string | null;
  ItemDuration: number | null;
  UserName: string | null;
  UserID: string | null;
  UserAlias: string | null;
  UserAuthEntity: string | null;
  Tags: string | null;
  TaskID: number | null;
  BookID: string | null;
  Extra: string | null;
  LikeCount: number | null;
  ViewCount: number | null;
  AnchorPoint: string | null;
  CommentCount: number | null;
  CollectCount: number | null;
  ForwardCount: number | null;
  ShareCount: number | null;
  PayMode: string | null;
  Collection: string | null;
  Episode: string | null;
  PublishTime: string | null;
};

type BitableRef = {
  appToken: string;
  tableID: string;
  wikiToken?: string;
};

type FilterOptions = {
  dbPath: string;
  table: string;
  limit: number;
  status: number[];
  taskID?: number;
  app?: string;
  scene?: string;
  paramsLike?: string;
  itemID?: string;
  dateFrom?: string;
  dateTo?: string;
  where?: string;
  whereArgs: string[];
};

type ReportOptions = FilterOptions & {
  bitableURL?: string;
  batchSize: number;
  dryRun: boolean;
  maxRows?: number;
};

type RetryResetOptions = {
  dbPath: string;
  table: string;
  app?: string;
  scene?: string;
};

type IntString = number | string | null | undefined;

type ResultFieldNames = {
  datetime: string;
  deviceSerial: string;
  app: string;
  scene: string;
  params: string;
  itemID: string;
  itemCaption: string;
  itemCDNURL: string;
  itemURL: string;
  itemDuration: string;
  userName: string;
  userID: string;
  userAlias: string;
  userAuthEntity: string;
  tags: string;
  taskID: string;
  bookID: string;
  extra: string;
  likeCount: string;
  viewCount: string;
  anchorPoint: string;
  commentCount: string;
  collectCount: string;
  forwardCount: string;
  shareCount: string;
  payMode: string;
  collection: string;
  episode: string;
  publishTime: string;
};

type TenantTokenResponse = {
  code: number;
  msg: string;
  tenant_access_token?: string;
};

type FeishuResp<T> = {
  code: number;
  msg: string;
  data?: T;
};

const DEFAULT_DB_PATH = join(homedir(), ".eval", "records.sqlite");
const DEFAULT_TABLE = "capture_results";
const REPORT_PAGE_SIZE = 200;

const program = new Command();
program
  .name("result_reporter")
  .description("Filter capture results from SQLite and report to Feishu Bitable")
  .showHelpAfterError();

function collect(value: string, previous: string[]): string[] {
  previous.push(value);
  return previous;
}

function parseStatusCSV(raw: string): number[] {
  const values = raw
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean)
    .map((item) => Number(item));
  if (values.length === 0 || values.some((v) => Number.isNaN(v))) {
    throw new Error(`invalid --status value: ${raw}`);
  }
  return values;
}

function parsePositiveInt(value: string, flagName: string): number {
  const parsed = Number(value);
  if (!Number.isInteger(parsed) || parsed <= 0) {
    throw new Error(`invalid ${flagName}: ${value}; expected positive integer`);
  }
  return parsed;
}

function parseTaskIDNumber(raw: string): number {
  const value = raw.trim();
  if (!/^\d+$/.test(value)) {
    throw new Error(`invalid --task-id value: ${raw}; expected digits only`);
  }
  const taskID = Number(value);
  if (!Number.isSafeInteger(taskID) || taskID < 0) {
    throw new Error(`invalid --task-id value: ${raw}; out of safe integer range`);
  }
  return taskID;
}

function parseCount(value: IntString): number {
  const parsed = typeof value === "number" ? value : Number(value ?? 0);
  return Number.isFinite(parsed) ? Math.max(0, Math.trunc(parsed)) : 0;
}

function expandHome(path: string): string {
  if (path === "~") {
    return homedir();
  }
  if (path.startsWith("~/")) {
    return join(homedir(), path.slice(2));
  }
  return path;
}

function resolveDBPath(flagValue?: string): string {
  if (flagValue && flagValue.trim() !== "") {
    return expandHome(flagValue.trim());
  }
  const fromEnv = process.env.TRACKING_STORAGE_DB_PATH?.trim();
  return fromEnv && fromEnv !== "" ? expandHome(fromEnv) : DEFAULT_DB_PATH;
}

function resolveTable(flagValue?: string): string {
  if (flagValue && flagValue.trim() !== "") {
    return flagValue.trim();
  }
  const fromEnv = process.env.RESULT_SQLITE_TABLE?.trim();
  return fromEnv && fromEnv !== "" ? fromEnv : DEFAULT_TABLE;
}

function quoteIdent(identifier: string): string {
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(identifier)) {
    throw new Error(`invalid SQL identifier: ${identifier}`);
  }
  return `"${identifier}"`;
}

function sqlString(value: string): string {
  return `'${value.replace(/'/g, "''")}'`;
}

function sqlLiteral(value: string | number | null): string {
  if (value === null) {
    return "NULL";
  }
  if (typeof value === "number") {
    return Number.isFinite(value) ? String(value) : "NULL";
  }
  return sqlString(value);
}

function parseDateToUnixMillis(input: string, endOfDay: boolean): number {
  const raw = input.trim();
  if (!raw) {
    throw new Error("date input is empty");
  }
  const dateOnly = /^\d{4}-\d{2}-\d{2}$/.test(raw);
  let d: Date;
  if (dateOnly) {
    d = new Date(`${raw}T00:00:00`);
    if (endOfDay) {
      d = new Date(`${raw}T23:59:59.999`);
    }
  } else {
    d = new Date(raw);
  }
  const ts = d.getTime();
  if (Number.isNaN(ts)) {
    throw new Error(`invalid date/datetime: ${input}`);
  }
  return ts;
}

function applyWhereArgs(whereExpr: string, args: string[]): string {
  let out = whereExpr;
  for (const arg of args) {
    const idx = out.indexOf("?");
    if (idx < 0) {
      throw new Error("--where-arg provided but --where has fewer placeholders");
    }
    out = `${out.slice(0, idx)}${sqlLiteral(arg)}${out.slice(idx + 1)}`;
  }
  if (out.includes("?")) {
    throw new Error("--where still contains placeholders; provide matching --where-arg values");
  }
  return out;
}

function buildWhereClause(opts: FilterOptions, extraClauses: string[] = []): string {
  const clauses: string[] = [];

  if (opts.status.length > 0) {
    const vals = opts.status.map((s) => String(s)).join(",");
    clauses.push(`reported IN (${vals})`);
  }
  if (opts.taskID !== undefined) {
    clauses.push(`TaskID = ${opts.taskID}`);
  }
  if (opts.app) {
    clauses.push(`App = ${sqlLiteral(opts.app)}`);
  }
  if (opts.scene) {
    clauses.push(`Scene = ${sqlLiteral(opts.scene)}`);
  }
  if (opts.paramsLike) {
    clauses.push(`Params LIKE ${sqlLiteral(`%${opts.paramsLike}%`)}`);
  }
  if (opts.itemID) {
    clauses.push(`ItemID = ${sqlLiteral(opts.itemID)}`);
  }
  if (opts.dateFrom) {
    clauses.push(`Datetime >= ${parseDateToUnixMillis(opts.dateFrom, false)}`);
  }
  if (opts.dateTo) {
    clauses.push(`Datetime <= ${parseDateToUnixMillis(opts.dateTo, true)}`);
  }
  if (opts.where) {
    clauses.push(`(${applyWhereArgs(opts.where, opts.whereArgs)})`);
  }
  clauses.push(...extraClauses);

  return clauses.length === 0 ? "" : `WHERE ${clauses.join(" AND ")}`;
}

function runSQLiteRaw(dbPath: string, sql: string, asJSON: boolean): string {
  const args = [asJSON ? "-json" : "-batch", dbPath, sql];
  return execFileSync("sqlite3", args, { encoding: "utf8" });
}

function runSQLite(dbPath: string, sql: string): void {
  runSQLiteRaw(dbPath, sql, false);
}

function runSQLiteJSON<T>(dbPath: string, sql: string): T {
  const out = runSQLiteRaw(dbPath, sql, true).trim();
  if (!out) {
    return [] as unknown as T;
  }
  return JSON.parse(out) as T;
}

function fetchRows(opts: FilterOptions): CaptureRow[] {
  return fetchRowsPage(opts, opts.limit, 0);
}

function fetchRowsPage(opts: FilterOptions, limit: number, afterID: number): CaptureRow[] {
  const table = quoteIdent(opts.table);
  const extraClauses = afterID > 0 ? [`id > ${afterID}`] : [];
  const whereSQL = buildWhereClause(opts, extraClauses);
  const sql = `
SELECT id, Datetime, DeviceSerial, App, Scene, Params, ItemID, ItemCaption,
       ItemCDNURL, ItemURL, ItemDuration, UserName, UserID, UserAlias,
       UserAuthEntity, Tags, TaskID, BookID, Extra, LikeCount, ViewCount, AnchorPoint,
       CommentCount, CollectCount, ForwardCount, ShareCount, PayMode, Collection,
       Episode, PublishTime
FROM ${table}
${whereSQL}
ORDER BY id ASC
LIMIT ${limit};`;
  return runSQLiteJSON<CaptureRow[]>(opts.dbPath, sql);
}

function truncateError(err: unknown): string {
  const text = err instanceof Error ? err.message : String(err);
  return text.length <= 512 ? text : text.slice(0, 512);
}

function markSuccessBatch(dbPath: string, table: string, ids: number[]): void {
  if (ids.length === 0) {
    return;
  }
  const qTable = quoteIdent(table);
  const list = ids.join(",");
  const now = Date.now();
  const sql = `UPDATE ${qTable} SET reported=1, reported_at=${now}, report_error=NULL WHERE id IN (${list});`;
  runSQLite(dbPath, sql);
}

function markFailureBatch(dbPath: string, table: string, ids: number[], error: string): void {
  if (ids.length === 0) {
    return;
  }
  const qTable = quoteIdent(table);
  const list = ids.join(",");
  const now = Date.now();
  const sql = `UPDATE ${qTable} SET reported=-1, reported_at=${now}, report_error=${sqlLiteral(error)} WHERE id IN (${list});`;
  runSQLite(dbPath, sql);
}

function parseBitableURL(rawURL: string): BitableRef {
  const parsed = new URL(preprocessBitableURL(rawURL));
  const tableID = parsed.searchParams.get("table")?.trim();
  if (!tableID) {
    throw new Error("bitable URL missing table query parameter");
  }
  const pathname = parsed.pathname;
  const baseMatch = pathname.match(/\/base\/([A-Za-z0-9]+)/);
  if (baseMatch) {
    return { appToken: baseMatch[1], tableID };
  }
  const wikiMatch = pathname.match(/\/wiki\/([A-Za-z0-9]+)/);
  if (wikiMatch) {
    return { appToken: "", tableID, wikiToken: wikiMatch[1] };
  }
  throw new Error(`unsupported bitable URL path: ${pathname}`);
}

function preprocessBitableURL(rawURL: string): string {
  let value = rawURL.trim();
  if (
    (value.startsWith('"') && value.endsWith('"')) ||
    (value.startsWith("'") && value.endsWith("'"))
  ) {
    value = value.slice(1, -1).trim();
  }
  value = value.replace(/\\([?&=])/g, "$1");
  value = value.replace(/&amp;/gi, "&");
  value = value.replace(/\s*([?&=])\s*/g, "$1");
  return value;
}

async function fetchJSON<T>(url: string, init: RequestInit): Promise<T> {
  const resp = await fetch(url, init);
  const text = await resp.text();
  let payload: T;
  try {
    payload = JSON.parse(text) as T;
  } catch (err) {
    throw new Error(`non-JSON response from ${url}: ${String(err)}; body=${text.slice(0, 500)}`);
  }
  if (!resp.ok) {
    throw new Error(`HTTP ${resp.status} from ${url}: ${text.slice(0, 500)}`);
  }
  return payload;
}

function baseURL(): string {
  return (process.env.FEISHU_BASE_URL || "https://open.feishu.cn").replace(/\/$/, "");
}

async function getTenantAccessToken(): Promise<string> {
  const appID = process.env.FEISHU_APP_ID?.trim();
  const appSecret = process.env.FEISHU_APP_SECRET?.trim();
  if (!appID || !appSecret) {
    throw new Error("FEISHU_APP_ID and FEISHU_APP_SECRET are required");
  }
  const url = `${baseURL()}/open-apis/auth/v3/tenant_access_token/internal/`;
  const payload = await fetchJSON<TenantTokenResponse>(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ app_id: appID, app_secret: appSecret }),
  });
  if (payload.code !== 0 || !payload.tenant_access_token) {
    throw new Error(`fetch tenant token failed: code=${payload.code}, msg=${payload.msg}`);
  }
  return payload.tenant_access_token;
}

async function resolveBitableRef(rawURL: string, token: string): Promise<BitableRef> {
  const ref = parseBitableURL(rawURL);
  if (!ref.wikiToken) {
    return ref;
  }
  const url = `${baseURL()}/open-apis/wiki/v2/spaces/get_node?token=${encodeURIComponent(ref.wikiToken)}`;
  const payload = await fetchJSON<FeishuResp<{ node?: { obj_token?: string; obj_type?: string } }>>(url, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
  const appToken = payload.data?.node?.obj_token?.trim() || "";
  const objType = payload.data?.node?.obj_type?.trim() || "";
  if (payload.code !== 0 || !appToken) {
    throw new Error(`resolve wiki token failed: code=${payload.code}, msg=${payload.msg}`);
  }
  if (objType !== "bitable") {
    throw new Error(`wiki node type is not bitable: ${objType}`);
  }
  return { appToken, tableID: ref.tableID, wikiToken: ref.wikiToken };
}

function normalizeExtra(raw: string | null): string | undefined {
  if (!raw) {
    return undefined;
  }
  const trimmed = raw.trim();
  if (trimmed === "") {
    return undefined;
  }
  return trimmed;
}

function resultFieldNames(): ResultFieldNames {
  const env = process.env;
  const pick = (k: string, d: string) => (env[k]?.trim() ? env[k]!.trim() : d);
  return {
    datetime: pick("RESULT_FIELD_DATETIME", "Datetime"),
    deviceSerial: pick("RESULT_FIELD_DEVICE_SERIAL", "DeviceSerial"),
    app: pick("RESULT_FIELD_APP", "App"),
    scene: pick("RESULT_FIELD_SCENE", "Scene"),
    params: pick("RESULT_FIELD_PARAMS", "Params"),
    itemID: pick("RESULT_FIELD_ITEMID", "ItemID"),
    itemCaption: pick("RESULT_FIELD_ITEMCAPTION", "ItemCaption"),
    itemCDNURL: pick("RESULT_FIELD_ITEMCDNURL", "ItemCDNURL"),
    itemURL: pick("RESULT_FIELD_ITEMURL", "ItemURL"),
    itemDuration: pick("RESULT_FIELD_DURATION", "ItemDuration"),
    userName: pick("RESULT_FIELD_USERNAME", "UserName"),
    userID: pick("RESULT_FIELD_USERID", "UserID"),
    userAlias: pick("RESULT_FIELD_USERALIAS", "UserAlias"),
    userAuthEntity: pick("RESULT_FIELD_USERAUTHENTITY", "UserAuthEntity"),
    tags: pick("RESULT_FIELD_TAGS", "Tags"),
    taskID: pick("RESULT_FIELD_TASKID", "TaskID"),
    bookID: pick("RESULT_FIELD_BOOKID", "BookID"),
    extra: pick("RESULT_FIELD_EXTRA", "Extra"),
    likeCount: pick("RESULT_FIELD_LIKECOUNT", "LikeCount"),
    viewCount: pick("RESULT_FIELD_VIEWCOUNT", "ViewCount"),
    anchorPoint: pick("RESULT_FIELD_ANCHORPOINT", "AnchorPoint"),
    commentCount: pick("RESULT_FIELD_COMMENTCOUNT", "CommentCount"),
    collectCount: pick("RESULT_FIELD_COLLECTCOUNT", "CollectCount"),
    forwardCount: pick("RESULT_FIELD_FORWARDCOUNT", "ForwardCount"),
    shareCount: pick("RESULT_FIELD_SHARECOUNT", "ShareCount"),
    payMode: pick("RESULT_FIELD_PAYMODE", "PayMode"),
    collection: pick("RESULT_FIELD_COLLECTION", "Collection"),
    episode: pick("RESULT_FIELD_EPISODE", "Episode"),
    publishTime: pick("RESULT_FIELD_PUBLISHTIME", "PublishTime"),
  };
}

function assignIfPresent(out: Record<string, unknown>, key: string, value: unknown): void {
  if (value === null || value === undefined) {
    return;
  }
  if (typeof value === "string" && value.trim() === "") {
    return;
  }
  out[key] = value;
}

function rowToFeishuFields(row: CaptureRow): Record<string, unknown> {
  const names = resultFieldNames();
  const fields: Record<string, unknown> = {};
  assignIfPresent(fields, names.datetime, row.Datetime);
  assignIfPresent(fields, names.deviceSerial, row.DeviceSerial);
  assignIfPresent(fields, names.app, row.App);
  assignIfPresent(fields, names.scene, row.Scene);
  assignIfPresent(fields, names.params, row.Params);
  assignIfPresent(fields, names.itemID, row.ItemID);
  assignIfPresent(fields, names.itemCaption, row.ItemCaption);
  assignIfPresent(fields, names.itemCDNURL, row.ItemCDNURL);
  assignIfPresent(fields, names.itemURL, row.ItemURL);
  assignIfPresent(fields, names.itemDuration, row.ItemDuration);
  assignIfPresent(fields, names.userName, row.UserName);
  assignIfPresent(fields, names.userID, row.UserID);
  assignIfPresent(fields, names.userAlias, row.UserAlias);
  assignIfPresent(fields, names.userAuthEntity, row.UserAuthEntity);
  assignIfPresent(fields, names.tags, row.Tags);
  assignIfPresent(fields, names.taskID, row.TaskID);
  assignIfPresent(fields, names.bookID, row.BookID);
  assignIfPresent(fields, names.extra, normalizeExtra(row.Extra));
  assignIfPresent(fields, names.likeCount, row.LikeCount);
  assignIfPresent(fields, names.viewCount, row.ViewCount);
  assignIfPresent(fields, names.anchorPoint, row.AnchorPoint);
  assignIfPresent(fields, names.commentCount, row.CommentCount);
  assignIfPresent(fields, names.collectCount, row.CollectCount);
  assignIfPresent(fields, names.forwardCount, row.ForwardCount);
  assignIfPresent(fields, names.shareCount, row.ShareCount);
  assignIfPresent(fields, names.payMode, row.PayMode);
  assignIfPresent(fields, names.collection, row.Collection);
  assignIfPresent(fields, names.episode, row.Episode);
  assignIfPresent(fields, names.publishTime, row.PublishTime);
  return fields;
}

async function createBitableRecordsBatch(accessToken: string, ref: BitableRef, rows: CaptureRow[]): Promise<void> {
  const url = `${baseURL()}/open-apis/bitable/v1/apps/${encodeURIComponent(ref.appToken)}/tables/${encodeURIComponent(
    ref.tableID,
  )}/records/batch_create`;
  const body = {
    records: rows.map((row) => ({ fields: rowToFeishuFields(row) })),
  };
  const payload = await fetchJSON<FeishuResp<unknown>>(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(body),
  });
  if (payload.code !== 0) {
    throw new Error(`batch_create failed: code=${payload.code}, msg=${payload.msg}`);
  }
}

async function createBitableRecordSingle(accessToken: string, ref: BitableRef, row: CaptureRow): Promise<void> {
  const url = `${baseURL()}/open-apis/bitable/v1/apps/${encodeURIComponent(ref.appToken)}/tables/${encodeURIComponent(
    ref.tableID,
  )}/records`;
  const body = {
    fields: rowToFeishuFields(row),
  };
  const payload = await fetchJSON<FeishuResp<unknown>>(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify(body),
  });
  if (payload.code !== 0) {
    throw new Error(`create failed: code=${payload.code}, msg=${payload.msg}`);
  }
}

function splitIntoChunks<T>(arr: T[], chunkSize: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < arr.length; i += chunkSize) {
    chunks.push(arr.slice(i, i + chunkSize));
  }
  return chunks;
}

function buildFilterOptions(cmd: {
  dbPath?: string;
  table?: string;
  limit?: string;
  status?: string;
  taskId?: string;
  app?: string;
  scene?: string;
  paramsLike?: string;
  itemId?: string;
  dateFrom?: string;
  dateTo?: string;
  where?: string;
  whereArg?: string[];
}): FilterOptions {
  const limit = parsePositiveInt(cmd.limit ?? "30", "--limit");
  const status = parseStatusCSV(cmd.status ?? "0,-1");
  const taskID = cmd.taskId?.trim() ? parseTaskIDNumber(cmd.taskId) : undefined;
  return {
    dbPath: resolveDBPath(cmd.dbPath),
    table: resolveTable(cmd.table),
    limit,
    status,
    taskID,
    app: cmd.app?.trim() || undefined,
    scene: cmd.scene?.trim() || undefined,
    paramsLike: cmd.paramsLike?.trim() || undefined,
    itemID: cmd.itemId?.trim() || undefined,
    dateFrom: cmd.dateFrom?.trim() || undefined,
    dateTo: cmd.dateTo?.trim() || undefined,
    where: cmd.where?.trim() || undefined,
    whereArgs: (cmd.whereArg ?? []).map((x) => x.trim()),
  };
}

program
  .command("stat")
  .description("Print total row count for one TaskID in capture_results")
  .option("--db-path <path>", "SQLite db path (default from TRACKING_STORAGE_DB_PATH or ~/.eval/records.sqlite)")
  .option("--table <name>", "Result table name (default from RESULT_SQLITE_TABLE or capture_results)")
  .requiredOption("--task-id <value>", "Filter by exact TaskID (digits)")
  .action((cmd) => {
    const dbPath = resolveDBPath(cmd.dbPath);
    const table = resolveTable(cmd.table);
    const taskID = parseTaskIDNumber(String(cmd.taskId ?? ""));
    const qTable = quoteIdent(table);
    const rows = runSQLiteJSON<Array<{ count: number | string }>>(
      dbPath,
      `SELECT COUNT(*) AS count FROM ${qTable} WHERE TaskID = ${taskID};`,
    );
    process.stdout.write(`${parseCount(rows[0]?.count)}\n`);
  });

program
  .command("filter")
  .description("Print selected rows as JSONL")
  .option("--db-path <path>", "SQLite db path (default from TRACKING_STORAGE_DB_PATH or ~/.eval/records.sqlite)")
  .option("--table <name>", "Result table name (default from RESULT_SQLITE_TABLE or capture_results)")
  .option("--limit <n>", "Maximum rows to fetch", "30")
  .option("--status <csv>", "Reported status list, comma-separated", "0,-1")
  .option("--task-id <value>", "Filter by exact TaskID (digits)")
  .option("--app <value>", "Exact App filter")
  .option("--scene <value>", "Exact Scene filter")
  .option("--params-like <value>", "Params LIKE filter")
  .option("--item-id <value>", "Exact ItemID filter")
  .option("--date-from <value>", "Datetime lower bound (ISO date/datetime)")
  .option("--date-to <value>", "Datetime upper bound (ISO date/datetime)")
  .option("--where <sql>", "Extra SQL predicate appended with AND")
  .option("--where-arg <value>", "Bound value for --where (repeatable)", collect, [])
  .action((cmd) => {
    const opts = buildFilterOptions(cmd);
    const rows = fetchRows(opts);
    for (const row of rows) {
      process.stdout.write(`${JSON.stringify(row)}\n`);
    }
    process.stderr.write(`[filter] db=${opts.dbPath} table=${opts.table} selected=${rows.length} limit=${opts.limit}\n`);
  });

program
  .command("report")
  .description("Report selected rows to Feishu Bitable and write back sqlite status")
  .option("--db-path <path>", "SQLite db path (default from TRACKING_STORAGE_DB_PATH or ~/.eval/records.sqlite)")
  .option("--table <name>", "Result table name (default from RESULT_SQLITE_TABLE or capture_results)")
  .option("--bitable-url <url>", "Result Bitable URL (default from RESULT_BITABLE_URL)")
  .option("--status <csv>", "Reported status list, comma-separated", "0,-1")
  .option("--task-id <value>", "Filter by exact TaskID (digits)")
  .option("--max-rows <n>", "Maximum total rows to process in this report run")
  .option("--batch-size <n>", "Batch create size (max 500)", "100")
  .option("--dry-run", "Print selected rows only, skip Feishu and writeback", false)
  .option("--app <value>", "Exact App filter")
  .option("--scene <value>", "Exact Scene filter")
  .option("--params-like <value>", "Params LIKE filter")
  .option("--item-id <value>", "Exact ItemID filter")
  .option("--date-from <value>", "Datetime lower bound (ISO date/datetime)")
  .option("--date-to <value>", "Datetime upper bound (ISO date/datetime)")
  .option("--where <sql>", "Extra SQL predicate appended with AND")
  .option("--where-arg <value>", "Bound value for --where (repeatable)", collect, [])
  .action(async (cmd) => {
    const filterOpts = buildFilterOptions(cmd);
    const batchSize = parsePositiveInt(cmd.batchSize ?? "100", "--batch-size");
    if (batchSize > 500) {
      throw new Error(`invalid --batch-size: ${cmd.batchSize}; expected 1..500`);
    }

    const maxRows = cmd.maxRows === undefined ? undefined : parsePositiveInt(cmd.maxRows, "--max-rows");
    const reportOpts: ReportOptions = {
      ...filterOpts,
      bitableURL: cmd.bitableUrl?.trim() || process.env.RESULT_BITABLE_URL?.trim(),
      batchSize,
      dryRun: Boolean(cmd.dryRun),
      maxRows,
    };

    if (!reportOpts.dryRun && !reportOpts.bitableURL) {
      throw new Error("RESULT_BITABLE_URL or --bitable-url is required");
    }

    let accessToken = "";
    let bitableRef: BitableRef | null = null;
    if (!reportOpts.dryRun) {
      accessToken = await getTenantAccessToken();
      bitableRef = await resolveBitableRef(reportOpts.bitableURL as string, accessToken);
    }

    const pageSize = Math.max(reportOpts.batchSize, REPORT_PAGE_SIZE);
    let lastID = 0;
    let selectedCount = 0;
    let successCount = 0;
    let failedCount = 0;

    while (true) {
      if (reportOpts.maxRows !== undefined && selectedCount >= reportOpts.maxRows) {
        break;
      }
      const currentLimit =
        reportOpts.maxRows === undefined ? pageSize : Math.min(pageSize, reportOpts.maxRows - selectedCount);
      if (currentLimit <= 0) {
        break;
      }
      const rows = fetchRowsPage(reportOpts, currentLimit, lastID);
      if (rows.length === 0) {
        break;
      }
      selectedCount += rows.length;
      lastID = rows[rows.length - 1]?.id ?? lastID;

      if (reportOpts.dryRun) {
        for (const row of rows) {
          process.stdout.write(`${JSON.stringify(row)}\n`);
        }
        continue;
      }
      if (!bitableRef) {
        throw new Error("internal error: bitable ref is missing");
      }

      const chunks = splitIntoChunks(rows, reportOpts.batchSize);
      for (const chunk of chunks) {
        const ids = chunk.map((row) => row.id);
        try {
          await createBitableRecordsBatch(accessToken, bitableRef, chunk);
          markSuccessBatch(reportOpts.dbPath, reportOpts.table, ids);
          successCount += ids.length;
        } catch (err) {
          const msg = truncateError(err);
          process.stderr.write(`[report] batch failed size=${ids.length} error=${msg}; fallback to single rows\n`);
          for (const row of chunk) {
            try {
              await createBitableRecordSingle(accessToken, bitableRef, row);
              markSuccessBatch(reportOpts.dbPath, reportOpts.table, [row.id]);
              successCount += 1;
            } catch (singleErr) {
              const singleMsg = truncateError(singleErr);
              markFailureBatch(reportOpts.dbPath, reportOpts.table, [row.id], singleMsg);
              failedCount += 1;
              process.stderr.write(`[report] row failed id=${row.id} error=${singleMsg}\n`);
            }
          }
        }
      }
    }

    process.stderr.write(
      `[report] db=${reportOpts.dbPath} table=${reportOpts.table} selected=${selectedCount} page_size=${pageSize} max_rows=${reportOpts.maxRows ?? "all"}\n`,
    );

    if (selectedCount === 0) {
      process.stderr.write("[report] no rows selected, exit\n");
      return;
    }

    if (reportOpts.dryRun) {
      process.stderr.write("[report] dry-run enabled, skipped Feishu upload and sqlite writeback\n");
      return;
    }

    process.stderr.write(`[report] completed success=${successCount} failed=${failedCount}\n`);
  });

program
  .command("retry-reset")
  .description("Reset failed rows (reported=-1) back to pending (reported=0)")
  .option("--db-path <path>", "SQLite db path (default from TRACKING_STORAGE_DB_PATH or ~/.eval/records.sqlite)")
  .option("--table <name>", "Result table name (default from RESULT_SQLITE_TABLE or capture_results)")
  .option("--app <value>", "Optional App filter")
  .option("--scene <value>", "Optional Scene filter")
  .action((cmd: RetryResetOptions) => {
    const dbPath = resolveDBPath(cmd.dbPath);
    const table = resolveTable(cmd.table);
    const qTable = quoteIdent(table);

    const clauses = ["reported = -1"];
    if (cmd.app && cmd.app.trim() !== "") {
      clauses.push(`App = ${sqlLiteral(cmd.app.trim())}`);
    }
    if (cmd.scene && cmd.scene.trim() !== "") {
      clauses.push(`Scene = ${sqlLiteral(cmd.scene.trim())}`);
    }

    const sql = `
BEGIN;
UPDATE ${qTable} SET reported=0, reported_at=NULL, report_error=NULL WHERE ${clauses.join(" AND ")};
SELECT changes() AS changed;
COMMIT;`;
    const ret = runSQLiteJSON<Array<{ changed: number }>>(dbPath, sql);
    const changed = ret[0]?.changed ?? 0;
    process.stderr.write(`[retry-reset] db=${dbPath} table=${table} updated=${changed}\n`);
  });

program.parseAsync(process.argv).catch((err: unknown) => {
  const msg = err instanceof Error ? err.message : String(err);
  process.stderr.write(`[error] ${msg}\n`);
  process.exit(1);
});
