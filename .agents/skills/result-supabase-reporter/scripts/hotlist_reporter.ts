#!/usr/bin/env -S npx tsx

import { readFileSync } from "node:fs";
import { Command } from "commander";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";

type HotlistRecord = {
  platform_name: string;
  rank: number;
  catalog_name: string;
  catalog_type: string | null;
  release_date: string | null;
  collected_date: string;
};

type InsertInput = {
  platform_name?: string;
  rank?: number | string;
  catalog_name?: string;
  catalog_type?: string | null;
  release_date?: string | null;
  collected_date?: string | number | null;
};

const DEFAULT_TABLE = "hotlist_catalogs";

const program = new Command();
program
  .name("hotlist_reporter")
  .description("Insert and query hotlist catalogs in Supabase")
  .showHelpAfterError();

function normalizeText(v: unknown): string | null {
  if (v === null || v === undefined) {
    return null;
  }
  const s = String(v).trim();
  return s === "" ? null : s;
}

function requireText(v: unknown, field: string): string {
  const s = normalizeText(v);
  if (!s) {
    throw new Error(`missing required field: ${field}`);
  }
  return s;
}

function parsePositiveInt(v: unknown, field: string): number {
  const n = Number(v);
  if (!Number.isInteger(n) || n <= 0) {
    throw new Error(`invalid ${field}: ${String(v)}; expected positive integer`);
  }
  return n;
}

function parseReleaseDate(v: unknown): string | null {
  const s = normalizeText(v);
  if (!s) {
    return null;
  }
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    throw new Error(`invalid release_date: ${s}; expected YYYY-MM-DD`);
  }
  return s;
}

