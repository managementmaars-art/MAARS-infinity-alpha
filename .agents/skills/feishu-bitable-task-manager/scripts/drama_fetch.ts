#!/usr/bin/env node
import {
  BitableRef,
  ClampPageSize,
  DefaultBaseURL,
  Env,
  GetTenantAccessToken,
  NormalizeBitableValue,
  ParseBitableURL,
  RequestJSON,
  ResolveWikiAppToken,
} from "./bitable_common";
import * as fs from "node:fs";
import { Command } from "commander";

type DramaFieldMap = {
  bookID: string;
  name: string;
  durationMin: string;
  episodeCount: string;
  rightsProtectionScenario: string;
  priority: string;
};

export type SourceFetchParams = {
  bitableURL: string;
  bookIDs?: string[];
  bidField?: string;
  priorities?: string[];
  priorityField?: string;
  pageSize?: number;
  limit?: number;
  appID?: string;
  appSecret?: string;
  baseURL?: string;
};

export type SourceFetchResult = {
  items: any[];
  bidField: string | null;
  priorityField: string | null;
  usedFilter: boolean;
};

function dramaFieldsFromEnv(): DramaFieldMap {
  return {
    bookID: Env("DRAMA_FIELD_BOOKID", "短剧id").trim() || "短剧id",
    name: Env("DRAMA_FIELD_NAME", "短剧名").trim() || "短剧名",
    durationMin: Env("DRAMA_FIELD_DURATION_MIN", "短剧总时长（分钟）").trim() || "短剧总时长（分钟）",
    episodeCount: Env("DRAMA_FIELD_EPISODE_COUNT", "集数").trim() || "集数",
    rightsProtectionScenario: Env("DRAMA_FIELD_RIGHTS_PROTECTION_SCENARIO", "维权场景").trim() || "维权场景",
    priority: Env("DRAMA_FIELD_PRIORITY", "优先级").trim() || "优先级",
  };
}

