import fs from "node:fs/promises";
import { createRequire } from "node:module";
import os from "node:os";
import path from "node:path";
import { findCommandOnPath } from "./shell.js";

const require = createRequire(import.meta.url);
const { version: packageVersion } = require("../package.json");

const defaultStorageDir = path.join(os.homedir(), ".kodevu");
const SUPPORTED_REVIEWERS = ["codex", "gemini", "copilot", "openai", "opencode"];
const AUTO_SUPPORTED_REVIEWERS = ["codex", "gemini", "copilot", "opencode"];

const defaultConfig = {
  reviewer: "auto",
  target: "",
  lang: "auto",
  outputDir: defaultStorageDir,
  logsDir: path.join(defaultStorageDir, "logs"),
  commandTimeoutMs: 120000,
  prompt: "",
  maxRevisionsPerRun: 5,
  outputFormats: ["markdown"],
  rev: "",
  last: 0,
  uncommitted: false,
  openaiApiKey: "",
  openaiBaseUrl: "https://api.openai.com/v1",
  openaiModel: "gpt-5-mini",
  openaiOrganization: "",
  openaiProject: ""
};

function mkCliError(message) {
  const e = new Error(message);
  // exit code 2 = usage / configuration errors
  e.exitCode = 2;
  return e;
}

const ENV_MAP = {
  KODEVU_REVIEWER: "reviewer",
  KODEVU_LANG: "lang",
  KODEVU_OUTPUT_DIR: "outputDir",
  KODEVU_PROMPT: "prompt",
  KODEVU_TIMEOUT: "commandTimeoutMs",
  KODEVU_MAX_REVISIONS: "maxRevisionsPerRun",
  KODEVU_FORMATS: "outputFormats",
  KODEVU_OPENAI_API_KEY: "openaiApiKey",
  KODEVU_OPENAI_BASE_URL: "openaiBaseUrl",
  KODEVU_OPENAI_MODEL: "openaiModel",
  KODEVU_OPENAI_ORG: "openaiOrganization",
  KODEVU_OPENAI_PROJECT: "openaiProject"
};

const CONFIG_FILE_KEYS = new Set(Object.values(ENV_MAP));
const defaultConfigFilePath = path.join(defaultStorageDir, "config.json");

function resolvePath(value) {
  if (!value) return value;
  if (value === "~") return os.homedir();
  if (value.startsWith("~/") || value.startsWith("~\\")) {
    return path.join(os.homedir(), value.slice(2));
  }
  return path.isAbsolute(value) ? value : path.resolve(process.cwd(), value);
}

async function loadConfigFile(configPath = defaultConfigFilePath) {
  const resolvedPath = resolvePath(configPath);
  let content;
  try {
    content = await fs.readFile(resolvedPath, "utf8");
  } catch (err) {
    if (err.code === "ENOENT") return {};
    throw mkCliError(`Failed to read config file ${resolvedPath}: ${err.message}`);
  }
  let parsed;
  try {
    parsed = JSON.parse(content);
  } catch (err) {
    throw mkCliError(`Invalid JSON in config file ${resolvedPath}: ${err.message}`);
  }
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw mkCliError(`Config file ${resolvedPath} must contain a JSON object`);
  }
  const result = {};
  for (const [key, value] of Object.entries(parsed)) {
    if (CONFIG_FILE_KEYS.has(key)) {
      result[key] = value;
    }
  }
  return result;
}

function normalizeOutputFormats(outputFormats) {
  const source = outputFormats == null ? ["markdown"] : outputFormats;
  const values = Array.isArray(source) ? source : String(source).split(",");
  const normalized = [...new Set(values.map((item) => String(item || "").trim().toLowerCase()).filter(Boolean))];
  const supported = ["markdown", "json"];
  const invalid = normalized.filter((item) => !supported.includes(item));

  if (invalid.length > 0) {
    throw mkCliError(`Unsupported output format(s): ${invalid.join(", ")}. Use: ${supported.join(", ")}`);
  }
  return normalized.length === 0 ? ["markdown"] : normalized;
}

export function detectLanguage() {
  const envLang = (process.env.LANG || process.env.LC_ALL || process.env.LC_MESSAGES || "").toLowerCase();
  const intlLocale = (() => {
    try {
      return Intl.DateTimeFormat().resolvedOptions().locale.toLowerCase();
    } catch {
      return "";
    }
  })();

  const locales = [envLang, intlLocale].filter(l => l && l !== "und");

  // 1. Search for Chinese in any source first, to avoid "fake" English defaults in some shells on Windows
  for (const loc of locales) {
    if (loc.startsWith("zh")) return "zh";
  }

  // 2. Search for English
  for (const loc of locales) {
    if (loc.startsWith("en")) return "en";
  }

  // 3. Fallback to the first part of the first detected locale, or "en"
  return locales[0]?.split(/[._-]/)[0] || "en";
}

