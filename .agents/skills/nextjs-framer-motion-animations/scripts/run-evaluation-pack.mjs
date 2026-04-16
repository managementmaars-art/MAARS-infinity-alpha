#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HELP = `Usage: node scripts/run-evaluation-pack.mjs [--case ID] [--list]

Run the bundled evaluation pack against the included fixtures. Prints JSON to stdout.

Options:
  --case ID   Run only one case by id.
  --list      List available case ids and exit.
  --help      Show this help text.

Examples:
  node scripts/run-evaluation-pack.mjs
  node scripts/run-evaluation-pack.mjs --case app-router-passive-card
`;

function parseArgs(argv) {
  const args = { caseId: "", list: false, help: false };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") {
      args.help = true;
    } else if (token === "--case") {
      args.caseId = argv[index + 1] || "";
      index += 1;
    } else if (token === "--list") {
      args.list = true;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  return args;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function runJson(scriptPath, args) {
  const result = spawnSync(process.execPath, [scriptPath, ...args], {
    encoding: "utf8",
    maxBuffer: 10 * 1024 * 1024,
  });

  if (result.status !== 0) {
    throw new Error(result.stderr?.trim() || `Script failed: ${scriptPath}`);
  }

  try {
    return JSON.parse(result.stdout);
  } catch (error) {
    throw new Error(`Could not parse JSON from ${scriptPath}: ${error instanceof Error ? error.message : String(error)}`);
  }
}

function pushCheck(checks, name, expected, actual, pass) {
  checks.push({ name, expected, actual, pass: Boolean(pass) });
}

function includesAll(actualList, expectedList) {
  return expectedList.every((value) => actualList.includes(value));
}

function evaluateScenario(entry, golden, paths) {
  const root = path.join(paths.packRoot, entry.fixtureRoot);
  const planner = runJson(paths.planScript, ["--root", root, "--target", entry.targetFile, "--task", entry.task]);
  const anti = runJson(paths.antiScript, ["--root", root]);
  const checks = [];

  pushCheck(checks, "repo router", golden.repoRouter, planner.repo.router, planner.repo.router === golden.repoRouter);
  pushCheck(checks, "package strategy", golden.packageStrategy, planner.decision.packageStrategy, planner.decision.packageStrategy === golden.packageStrategy);
  pushCheck(checks, "recommended import path", golden.recommendedImportPath, planner.decision.recommendedImportPath, planner.decision.recommendedImportPath === golden.recommendedImportPath);
  pushCheck(checks, "recommended boundary", golden.recommendedBoundary, planner.decision.recommendedBoundary, planner.decision.recommendedBoundary === golden.recommendedBoundary);
  pushCheck(checks, "recommended pattern", golden.recommendedPattern, planner.decision.recommendedPattern, planner.decision.recommendedPattern === golden.recommendedPattern);
  pushCheck(
    checks,
    "likely files to change",
    golden.likelyFilesToChange,
    planner.decision.likelyFilesToChange,
    includesAll(planner.decision.likelyFilesToChange || [], golden.likelyFilesToChange || [])
  );
  pushCheck(
    checks,
    "anti-pattern errors",
    0,
    anti.summary.errors,
    anti.summary.errors === 0
  );

  const pass = checks.every((check) => check.pass);
  return {
    id: entry.id,
    type: entry.type,
    pass,
    checks,
    planner,
    antiPatternSummary: anti.summary,
  };
}

function evaluateAntiPattern(entry, golden, paths) {
  const root = path.join(paths.packRoot, entry.fixtureRoot);
  const anti = runJson(paths.antiScript, ["--root", root]);
  const ruleIds = anti.issues.map((issue) => issue.ruleId);
  const checks = [];

  for (const ruleId of golden.expectedRuleIds || []) {
    pushCheck(checks, `expected rule ${ruleId}`, true, ruleIds.includes(ruleId), ruleIds.includes(ruleId));
  }

  if (typeof golden.minimumErrorCount === "number") {
    pushCheck(checks, "minimum error count", golden.minimumErrorCount, anti.summary.errors, anti.summary.errors >= golden.minimumErrorCount);
  }

  const pass = checks.every((check) => check.pass);
  return {
    id: entry.id,
    type: entry.type,
    pass,
    checks,
    antiPatternSummary: anti.summary,
    issues: anti.issues,
  };
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(`${HELP}\n`);
    return;
  }

  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const skillRoot = path.resolve(path.join(scriptDir, ".."));
  const packRoot = path.join(skillRoot, "assets", "evaluation-pack");
  const manifest = readJson(path.join(packRoot, "manifest.json"));
  const cases = manifest.scenarios || [];

  if (args.list) {
    process.stdout.write(`${JSON.stringify({ cases: cases.map((entry) => ({ id: entry.id, type: entry.type })) }, null, 2)}\n`);
    return;
  }

  const selected = args.caseId ? cases.filter((entry) => entry.id === args.caseId) : cases;
  if (args.caseId && selected.length === 0) {
    throw new Error(`Unknown case id: ${args.caseId}`);
  }

  const paths = {
    packRoot,
    planScript: path.join(scriptDir, "plan-motion-change.mjs"),
    antiScript: path.join(scriptDir, "check-motion-antipatterns.mjs"),
  };

  const results = [];
  for (const entry of selected) {
    const golden = readJson(path.join(packRoot, entry.goldenJson));
    if (entry.type === "scenario") {
      results.push(evaluateScenario(entry, golden, paths));
    } else if (entry.type === "anti-pattern") {
      results.push(evaluateAntiPattern(entry, golden, paths));
    } else {
      throw new Error(`Unsupported case type: ${entry.type}`);
    }
  }

  const passed = results.filter((result) => result.pass).length;
  const failed = results.length - passed;

  const output = {
    manifestVersion: manifest.version || 1,
    casesRun: results.length,
    passed,
    failed,
    results,
  };

  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
}

try {
  main();
} catch (error) {
  process.stderr.write(`Error: ${error instanceof Error ? error.message : String(error)}\n`);
  process.stderr.write(`${HELP}\n`);
  process.exit(1);
}
