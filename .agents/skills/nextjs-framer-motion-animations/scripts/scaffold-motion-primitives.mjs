#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HELP = `Usage: node scripts/scaffold-motion-primitives.mjs --target PATH [options]

Copy template Motion components from assets/ into a target directory.
Prints JSON to stdout describing copied files.

Options:
  --target PATH           Destination directory. Required.
  --package NAME         motion | framer-motion (default: motion)
  --overwrite            Replace existing files.
  --include LIST         Comma-separated asset basenames to copy.
  --help                 Show this help text.

Examples:
  node scripts/scaffold-motion-primitives.mjs --target ../my-app/components/motion
  node scripts/scaffold-motion-primitives.mjs --target ../my-app/components/motion --package framer-motion --overwrite
`;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const assetsDir = path.resolve(__dirname, "..", "assets");

function parseArgs(argv) {
  const args = {
    target: "",
    packageName: "motion",
    overwrite: false,
    include: null,
    help: false,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--help" || token === "-h") {
      args.help = true;
    } else if (token === "--target") {
      args.target = argv[i + 1];
      i += 1;
    } else if (token === "--package") {
      args.packageName = argv[i + 1];
      i += 1;
    } else if (token === "--overwrite") {
      args.overwrite = true;
    } else if (token === "--include") {
      args.include = argv[i + 1]
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean);
      i += 1;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  if (!args.help && !args.target) {
    throw new Error("--target is required.");
  }

  if (!["motion", "framer-motion"].includes(args.packageName)) {
    throw new Error(`--package must be "motion" or "framer-motion". Received: ${args.packageName}`);
  }

  return args;
}

function listAssets() {
  return fs
    .readdirSync(assetsDir, { withFileTypes: true })
    .filter((entry) => entry.isFile())
    .map((entry) => entry.name)
    .sort();
}

function rewriteImports(text, packageName) {
  if (packageName === "motion") return text;

  return text
    .replaceAll('"motion/react"', '"framer-motion"')
    .replaceAll("'motion/react'", "'framer-motion'")
    .replaceAll('"motion/react-m"', '"framer-motion"')
    .replaceAll("'motion/react-m'", "'framer-motion'")
    .replaceAll('"motion/react-mini"', '"framer-motion"')
    .replaceAll("'motion/react-mini'", "'framer-motion'");
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    process.stdout.write(`${HELP}\n`);
    return;
  }

  const targetDir = path.resolve(args.target);
  const availableAssets = listAssets();
  const selected = args.include
    ? availableAssets.filter((file) => args.include.includes(path.basename(file, path.extname(file))) || args.include.includes(file))
    : availableAssets;

  if (selected.length === 0) {
    throw new Error("No assets selected.");
  }

  fs.mkdirSync(targetDir, { recursive: true });

  const copied = [];
  const skipped = [];
  const incompatible = [];

  for (const fileName of selected) {
    const source = path.join(assetsDir, fileName);
    const destination = path.join(targetDir, fileName);

    if (fs.existsSync(destination) && !args.overwrite) {
      skipped.push(destination);
      continue;
    }

    const raw = fs.readFileSync(source, "utf8");

    if (args.packageName === "framer-motion" && (raw.includes("motion/react-client") || raw.includes("motion/react-mini"))) {
      incompatible.push(destination);
      continue;
    }

    const rewritten = rewriteImports(raw, args.packageName);
    fs.writeFileSync(destination, rewritten, "utf8");
    copied.push(destination);
  }

  const result = {
    target: targetDir,
    packageName: args.packageName,
    copied,
    skipped,
    incompatible,
    availableAssets,
  };

  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

try {
  main();
} catch (error) {
  process.stderr.write(`Error: ${error instanceof Error ? error.message : String(error)}\n`);
  process.stderr.write(`${HELP}\n`);
  process.exit(1);
}
