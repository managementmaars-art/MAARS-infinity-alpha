#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const HELP = `Usage: node scripts/inspect-motion-target.mjs FILE [--root PATH]

Inspect one target file and emit Motion / Next.js editing guidance as JSON.

Arguments:
  FILE            Target file to inspect.

Options:
  --root PATH     Repository root used for relative path output. Defaults to current working directory.
  --help          Show this help text.

Examples:
  node scripts/inspect-motion-target.mjs app/page.tsx --root ../my-app
  node scripts/inspect-motion-target.mjs src/components/hero.tsx
`;

function parseArgs(argv) {
  const args = { file: "", root: process.cwd(), help: false };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];

    if (token === "--help" || token === "-h") {
      args.help = true;
    } else if (token === "--root") {
      args.root = argv[index + 1];
      index += 1;
    } else if (!args.file) {
      args.file = token;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  if (!args.help && !args.file) {
    throw new Error("A target file is required.");
  }

  return args;
}

function readText(filePath) {
  try {
    return fs.readFileSync(filePath, "utf8");
  } catch {
    return "";
  }
}

function isClientComponent(text) {
  return /^\s*["']use client["'];?/m.test(text);
}

function detectRouterContext(relativePath) {
  const value = relativePath.replaceAll('\\', '/').toLowerCase();
  if (value.startsWith('app/') || value.includes('/app/') || value.startsWith('src/app/')) {
    return 'app-router';
  }
  if (value.startsWith('pages/') || value.includes('/pages/') || value.startsWith('src/pages/')) {
    return 'pages-router';
  }
  return 'shared';
}

function relativeOrAbsolute(root, target) {
  const relative = path.relative(root, target).replaceAll(path.sep, '/');
  return relative.startsWith('..') ? target : relative;
}

function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.help) {
    process.stdout.write(`${HELP}
`);
    return;
  }

  const root = path.resolve(args.root);
  const target = path.resolve(root, args.file);

  if (!fs.existsSync(target)) {
    throw new Error(`File not found: ${target}`);
  }

  const text = readText(target);
  if (!text) {
    throw new Error(`Could not read file: ${target}`);
  }

  const relPath = relativeOrAbsolute(root, target);
  const routerContext = detectRouterContext(relPath);
  const clientComponent = isClientComponent(text);

  const imports = {
    'motion/react': /from\s+["']motion\/react["']/.test(text),
    'motion/react-client': /from\s+["']motion\/react-client["']/.test(text),
    'motion/react-m': /from\s+["']motion\/react-m["']/.test(text),
    'framer-motion': /from\s+["']framer-motion["']/.test(text),
  };

  const hooks = [
    'useReducedMotion',
    'useAnimate',
    'useInView',
    'useScroll',
    'useMotionValue',
    'useTransform',
    'useSpring',
    'useVelocity',
    'usePathname',
    'useSelectedLayoutSegment',
    'useSelectedLayoutSegments',
  ];

  const hookHits = hooks.filter((name) => text.includes(name));

  const interactionSignals = [
    'useState(',
    'useReducer(',
    'useEffect(',
    'useLayoutEffect(',
    'useRef(',
    'onClick=',
    'onPointerDown=',
    'onMouseEnter=',
    'onKeyDown=',
  ];

  const interaction = interactionSignals.some((token) => text.includes(token));

  const patternHints = {
    presence: ['AnimatePresence', 'exit=', 'modal', 'dialog', 'drawer', 'dropdown', 'toast'].some((token) => text.includes(token)),
    stagger: ['variants', 'staggerChildren', 'delayChildren', '.map('].some((token) => text.includes(token)),
    'scroll-reveal': ['whileInView', 'useInView', 'viewport={{'].some((token) => text.includes(token)),
    'scroll-linked': ['useScroll', 'scrollYProgress', 'scrollXProgress'].some((token) => text.includes(token)),
    layout: ['layout', 'layoutId', 'LayoutGroup', 'accordion', 'tabs'].some((token) => text.includes(token)),
    reorder: ['Reorder.', 'onReorder', 'useDragControls'].some((token) => text.includes(token)),
    microinteraction: ['whileHover', 'whileTap', 'whileFocus', '<button', '<a ', 'next/link'].some((token) => text.includes(token)),
  };

  const warnings = [];
  const recommendations = [];

  if (routerContext === 'app-router' && !clientComponent && imports['framer-motion']) {
    warnings.push('App Router server-friendly file imports framer-motion directly. Prefer a tiny client leaf unless the file is already client-side.');
  }
  if (text.includes('<Image') && (!text.includes(' width=') && !text.includes(' fill'))) {
    warnings.push('next/image usage detected. Check that layout space is still preserved when animating.');
  }
  if (text.includes('AnimatePresence') && !text.includes('key=')) {
    warnings.push('AnimatePresence detected but no obvious key was found. Verify direct-child stable keys manually.');
  }
  if (text.includes('layoutId') && !text.includes('LayoutGroup')) {
    recommendations.push('If this shared element appears in repeated widgets, consider LayoutGroup id to isolate layoutId scope.');
  }

  if (interaction || hookHits.length > 0 || clientComponent) {
    recommendations.push('This file is already interactive or hook-driven. A small client-component Motion pattern is the most natural fit.');
  } else if (routerContext === 'app-router') {
    recommendations.push('This App Router file might be a candidate for motion/react-client if the requested effect is passive and hook-free.');
  } else {
    recommendations.push('This file can usually take direct motion/react or framer-motion usage without extra boundary work.');
  }

  if (patternHints.microinteraction) {
    recommendations.push('Microinteraction signals detected. Prefer whileHover plus whileTap plus whileFocus with restrained values.');
  }
  if (patternHints.stagger) {
    recommendations.push('List or variant signals detected. Prefer parent-controlled stagger rather than bespoke timing on every child.');
  }
  if (patternHints.presence) {
    recommendations.push('Presence signals detected. Use AnimatePresence with direct children and stable keys.');
  }
  if (patternHints.layout) {
    recommendations.push('Layout signals detected. Start with layout before manual size choreography.');
  }
  if (patternHints['scroll-linked']) {
    recommendations.push('Scroll-linked signals detected. Keep useScroll only if the motion genuinely needs to track scroll continuously.');
  }

  let recommendedBoundary = 'local-motion-edit';
  if (clientComponent) {
    recommendedBoundary = 'already-client';
  } else if (
    routerContext === 'app-router' &&
    hookHits.length === 0 &&
    !interaction &&
    !patternHints.presence &&
    !patternHints.reorder &&
    !patternHints['scroll-linked']
  ) {
    recommendedBoundary = 'server-friendly-motion-react-client-candidate';
  } else if (routerContext === 'app-router') {
    recommendedBoundary = 'small-client-leaf';
  }

  let preferredImportPath = 'inherit-from-repo';
  if (imports['framer-motion']) {
    preferredImportPath = 'framer-motion';
  } else if (imports['motion/react'] || imports['motion/react-client'] || imports['motion/react-m']) {
    preferredImportPath = 'motion/react';
  }

  const result = {
    path: relPath,
    routerContext,
    clientComponent,
    imports,
    hookHits,
    interactionSignalsPresent: interaction,
    patternHints,
    recommendedBoundary,
    preferredImportPath,
    warnings,
    recommendations,
  };

  process.stdout.write(`${JSON.stringify(result, null, 2)}
`);
}

try {
  main();
} catch (error) {
  process.stderr.write(`Error: ${error instanceof Error ? error.message : String(error)}
`);
  process.stderr.write(`${HELP}
`);
  process.exit(1);
}
