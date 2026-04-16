#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const HELP = `Usage: node scripts/plan-motion-change.mjs --root PATH --target FILE --task "TASK"

Combine repo audit + target inspection + task wording into a structured Motion plan.

Required options:
  --root PATH      Repository root to inspect.
  --target FILE    Target file to inspect, relative to --root or absolute.
  --task TEXT      The requested animation task.

Optional:
  --help           Show this help text.

Examples:
  node scripts/plan-motion-change.mjs --root ../my-app --target app/page.tsx --task "Add a subtle reveal to these cards"
  node scripts/plan-motion-change.mjs --root . --target pages/_app.tsx --task "Add route transitions between blog pages"
`;

function parseArgs(argv) {
  const args = { root: "", target: "", task: "", help: false };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === "--help" || token === "-h") {
      args.help = true;
    } else if (token === "--root") {
      args.root = argv[index + 1] || "";
      index += 1;
    } else if (token === "--target") {
      args.target = argv[index + 1] || "";
      index += 1;
    } else if (token === "--task") {
      args.task = argv[index + 1] || "";
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  if (!args.help && (!args.root || !args.target || !args.task)) {
    throw new Error("--root, --target, and --task are required.");
  }

  return args;
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

function hasAny(text, patterns) {
  return patterns.some((pattern) => pattern.test(text));
}

function inferTaskIntents(task) {
  const value = task.toLowerCase();
  const checks = [
    { intent: "migration", patterns: [/\bmigrat(e|ion|ing)\b/, /\bswitch\b.*\bframer[- ]motion\b/, /\bswap imports\b/] },
    { intent: "route-transition", patterns: [/\broute transitions?\b/, /\bpage transitions?\b/, /\broute-content transition\b/, /\bbetween routes\b/, /\bbetween pages\b/, /\btransition\b.*\bbetween\b.*\bpages?\b/, /\bnavigation\b/, /\bpathname\b/] },
    { intent: "presence", patterns: [/\bmodal\b/, /\bdrawer\b/, /\bdialog\b/, /\bdropdown\b/, /\bpopover\b/, /\btoast\b/, /\bexit animations?\b/, /\bopen(?:\/| )close\b/] },
    { intent: "shared-layout", patterns: [/\bshared element\b/, /\bshared layout\b/, /\blayoutid\b/, /\btab underline\b/, /\bunderline\b/, /\bselected pill\b/] },
    { intent: "layout", patterns: [/\baccordion\b/, /\bexpand\b/, /\bcollapse\b/, /\blayout animation\b/, /\breflow\b/] },
    { intent: "reorder", patterns: [/\breorder\b/, /\bsortable\b/, /\bdrag to reorder\b/, /\bdrag-and-drop\b/, /\bdrag and drop\b/] },
    { intent: "scroll-linked", patterns: [/\bparallax\b/, /\bscroll-linked\b/, /\bscroll linked\b/, /\bscroll progress\b/, /\bprogress bar\b/] },
    { intent: "scroll-reveal", patterns: [/\bon scroll\b/, /\bin view\b/, /\binto view\b/, /\bwhileinview\b/, /\bviewport\b/, /\bscroll reveal\b/] },
    { intent: "design-system", patterns: [/\bdesign system\b/, /\bdesign-system\b/, /\bforwardref\b/, /\bforward ref\b/, /\bwrapper div\b/, /\bwrapper element\b/, /\bmotion\.create\b/] },
    { intent: "microinteraction", patterns: [/\bhover\b/, /\btap\b/, /\bfocus\b/, /\bbutton\b/, /\blink\b/, /\bcard\b/, /\bfeel better\b/, /\bsnappier\b/, /\bmicro-?interaction\b/, /\bcta\b/] },
    { intent: "mount-reveal", patterns: [/\bfirst render\b/, /\bon load\b/, /\bmount\b/, /\bfade in\b/, /\bfade-in\b/, /\breveal\b/, /\bentrance\b/] },
    { intent: "performance", patterns: [/\bbundle\b/, /\bjank\b/, /\bperformance\b/, /\bperf\b/, /\blazymotion\b/, /\bdomanimation\b/, /\bdommax\b/] },
    { intent: "debugging", patterns: [/\bbroken\b/, /\bnot working\b/, /\bbug\b/, /\bdebug\b/, /\bhydration\b/, /\bmismatch\b/, /\bwhy\b.*\bexit\b/, /\bfix\b/] },
    { intent: "accessibility", patterns: [/\breduced motion\b/, /\baccessibility\b/, /\bprefers-reduced-motion\b/] },
  ];

  const intents = checks
    .filter((check) => hasAny(value, check.patterns))
    .map((check) => check.intent);

  if (intents.length === 0) intents.push("general-motion-edit");
  return intents;
}

function choosePackageStrategy(audit, intents) {
  const deps = audit.dependencies || {};
  const imports = audit.importStyleSummary || {};
  const hasMotion = Boolean(deps.motion || imports["motion/react"] || imports["motion/react-client"] || imports["motion/react-m"]);
  const hasFramer = Boolean(deps["framer-motion"] || imports["framer-motion"]);

  if (intents.includes("migration")) return "explicit-migration";
  if (hasMotion && hasFramer) return "mixed-repo-preserve-scope";
  if (hasFramer) return "keep-framer-motion";
  if (hasMotion) return "use-motion";
  return "install-motion";
}

function fallbackPatternFromTarget(target) {
  if (target.patternHints?.presence) return "presence";
  if (target.patternHints?.["scroll-linked"]) return "scroll-linked";
  if (target.patternHints?.["scroll-reveal"]) return "scroll-reveal";
  if (target.patternHints?.reorder) return "reorder";
  if (target.patternHints?.layout) return "layout";
  if (target.patternHints?.microinteraction) return "microinteraction";
  return "mount-reveal";
}

function choosePattern(intents, target, audit) {
  if (intents.includes("migration")) return "migration";
  if (intents.includes("route-transition")) {
    return audit.router === "pages-router" ? "pages-router-route-transition" : "route-transition-shell";
  }
  if (intents.includes("presence")) return "presence";
  if (intents.includes("shared-layout")) return "shared-layout";
  if (intents.includes("design-system")) return "design-system-motion-create";
  if (intents.includes("reorder")) return "reorder";
  if (intents.includes("scroll-linked")) return "scroll-linked";
  if (intents.includes("scroll-reveal")) return "scroll-reveal";
  if (intents.includes("layout")) return "layout";
  if (intents.includes("mount-reveal")) return "mount-reveal";
  if (intents.includes("microinteraction")) return "microinteraction";
  return fallbackPatternFromTarget(target);
}

function chooseBoundary(pattern, target, audit, packageStrategy) {
  if (pattern === "route-transition-shell") return "persistent-route-shell-under-layout";
  if (pattern === "pages-router-route-transition") return "pages-app-presence-wrapper";
  if (pattern === "migration") return "explicit-migration-scope";
  if (target.clientComponent) return "already-client";

  if (audit.router === "app-router") {
    if ([
      "presence",
      "shared-layout",
      "layout",
      "reorder",
      "scroll-linked",
      "design-system-motion-create",
    ].includes(pattern)) {
      return "small-client-leaf";
    }

    if (
      ["mount-reveal", "microinteraction", "scroll-reveal"].includes(pattern) &&
      packageStrategy !== "keep-framer-motion" &&
      !target.interactionSignalsPresent &&
      (target.hookHits || []).length === 0
    ) {
      return "server-friendly-motion-react-client-candidate";
    }

    return "small-client-leaf";
  }

  return "local-motion-edit";
}

function chooseImportPath(packageStrategy, boundary) {
  if (packageStrategy === "keep-framer-motion") return "framer-motion";
  if (packageStrategy === "mixed-repo-preserve-scope") return "inherit-from-edited-scope";
  if (packageStrategy === "explicit-migration") return "motion/react";
  if (boundary === "server-friendly-motion-react-client-candidate") return "motion/react-client";
  return "motion/react";
}

function chooseReducedMotionPlan(pattern) {
  if (pattern === "scroll-linked") {
    return "Disable parallax-style travel for reduced-motion users and fall back to static or opacity-only state.";
  }
  if (pattern === "route-transition-shell" || pattern === "pages-router-route-transition") {
    return "Keep route transitions to opacity plus very small travel, or disable travel entirely for reduced-motion users.";
  }
  if (pattern === "microinteraction" || pattern === "design-system-motion-create") {
    return "Retain feedback for reduced-motion users, but prefer opacity or colour changes over noticeable movement.";
  }
  if (pattern === "shared-layout") {
    return "Keep state indication clear even when movement is reduced; the active indicator can fade rather than travel dramatically.";
  }
  return "Use MotionConfig reducedMotion=\"user\" or useReducedMotion(), and switch large travel to opacity-only where appropriate.";
}

function choosePerformancePlan(pattern, boundary) {
  if (boundary === "server-friendly-motion-react-client-candidate") {
    return "Keep the file server-friendly with motion/react-client and animate only transform and opacity on the existing root element.";
  }
  if (pattern === "route-transition-shell") {
    return "Mount a tiny client shell under the stable layout instead of making the root layout itself a Client Component.";
  }
  if (pattern === "pages-router-route-transition") {
    return "Keep the change in pages/_app.tsx and avoid introducing a broader provider or route-wide animation system elsewhere.";
  }
  if (pattern === "design-system-motion-create") {
    return "Use motion.create() outside render so the wrapper is stable and avoid extra wrapper elements that can disturb layout or refs.";
  }
  if (pattern === "shared-layout") {
    return "Prefer layoutId plus LayoutGroup id over manual DOM measurement or coordinate syncing.";
  }
  return "Keep the client boundary as small as possible and prefer transform plus opacity over paint-heavy properties.";
}

function chooseFirstSteps(pattern, target, audit, importPath) {
  switch (pattern) {
    case "route-transition-shell":
      return [
        `Create a small client shell (for example components/motion/route-transition-shell.tsx) that imports from ${importPath}.`,
        `Render that shell from ${audit.boundaries?.appLayout || "app/layout.tsx"} without marking the layout itself as client.`,
        "Key the routed content by pathname and keep AnimatePresence mounted with initial={false}.",
      ];
    case "pages-router-route-transition":
      return [
        `Edit ${audit.boundaries?.pagesApp || "pages/_app.tsx"} and keep the repo on the existing import path.`,
        "Wrap the routed component with AnimatePresence and key it by router.asPath when dynamic param changes should animate.",
        "Use a restrained opacity plus y transition and avoid route-wide bounce.",
      ];
    case "presence":
      return [
        `Keep the change in ${target.path} if possible and import from ${importPath}.`,
        "Wrap the conditional child in AnimatePresence with a direct child and stable key when needed.",
        "Animate overlay opacity and panel opacity/y separately, with an opacity-only reduced-motion fallback.",
      ];
    case "shared-layout":
      return [
        `Edit ${target.path} and import LayoutGroup plus motion from ${importPath}.`,
        "Use layoutId for the moving indicator and namespace repeated widgets with LayoutGroup id.",
        "Prefer layout animation over manual coordinate math.",
      ];
    case "design-system-motion-create":
      return [
        `Edit ${target.path} and keep the wrapper in the existing component family.`,
        "Create the Motion-wrapped component with motion.create() outside render.",
        "Preserve ref forwarding and apply small whileHover/whileTap/whileFocus values.",
      ];
    case "mount-reveal":
      return [
        `Turn the existing root element in ${target.path} into a Motion element rather than adding a wrapper.`,
        `Use ${importPath} with a small initial opacity/y reveal.`,
        "Keep reduced-motion handling local and avoid widening the client boundary.",
      ];
    case "scroll-reveal":
      return [
        `Turn the existing root element in ${target.path} into a Motion element rather than adding a wrapper.`,
        `Use ${importPath} with whileInView and viewport={{ once: true }} unless repeated replay is required.`,
        "If the scroll container is not the window, set viewport.root explicitly.",
      ];
    case "microinteraction":
      return [
        `Edit ${target.path} and use ${importPath} on the existing interactive root element.`,
        "Apply whileHover plus whileTap plus whileFocus with restrained values.",
        "Avoid wrappers that could break refs, spacing, or CSS selectors.",
      ];
    case "reorder":
      return [
        `Keep the reorder work in ${target.path} and import Reorder from ${importPath}.`,
        "Use Reorder.Group and Reorder.Item together and update state from onReorder.",
        "Only use this for simple, single-column reorder interactions.",
      ];
    case "layout":
      return [
        `Edit ${target.path} and start with layout before manual size choreography.`,
        "If content distorts, add layout to affected children or try layout=\"position\".",
        "Use a spring for stateful layout movement rather than stacking reveal effects on top.",
      ];
    case "migration":
      return [
        "Plan the migration as an explicit package + import-path change, not as incidental cleanup inside another small animation task.",
        "Swap imports consistently within the migration scope and verify there is no mixed-package residue afterward.",
        "Retest reduced motion, route transitions, and shared-layout behaviours after the import-path change.",
      ];
    default:
      return [
        `Edit ${target.path} and prefer the smallest possible Motion change.`,
        "Keep imports consistent with the repo choice and avoid new global providers.",
        "Verify reduced motion and build stability before finishing.",
      ];
  }
}

function chooseValidation(pattern, boundary) {
  const checks = [
    "No mixed motion/framer-motion imports in the edited scope",
    "Reduced motion behaves intentionally",
    "Transform/opacity are favoured over paint-heavy properties",
  ];

  if (boundary === "persistent-route-shell-under-layout") {
    checks.push("AnimatePresence stays mounted across route changes");
    checks.push("The root App Router layout remains server-side");
  }
  if (boundary === "pages-app-presence-wrapper") {
    checks.push("pages/_app.tsx keys routed children by a value that actually changes");
  }
  if (pattern === "presence") {
    checks.push("Exit animations use direct children and stable keys");
  }
  if (pattern === "shared-layout") {
    checks.push("Repeated widgets use LayoutGroup id when layoutId is reused");
  }
  if (pattern === "design-system-motion-create") {
    checks.push("motion.create() is outside render and refs still work");
  }
  if (pattern === "scroll-reveal") {
    checks.push("The viewport root is correct for non-window scrollers");
  }
  if (pattern === "reorder") {
    checks.push("Reorder.Item remains inside Reorder.Group");
  }

  return checks;
}

function likelyFilesToChange(pattern, target, audit) {
  if (pattern === "route-transition-shell") {
    return [
      audit.boundaries?.appLayout || "app/layout.tsx",
      "components/motion/route-transition-shell.tsx",
    ];
  }
  if (pattern === "pages-router-route-transition") {
    return [audit.boundaries?.pagesApp || "pages/_app.tsx"];
  }
  return [target.path];
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(`${HELP}\n`);
    return;
  }

  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const auditPath = path.join(scriptDir, "audit-nextjs-motion.mjs");
  const inspectPath = path.join(scriptDir, "inspect-motion-target.mjs");

  const root = path.resolve(args.root);
  const targetArg = args.target;
  const task = args.task.trim();

  const audit = runJson(auditPath, ["--root", root, "--limit", "20"]);
  const inspect = runJson(inspectPath, [targetArg, "--root", root]);

  const taskIntents = inferTaskIntents(task);
  const packageStrategy = choosePackageStrategy(audit, taskIntents);
  const recommendedPattern = choosePattern(taskIntents, inspect, audit);
  const recommendedBoundary = chooseBoundary(recommendedPattern, inspect, audit, packageStrategy);
  const recommendedImportPath = chooseImportPath(packageStrategy, recommendedBoundary);
  const reducedMotionPlan = chooseReducedMotionPlan(recommendedPattern);
  const performancePlan = choosePerformancePlan(recommendedPattern, recommendedBoundary);
  const firstSteps = chooseFirstSteps(recommendedPattern, inspect, audit, recommendedImportPath);
  const validation = chooseValidation(recommendedPattern, recommendedBoundary);
  const warnings = [...(audit.warnings || []), ...(inspect.warnings || [])];

  const result = {
    root,
    task,
    taskIntents,
    repo: {
      router: audit.router,
      packageManager: audit.packageManager,
      dependencies: audit.dependencies,
      libraryRecommendation: audit.libraryRecommendation,
      boundaries: audit.boundaries,
      candidateFiles: audit.candidateFiles,
    },
    target: inspect,
    decision: {
      packageStrategy,
      recommendedImportPath,
      recommendedBoundary,
      recommendedPattern,
      reducedMotionPlan,
      performancePlan,
      likelyFilesToChange: likelyFilesToChange(recommendedPattern, inspect, audit),
      firstSteps,
      validation,
    },
    warnings,
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
