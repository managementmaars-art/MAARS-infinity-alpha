#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const HELP = `Usage: node scripts/check-motion-antipatterns.mjs [--root PATH]

Scan a Next.js repo for common Motion / Framer Motion anti-patterns. Prints JSON to stdout.

Options:
  --root PATH   Repository root to inspect. Defaults to current working directory.
  --help        Show this help text.

Examples:
  node scripts/check-motion-antipatterns.mjs --root ../my-app
  node scripts/check-motion-antipatterns.mjs
`;

const IGNORE_DIRS = new Set([
  ".git",
  ".next",
  ".turbo",
  "node_modules",
  "dist",
  "build",
  "coverage",
  "out",
  ".cache",
]);

const SOURCE_DIRS = [
  "app",
  "src/app",
  "pages",
  "src/pages",
  "components",
  "src/components",
  "ui",
  "src/ui",
];

const SOURCE_EXTS = new Set([".ts", ".tsx", ".js", ".jsx", ".mdx"]);

function parseArgs(argv) {
  const args = { root: process.cwd(), help: false };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") {
      args.help = true;
    } else if (token === "--root") {
      args.root = argv[index + 1];
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  return args;
}

function exists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function readText(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

function iterSourceFiles(root) {
  const files = [];

  function walk(start) {
    let entries = [];
    try {
      entries = fs.readdirSync(start, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const absolute = path.join(start, entry.name);
      if (entry.isDirectory()) {
        if (IGNORE_DIRS.has(entry.name)) continue;
        walk(absolute);
        continue;
      }
      if (SOURCE_EXTS.has(path.extname(entry.name))) {
        files.push(absolute);
      }
    }
  }

  for (const base of SOURCE_DIRS) {
    const start = path.join(root, base);
    if (exists(start)) walk(start);
  }

  return files;
}

function isClientComponent(text) {
  return /^\s*["']use client["'];?/m.test(text);
}

function inAppRouter(relativePath) {
  const value = relativePath.replaceAll(path.sep, "/").toLowerCase();
  return value.startsWith("app/") || value.startsWith("src/app/");
}

function lineNumberFor(text, matchIndex) {
  if (matchIndex < 0) return null;
  return text.slice(0, matchIndex).split(/\r?\n/).length;
}

function addIssue(issues, { ruleId, severity, path: filePath, message, line = null }) {
  issues.push({ ruleId, severity, path: filePath, line, message });
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(`${HELP}\n`);
    return;
  }

  const root = path.resolve(args.root);
  if (!exists(root)) {
    throw new Error(`Root does not exist: ${root}`);
  }

  const files = iterSourceFiles(root);
  const issues = [];
  const importSummary = {
    "motion/react": 0,
    "motion/react-client": 0,
    "motion/react-m": 0,
    "framer-motion": 0,
  };

  let reducedMotionSignals = 0;

  for (const absolutePath of files) {
    const relativePath = path.relative(root, absolutePath).replaceAll(path.sep, "/");
    const text = readText(absolutePath);
    if (!text) continue;

    const clientComponent = isClientComponent(text);
    const imports = {
      "motion/react": /from\s+["']motion\/react["']/.test(text),
      "motion/react-client": /from\s+["']motion\/react-client["']/.test(text),
      "motion/react-m": /from\s+["']motion\/react-m["']/.test(text),
      "framer-motion": /from\s+["']framer-motion["']/.test(text),
    };

    for (const [name, present] of Object.entries(imports)) {
      if (present) importSummary[name] += 1;
    }

    if (text.includes("useReducedMotion") || text.includes("MotionConfig")) {
      reducedMotionSignals += 1;
    }

    if (
      inAppRouter(relativePath) &&
      !clientComponent &&
      (imports["motion/react"] || imports["framer-motion"])
    ) {
      addIssue(issues, {
        ruleId: "app-router-server-imports-client-motion",
        severity: "error",
        path: relativePath,
        line: 1,
        message: "App Router server file imports motion/react or framer-motion directly. Move the animated part into a client leaf or use motion/react-client for passive cases.",
      });
    }

    if (
      (relativePath === "app/layout.tsx" || relativePath === "src/app/layout.tsx") &&
      clientComponent
    ) {
      addIssue(issues, {
        ruleId: "root-layout-client",
        severity: "warning",
        path: relativePath,
        line: 1,
        message: "Root App Router layout is a Client Component. Avoid widening this boundary unless the route truly needs a global client shell.",
      });
    }

    if (
      imports["motion/react-client"] &&
      (clientComponent ||
        /\buse(State|Reducer|Effect|LayoutEffect|Ref)\s*\(/.test(text) ||
        /\bon(Click|PointerDown|MouseEnter|MouseLeave|KeyDown)\s*=/.test(text))
    ) {
      addIssue(issues, {
        ruleId: "motion-react-client-with-hooks-or-client-directive",
        severity: "warning",
        path: relativePath,
        line: 1,
        message: "motion/react-client is intended for passive server-friendly components. This file is client-driven or interactive, so motion/react is the safer fit.",
      });
    }

    if (text.includes("AnimatePresence") && /\bkey=\{(?:index|idx|i)\}/.test(text)) {
      addIssue(issues, {
        ruleId: "animatepresence-index-key",
        severity: "error",
        path: relativePath,
        line: lineNumberFor(text, text.search(/\bkey=\{(?:index|idx|i)\}/)),
        message: "AnimatePresence child appears to use an index-based key. Use a stable item identifier instead.",
      });
    }

    if (text.includes("AnimatePresence") && !/key=/.test(text)) {
      addIssue(issues, {
        ruleId: "animatepresence-missing-key",
        severity: "warning",
        path: relativePath,
        line: lineNumberFor(text, text.indexOf("AnimatePresence")),
        message: "AnimatePresence detected without an obvious key. Verify the direct child uses a stable key when presence depends on switching children.",
      });
    }

    if (
      /(?:animate|initial|exit)\s*=\s*\{\{[\s\S]{0,200}\b(?:top|left|right|bottom)\b[\s\S]{0,200}\}\}/m.test(text)
    ) {
      addIssue(issues, {
        ruleId: "top-left-animation",
        severity: "warning",
        path: relativePath,
        line: lineNumberFor(text, text.search(/(?:animate|initial|exit)\s*=\s*\{\{/m)),
        message: "Detected top/left/right/bottom animation. Prefer transform-based x/y motion for better performance.",
      });
    }

    if (
      text.includes("layoutId") &&
      text.includes(".map(") &&
      (!text.includes("LayoutGroup") || !/LayoutGroup[^>]*\sid=/.test(text))
    ) {
      addIssue(issues, {
        ruleId: "layoutid-without-layoutgroup-id",
        severity: "warning",
        path: relativePath,
        line: lineNumberFor(text, text.indexOf("layoutId")),
        message: "layoutId appears inside a repeated context without a LayoutGroup id namespace. Repeated widgets can collide.",
      });
    }

    if (/^\s{2,}(?:const|let|var)\s+\w+\s*=\s*motion\.create\(/m.test(text)) {
      addIssue(issues, {
        ruleId: "motion-create-in-render",
        severity: "warning",
        path: relativePath,
        line: lineNumberFor(text, text.search(/^\s{2,}(?:const|let|var)\s+\w+\s*=\s*motion\.create\(/m)),
        message: "motion.create() appears inside an indented block, which usually means inside render. Hoist it to module scope.",
      });
    }

    if (text.includes("Reorder.Item") && !text.includes("Reorder.Group")) {
      addIssue(issues, {
        ruleId: "reorder-item-without-group",
        severity: "error",
        path: relativePath,
        line: lineNumberFor(text, text.indexOf("Reorder.Item")),
        message: "Reorder.Item detected without Reorder.Group in the same file. Verify the item sits inside a matching group.",
      });
    }
  }

  if (
    importSummary["framer-motion"] > 0 &&
    (importSummary["motion/react"] > 0 || importSummary["motion/react-client"] > 0 || importSummary["motion/react-m"] > 0)
  ) {
    addIssue(issues, {
      ruleId: "mixed-import-packages",
      severity: "error",
      path: "(repo)",
      line: null,
      message: "Both framer-motion and motion import styles were detected. Preserve one package strategy per edited scope unless doing an explicit migration.",
    });
  }

  const motionImportCount = Object.values(importSummary).reduce((sum, value) => sum + value, 0);
  if (motionImportCount > 0 && reducedMotionSignals === 0) {
    addIssue(issues, {
      ruleId: "reduced-motion-missing",
      severity: "warning",
      path: "(repo)",
      line: null,
      message: "Motion imports were found but no useReducedMotion or MotionConfig reduced-motion handling was detected.",
    });
  }

  const summary = {
    errors: issues.filter((issue) => issue.severity === "error").length,
    warnings: issues.filter((issue) => issue.severity === "warning").length,
    importSummary,
    reducedMotionSignals,
  };

  const result = { root, summary, issues };
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
}

try {
  main();
} catch (error) {
  process.stderr.write(`Error: ${error instanceof Error ? error.message : String(error)}\n`);
  process.stderr.write(`${HELP}\n`);
  process.exit(1);
}