async function resolveAutoReviewers(debug) {
  const availableReviewers = [];
  for (const reviewerName of AUTO_SUPPORTED_REVIEWERS) {
    const commandPath = await findCommandOnPath(reviewerName, { debug });
    if (commandPath) availableReviewers.push({ reviewerName, commandPath });
  }

  if (availableReviewers.length === 0) {
    throw mkCliError(`No reviewer CLI found in PATH. Install one of: ${AUTO_SUPPORTED_REVIEWERS.join(", ")}`);
  }

  // Shuffle for variety
  for (let i = availableReviewers.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [availableReviewers[i], availableReviewers[j]] = [availableReviewers[j], availableReviewers[i]];
  }

  return availableReviewers;
}

export function parseCliArgs(argv) {
  const args = {
    target: "",
    debug: false,
    help: false,
    version: false,
    reviewer: "",
    lang: "",
    prompt: "",
    rev: "",
    last: "",
    uncommitted: false,
    outputDir: "",
    outputFormats: "",
    openaiApiKey: "",
    openaiBaseUrl: "",
    openaiModel: "",
    openaiOrganization: "",
    openaiProject: ""
  };

  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];

    if (value === "--help" || value === "-h") {
      args.help = true;
      continue;
    }

    if (value === "--version" || value === "-V") {
      args.version = true;
      continue;
    }

    if (value === "--debug" || value === "-d") {
      args.debug = true;
      continue;
    }

    const nextValue = argv[index + 1];
    const hasNextValue = nextValue && !nextValue.startsWith("-");

    if (value === "--reviewer" || value === "-r") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.reviewer = nextValue;
      index += 1;
      continue;
    }

    if (value === "--prompt" || value === "-p") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.prompt = nextValue;
      index += 1;
      continue;
    }

    if (value === "--lang" || value === "-l") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.lang = nextValue;
      index += 1;
      continue;
    }

    if (value === "--rev" || value === "-v") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.rev = nextValue;
      index += 1;
      continue;
    }

    if (value === "--last" || value === "-n") {
      const hasLastValue = nextValue !== undefined && /^-?\d+$/.test(nextValue);
      if (!hasLastValue) throw mkCliError(`Missing value for ${value}`);
      args.last = nextValue;
      index += 1;
      continue;
    }

    if (value === "--uncommitted" || value === "-u") {
      args.uncommitted = true;
      continue;
    }

    if (value === "--output" || value === "-o") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.outputDir = nextValue;
      index += 1;
      continue;
    }

    if (value === "--format" || value === "-f") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.outputFormats = nextValue;
      index += 1;
      continue;
    }

    if (value === "--openai-api-key") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.openaiApiKey = nextValue;
      index += 1;
      continue;
    }

    if (value === "--openai-base-url") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.openaiBaseUrl = nextValue;
      index += 1;
      continue;
    }

    if (value === "--openai-model") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.openaiModel = nextValue;
      index += 1;
      continue;
    }

    if (value === "--openai-org") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.openaiOrganization = nextValue;
      index += 1;
      continue;
    }

    if (value === "--openai-project") {
      if (!hasNextValue) throw mkCliError(`Missing value for ${value}`);
      args.openaiProject = nextValue;
      index += 1;
      continue;
    }

    if (!value.startsWith("-") && !args.target) {
      args.target = value;
      continue;
    }

    throw mkCliError(`Unexpected argument: ${value}`);
  }

  return args;
}