export function parseCSVList(raw: string) {
  return raw
    .split(/[\s,，]+/g)
    .map((x) => x.trim())
    .filter(Boolean);
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

export function simplifyFields(fieldsRaw: Record<string, any>) {
  const out: Record<string, any> = {};
  for (const [k, v] of Object.entries(fieldsRaw)) out[k] = simplifyValue(v);
  return out;
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
    const resp = await RequestJSON("POST", urlStr, token, body, true);
    if (resp.code !== 0) throw new Error(`search records failed: code=${resp.code} msg=${resp.msg}`);
    const batch = resp.data?.items || [];
    items.push(...batch);
    if (limit && items.length >= limit) return items.slice(0, limit);
    if (!resp.data?.has_more) break;
    pageToken = String(resp.data?.page_token || "").trim();
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

export async function fetchSourceRecords(params: SourceFetchParams): Promise<SourceFetchResult> {
  const bitableURL = params.bitableURL.trim();
  if (!bitableURL) throw new Error("--bitable-url is required");
  const appID = (params.appID || Env("FEISHU_APP_ID", "")).trim();
  const appSecret = (params.appSecret || Env("FEISHU_APP_SECRET", "")).trim();
  if (!appID || !appSecret) throw new Error("FEISHU_APP_ID/FEISHU_APP_SECRET are required");
  const baseURL = (params.baseURL || Env("FEISHU_BASE_URL", DefaultBaseURL)).trim() || DefaultBaseURL;
  const pageSize = Math.max(1, Number(params.pageSize || 200));
  const limit = Math.max(0, Number(params.limit || 0));
  const bookIDs = (params.bookIDs || []).map((x) => x.trim()).filter(Boolean);
  const priorities = (params.priorities || []).map((x) => x.trim()).filter(Boolean);

  let ref = ParseBitableURL(bitableURL);
  const token = await GetTenantAccessToken(baseURL, appID, appSecret);
  ref = await resolveBitableRef(baseURL, token, ref);

  let bidField: string | null = null;
  let priorityField: string | null = null;
  let filterObj: any = null;

  const conditions: any[] = [];

  const fieldNames = await fetchTableFieldNames(baseURL, token, ref);

  if (bookIDs.length) {
    const preferred = (params.bidField || Env("SOURCE_FIELD_BID", "BID")).trim() || "BID";
    const resolved = resolveFieldName(fieldNames, preferred, ["BID", "BookID", "book_id", "bookId", "短剧id"]);
    if (!resolved) throw new Error(`cannot resolve bid field in source table: preferred=${preferred}`);
    bidField = resolved;
    const bidFilter = buildORIsFilter(bidField, bookIDs);
    if (!bidFilter) throw new Error("invalid bid field or book ids");
    conditions.push(bidFilter);
  }

  if (priorities.length) {
    const preferred = (params.priorityField || Env("SOURCE_FIELD_PRIORITY", "优先级")).trim() || "优先级";
    const resolved = resolveFieldName(fieldNames, preferred, ["Priority", "priority", "优先级"]);
    if (!resolved) throw new Error(`cannot resolve priority field in source table: preferred=${preferred}`);
    priorityField = resolved;
    const priorityFilter = buildORIsFilter(priorityField, priorities);
    if (!priorityFilter) throw new Error("invalid priority field or priorities");
    conditions.push(priorityFilter);
  }

  if (conditions.length === 1) {
    filterObj = conditions[0];
  } else if (conditions.length > 1) {
    filterObj = { conjunction: "and", conditions };
  }

  const items = await fetchAllRecords(baseURL, token, ref, pageSize, ref.ViewID, Boolean(ref.ViewID), filterObj, limit || undefined);
  return { items, bidField, priorityField, usedFilter: Boolean(filterObj) };
}

async function main() {
  const program = new Command();
  program.name("drama-fetch").description("Fetch source drama rows from a Feishu Bitable");

  program
    .requiredOption("--bitable-url <url>", "Source Bitable URL")
    .option("--book-id <value>", "Optional BookID/BID filter (single value or comma-separated list)")
    .option("--bid-field <name>", "Preferred source field name for BID/BookID")
    .option("--priority <value>", "Optional Priority filter (single value or comma-separated list)")
    .option("--priority-field <name>", "Preferred source field name for Priority")
    .option("--page-size <n>", "Page size (max 500)", "200")
    .option("--limit <n>", "Max records to return (0 = no cap)", "0")
    .option("--format <name>", "Output format: raw|meta", "raw")
    .option("--output <path>", "Output path for JSONL (default stdout)")
    .action(async (opts) => {
      const bookIDs = parseCSVList(String(opts.bookId || ""));
      const priorities = parseCSVList(String(opts.priority || ""));
      if (!bookIDs.length && !priorities.length) {
        process.stderr.write("[drama-fetch] hint: fetch without --book-id or --priority will scan all source rows\n");
      }
      const result = await fetchSourceRecords({
        bitableURL: String(opts.bitableUrl || ""),
        bookIDs,
        bidField: String(opts.bidField || ""),
        priorities,
        priorityField: String(opts.priorityField || ""),
        pageSize: Number(opts.pageSize || 200),
        limit: Number(opts.limit || 0),
      });
      const out = opts.output ? fs.createWriteStream(String(opts.output)) : process.stdout;
      const format = String(opts.format || "raw").trim().toLowerCase();
      const dramaFields = dramaFieldsFromEnv();
      for (const item of result.items) {
        const fieldsRaw = item?.fields || {};
        if (format === "meta") {
          const row = {
            record_id: NormalizeBitableValue(item?.record_id).trim(),
            book_id: NormalizeBitableValue(fieldsRaw[dramaFields.bookID]).trim(),
            name: NormalizeBitableValue(fieldsRaw[dramaFields.name]).trim(),
            duration_min: NormalizeBitableValue(fieldsRaw[dramaFields.durationMin]).trim(),
            episode_count: NormalizeBitableValue(fieldsRaw[dramaFields.episodeCount]).trim(),
            rights_protection_scenario: NormalizeBitableValue(fieldsRaw[dramaFields.rightsProtectionScenario]).trim(),
            priority: NormalizeBitableValue(fieldsRaw[dramaFields.priority]).trim(),
          };
          out.write(`${JSON.stringify(row)}\n`);
          continue;
        }
        out.write(`${JSON.stringify(simplifyFields(fieldsRaw))}\n`);
      }
      process.stderr.write(
        `[drama-fetch] fetched ${result.items.length} rows, filtered=${result.usedFilter}, bid_field=${result.bidField || "-"}, priority_field=${result.priorityField || "-"}\n`
      );
    });

  program.showHelpAfterError().showSuggestionAfterError();
  await program.parseAsync(process.argv);
}

if (require.main === module) {
  main().catch((err) => {
    process.stderr.write(`[drama-fetch] ${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  });
}