function toDateString(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function parseCollectedDate(v: unknown): string {
  if (typeof v === "number") {
    if (!Number.isFinite(v)) {
      throw new Error(`invalid collected_date: ${v}`);
    }
    return toDateString(new Date(Math.trunc(v) * 1000));
  }
  const s = normalizeText(v);
  if (!s || s.toLowerCase() === "now") {
    return toDateString(new Date());
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) {
    return s;
  }
  if (/^\d+$/.test(s)) {
    return toDateString(new Date(Number(s) * 1000));
  }
  const d = new Date(s);
  if (Number.isNaN(d.getTime())) {
    throw new Error(`invalid collected_date: ${s}; use YYYY-MM-DD / ISO datetime / unix seconds`);
  }
  return toDateString(d);
}

function createSupabaseClientFromEnv(): SupabaseClient {
  const url = process.env.SUPABASE_URL?.trim();
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY?.trim();
  if (!url || !key) {
    throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required");
  }
  return createClient(url, key, {
    auth: { persistSession: false, autoRefreshToken: false },
  });
}

function resolveTable(flagValue?: string): string {
  if (flagValue && flagValue.trim() !== "") {
    return flagValue.trim();
  }
  const fromEnv = process.env.SUPABASE_HOTLIST_TABLE?.trim();
  return fromEnv && fromEnv !== "" ? fromEnv : DEFAULT_TABLE;
}

function toHotlistRecord(input: InsertInput): HotlistRecord {
  return {
    platform_name: requireText(input.platform_name, "platform_name"),
    rank: parsePositiveInt(input.rank, "rank"),
    catalog_name: requireText(input.catalog_name, "catalog_name"),
    catalog_type: normalizeText(input.catalog_type),
    release_date: parseReleaseDate(input.release_date),
    collected_date: parseCollectedDate(input.collected_date),
  };
}

function parseJSONLInput(path: string): InsertInput[] {
  const text = readFileSync(path, "utf8");
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  return lines.map((line, idx) => {
    try {
      return JSON.parse(line) as InsertInput;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      throw new Error(`invalid JSON at line ${idx + 1}: ${msg}`);
    }
  });
}

program
  .command("insert")
  .description("Insert one row or upsert batch rows from JSONL")
  .option("--table <name>", "Supabase table name (default hotlist_catalogs)")
  .option("--input <path>", "Batch insert from JSONL file")
  .option("--platform-name <value>", "Platform name, e.g. 腾讯视频")
  .option("--rank <n>", "Hotlist rank")
  .option("--catalog-name <value>", "Catalog name")
  .option("--catalog-type <value>", "Catalog type")
  .option("--release-date <yyyy-mm-dd>", "Release date")
  .option("--collected-date <value>", "Collected date: YYYY-MM-DD / ISO datetime / unix seconds / now", "now")
  .action(async (cmd) => {
    const client = createSupabaseClientFromEnv();
    const table = resolveTable(cmd.table);

    const inputRows: InsertInput[] = cmd.input
      ? parseJSONLInput(String(cmd.input))
      : [
          {
            platform_name: cmd.platformName,
            rank: cmd.rank,
            catalog_name: cmd.catalogName,
            catalog_type: cmd.catalogType,
            release_date: cmd.releaseDate,
            collected_date: cmd.collectedDate,
          },
        ];
    if (inputRows.length === 0) {
      throw new Error("no input rows");
    }
    const records = inputRows.map(toHotlistRecord);

    const { error } = await client.from(table).upsert(records, {
      onConflict: "platform_name,collected_date,rank",
      ignoreDuplicates: false,
    });
    if (error) {
      throw new Error(`supabase upsert failed: ${error.message}`);
    }
    process.stderr.write(`[insert] table=${table} inserted=${records.length}\n`);
  });

program
  .command("query")
  .description("Query rows by platform and collected_date range")
  .option("--table <name>", "Supabase table name (default hotlist_catalogs)")
  .option("--platform-name <value>", "Exact platform_name filter, e.g. 腾讯视频")
  .option("--from <value>", "Collected_date lower bound: YYYY-MM-DD / ISO datetime / unix seconds")
  .option("--to <value>", "Collected_date upper bound: YYYY-MM-DD / ISO datetime / unix seconds")
  .option("--last-days <n>", "Shortcut for from=now-n days", "0")
  .option("--limit <n>", "Maximum rows", "100")
  .action(async (cmd) => {
    const client = createSupabaseClientFromEnv();
    const table = resolveTable(cmd.table);
    const limit = parsePositiveInt(cmd.limit, "--limit");
    const lastDays = Number(cmd.lastDays ?? 0);
    if (!Number.isInteger(lastDays) || lastDays < 0) {
      throw new Error(`invalid --last-days: ${cmd.lastDays}; expected non-negative integer`);
    }

    const fromByDays =
      lastDays > 0 ? toDateString(new Date(Date.now() - lastDays * 24 * 60 * 60 * 1000)) : undefined;
    const from = cmd.from ? parseCollectedDate(cmd.from) : fromByDays;
    const to = cmd.to ? parseCollectedDate(cmd.to) : undefined;

    let query = client.from(table).select("*").limit(limit);
    if (cmd.platformName && String(cmd.platformName).trim() !== "") {
      query = query.eq("platform_name", String(cmd.platformName).trim());
    }
    if (from) {
      query = query.gte("collected_date", from);
    }
    if (to) {
      query = query.lte("collected_date", to);
    }
    query = query.order("collected_date", { ascending: false }).order("rank", { ascending: true });

    const { data, error } = await query;
    if (error) {
      throw new Error(`supabase query failed: ${error.message}`);
    }
    for (const row of data ?? []) {
      process.stdout.write(`${JSON.stringify(row)}\n`);
    }
    process.stderr.write(
      `[query] table=${table} platform=${cmd.platformName ?? "all"} from=${from ?? "-"} to=${to ?? "-"} rows=${(data ?? []).length}\n`,
    );
  });

program.parseAsync(process.argv).catch((err: unknown) => {
  const msg = err instanceof Error ? err.message : String(err);
  process.stderr.write(`[error] ${msg}\n`);
  process.exit(1);
});