export async function resolveConfig(cliArgs = {}) {
  const config = { ...defaultConfig };

  // 0. Merge Config File (lowest priority: overridden by env vars and CLI args)
  const fileConfig = await loadConfigFile();
  for (const key of CONFIG_FILE_KEYS) {
    if (fileConfig[key] !== undefined && fileConfig[key] !== "") {
      config[key] = fileConfig[key];
    }
  }

  // 1. Merge Environment Variables
  for (const [envVar, configKey] of Object.entries(ENV_MAP)) {
    if (process.env[envVar] !== undefined) {
      config[configKey] = process.env[envVar];
    }
  }

  // 2. Merge CLI Arguments
  for (const key of [
    "target",
    "reviewer",
    "prompt",
    "lang",
    "rev",
    "last",
    "uncommitted",
    "outputDir",
    "outputFormats",
    "openaiApiKey",
    "openaiBaseUrl",
    "openaiModel",
    "openaiOrganization",
    "openaiProject"
  ]) {
    if (cliArgs[key] !== undefined && cliArgs[key] !== "") {
      config[key] = cliArgs[key];
    }
  }

  if (cliArgs.rev && cliArgs.last) {
    throw mkCliError("Parameters --rev and --last are mutually exclusive. Please specify only one.");
  }

  if (cliArgs.uncommitted && (cliArgs.rev || cliArgs.last)) {
    throw mkCliError("Parameter --uncommitted is mutually exclusive with --rev and --last.");
  }

  if (!config.target) {
    config.target = process.cwd();
  }

  config.baseDir = process.cwd();
  config.debug = Boolean(cliArgs.debug);
  config.reviewer = String(config.reviewer || "auto").toLowerCase();
  config.lang = String(config.lang || "auto").toLowerCase();
  config.resolvedLang = config.lang === "auto" ? detectLanguage() : config.lang;

  // Handle @file prompt
  if (config.prompt.startsWith("@")) {
    const promptPath = resolvePath(config.prompt.slice(1));
    try {
      config.prompt = await fs.readFile(promptPath, "utf8");
    } catch (err) {
      throw mkCliError(`Failed to read prompt file: ${promptPath} (${err.message})`);
    }
  }

  if (config.reviewer === "auto") {
    const availableReviewers = await resolveAutoReviewers(config.debug);
    const selectedReviewer = availableReviewers[0];
    config.reviewer = selectedReviewer.reviewerName;
    config.reviewerCommandPath = selectedReviewer.commandPath;
    config.fallbackReviewers = availableReviewers.map(r => r.reviewerName).slice(1);
    config.reviewerWasAutoSelected = true;
  } else if (!SUPPORTED_REVIEWERS.includes(config.reviewer)) {
    throw mkCliError(`"reviewer" must be one of: ${SUPPORTED_REVIEWERS.join(", ")}, or "auto"`);
  }

  config.outputDir = resolvePath(config.outputDir);
  config.logsDir = path.join(config.outputDir, "logs");
  config.maxRevisionsPerRun = Number(config.maxRevisionsPerRun);
  config.commandTimeoutMs = Number(config.commandTimeoutMs);
  config.last = Number(config.last);
  config.uncommitted = Boolean(config.uncommitted);
  config.outputFormats = normalizeOutputFormats(config.outputFormats);
  config.openaiApiKey = String(config.openaiApiKey || "").trim();
  config.openaiBaseUrl = String(config.openaiBaseUrl || defaultConfig.openaiBaseUrl).trim().replace(/\/+$/, "");
  config.openaiModel = String(config.openaiModel || defaultConfig.openaiModel).trim();
  config.openaiOrganization = String(config.openaiOrganization || "").trim();
  config.openaiProject = String(config.openaiProject || "").trim();

  if (!config.uncommitted && !config.rev && (isNaN(config.last) || config.last === 0)) {
    config.last = 1;
  }

  if (config.reviewer === "openai" && !config.openaiApiKey) {
    throw mkCliError('Reviewer "openai" requires an API key. Set KODEVU_OPENAI_API_KEY or pass --openai-api-key.');
  }

  return config;
}

export function printHelp() {
  console.log(`Kodevu v${packageVersion}

Usage:
  npx kodevu [target] [options]

Options:
  --target, <path>  Target repository path (default: current directory)
  --reviewer, -r    Reviewer (codex | gemini | copilot | openai | opencode | auto, default: auto)
  --prompt, -p      Additional instructions or @file.txt to read from file
  --lang, -l        Output language (e.g. zh, en, auto)
  --rev, -v         Review specific revision(s), hashes, branches or ranges (comma-separated)
  --last, -n        Review the latest N revisions; use negative (-N) to review only the Nth-from-last revision (default: 1)
  --uncommitted, -u    Review current uncommitted changes (mutually exclusive with --rev and --last)
  --output, -o      Output directory (default: ~/.kodevu)
  --format, -f      Output formats (markdown, json, comma-separated)
  --openai-api-key  API key used when reviewer=openai
  --openai-base-url Base URL used when reviewer=openai (default: https://api.openai.com/v1)
  --openai-model    Model used when reviewer=openai (default: gpt-5-mini)
  --openai-org      Optional OpenAI organization ID
  --openai-project  Optional OpenAI project ID
  --debug, -d       Show extra debug information on the console
  --help, -h        Show help
  --version, -V     Show version

Environment Variables:
  KODEVU_REVIEWER   Default reviewer
  KODEVU_LANG       Default language
  KODEVU_OUTPUT_DIR Default output directory
  KODEVU_PROMPT     Default prompt text
  KODEVU_TIMEOUT    Reviewer timeout in ms
  KODEVU_OPENAI_API_KEY   API key for reviewer=openai
  KODEVU_OPENAI_BASE_URL  Base URL for reviewer=openai
  KODEVU_OPENAI_MODEL     Model for reviewer=openai
  KODEVU_OPENAI_ORG       Organization ID for reviewer=openai
  KODEVU_OPENAI_PROJECT   Project ID for reviewer=openai

Config File:
  ~/.kodevu/config.json   Optional persistent settings (overridden by env vars and CLI flags)
  Supported keys: reviewer, lang, outputDir, prompt, commandTimeoutMs, outputFormats,
                  openaiApiKey, openaiBaseUrl, openaiModel, openaiOrganization, openaiProject
  Example: { "reviewer": "openai", "openaiApiKey": "sk-...", "openaiModel": "gpt-4o" }
`);
}

export function printVersion() {
  console.log(packageVersion);
}
