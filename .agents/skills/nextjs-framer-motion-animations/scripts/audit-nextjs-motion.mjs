#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const HELP = `Usage: node scripts/audit-nextjs-motion.mjs [--root PATH] [--limit N]

Inspect a Next.js repo for Motion / Framer Motion work. Prints JSON to stdout.

Options:
  --root PATH   Repository root to inspect. Defaults to current working directory.
  --limit N     Maximum number of candidate files to return. Defaults to 16.
  --help        Show this help text.

Examples:
  node scripts/audit-nextjs-motion.mjs --root ../my-app
  node scripts/audit-nextjs-motion.mjs --root /workspace/repo --limit 24
`;

const IGNORE_DIRS = new Set([
  '.git',
  '.next',
  '.turbo',
  'node_modules',
  'dist',
  'build',
  'coverage',
  'out',
  '.cache',
]);

const SOURCE_DIRS = [
  'app',
  'src/app',
  'pages',
  'src/pages',
  'components',
  'src/components',
  'ui',
  'src/ui',
];

const SOURCE_EXTS = new Set(['.ts', '.tsx', '.js', '.jsx', '.mdx']);

const KEYWORDS = {
  hero: 4,
  card: 3,
  button: 3,
  modal: 5,
  dialog: 5,
  drawer: 5,
  accordion: 5,
  tabs: 4,
  tab: 4,
  list: 3,
  grid: 3,
  nav: 2,
  header: 2,
  sidebar: 3,
  menu: 4,
  toast: 4,
  dropdown: 4,
  page: 3,
  layout: 2,
};

const HOOK_IMPORTS = [
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

const MOTION_APIS = [
  'AnimatePresence',
  'LayoutGroup',
  'MotionConfig',
  'Reorder',
  'LazyMotion',
  'whileInView',
  'whileHover',
  'whileTap',
  'whileFocus',
  'layoutId',
  'layout',
  'useReducedMotion',
  'useAnimate',
  'useInView',
  'useScroll',
];

function parseArgs(argv) {
  const args = { root: process.cwd(), limit: 16, help: false };

  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (token === '--help' || token === '-h') {
      args.help = true;
    } else if (token === '--root') {
      args.root = argv[index + 1];
      index += 1;
    } else if (token === '--limit') {
      args.limit = Number.parseInt(argv[index + 1], 10);
      index += 1;
    } else {
      throw new Error(`Unknown argument: ${token}`);
    }
  }

  if (!Number.isFinite(args.limit) || args.limit <= 0) {
    throw new Error('--limit must be a positive integer.');
  }

  return args;
}

function readText(filePath) {
  try {
    return fs.readFileSync(filePath, 'utf8');
  } catch {
    return '';
  }
}

function readJson(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch {
    return null;
  }
}

function exists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch {
    return false;
  }
}

function isClientComponent(text) {
  return /^\s*["']use client["'];?/m.test(text);
}

function findFirstExisting(root, candidates) {
  for (const relative of candidates) {
    const absolute = path.join(root, relative);
    if (exists(absolute)) return relative;
  }
  return null;
}

function detectRouter(root) {
  const hasApp = exists(path.join(root, 'app')) || exists(path.join(root, 'src/app'));
  const hasPages = exists(path.join(root, 'pages')) || exists(path.join(root, 'src/pages'));
  if (hasApp && hasPages) return 'mixed';
  if (hasApp) return 'app-router';
  if (hasPages) return 'pages-router';
  return 'unknown';
}

function flattenDependencies(pkg) {
  const output = {};
  if (!pkg || typeof pkg !== 'object') return output;

  for (const section of ['dependencies', 'devDependencies', 'peerDependencies']) {
    const value = pkg[section];
    if (!value || typeof value !== 'object') continue;
    for (const [name, version] of Object.entries(value)) {
      if (typeof version === 'string') output[name] = version;
    }
  }

  return output;
}

function detectStylingHints(root, deps) {
  const hints = {
    tailwind: false,
    cssModules: false,
    styledComponents: Boolean(deps['styled-components']),
    emotion: Boolean(deps['@emotion/react'] || deps['@emotion/styled']),
  };

  if (['tailwind.config.js', 'tailwind.config.ts', 'tailwind.config.mjs'].some((name) => exists(path.join(root, name)))) {
    hints.tailwind = true;
  }

  function walk(current) {
    let entries = [];
    try {
      entries = fs.readdirSync(current, { withFileTypes: true });
    } catch {
      return;
    }

    for (const entry of entries) {
      const absolute = path.join(current, entry.name);
      if (entry.isDirectory()) {
        if (IGNORE_DIRS.has(entry.name)) continue;
        walk(absolute);
        continue;
      }
      if (entry.name.endsWith('.module.css') || entry.name.endsWith('.module.scss')) {
        hints.cssModules = true;
      }
      if (hints.cssModules && hints.tailwind) return;
    }
  }

  walk(root);
  return hints;
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

function analyseFile(root, absolutePath) {
  const text = readText(absolutePath);
  const relative = path.relative(root, absolutePath).replaceAll(path.sep, '/');
  const lowerRelative = relative.toLowerCase();

  const imports = {
    'motion/react': /from\s+["']motion\/react["']/.test(text),
    'motion/react-client': /from\s+["']motion\/react-client["']/.test(text),
    'motion/react-m': /from\s+["']motion\/react-m["']/.test(text),
    'framer-motion': /from\s+["']framer-motion["']/.test(text),
  };

  const signals = {
    clientComponent: isClientComponent(text),
    hasInteractionLogic: ['useState(', 'useReducer(', 'useEffect(', 'useLayoutEffect(', 'useRef(', 'onClick=', 'onPointerDown=', 'onMouseEnter=', 'onMouseLeave=', 'onKeyDown='].some((token) => text.includes(token)),
    importsNextImage: text.includes('from "next/image"') || text.includes("from 'next/image'"),
    importsNextDynamic: text.includes('from "next/dynamic"') || text.includes("from 'next/dynamic'"),
    hasListMap: text.includes('.map('),
    hasConditionalRender: text.includes(' ? ') || text.includes('&& <') || text.includes('&& ('),
    hasImageComponent: text.includes('<Image'),
    hasSerializationRisk: text.includes('onClick') && !isClientComponent(text),
  };

  const hookHits = HOOK_IMPORTS.filter((name) => text.includes(name));
  const motionHits = MOTION_APIS.filter((name) => text.includes(name));

  let score = 0;
  const reasons = [];

  if (/\/page\.(t|j)sx?$/.test(lowerRelative)) {
    score += 4;
    reasons.push('page component');
  }
  if (/\/layout\.(t|j)sx?$/.test(lowerRelative)) {
    score += 2;
    reasons.push('layout component');
  }
  if (lowerRelative.startsWith('components/') || lowerRelative.includes('/components/') || lowerRelative.startsWith('ui/') || lowerRelative.includes('/ui/')) {
    score += 1;
    reasons.push('component directory');
  }
  for (const [word, weight] of Object.entries(KEYWORDS)) {
    if (lowerRelative.includes(word)) {
      score += weight;
      reasons.push(`matches '${word}'`);
    }
  }
  if (signals.clientComponent) {
    score += 3;
    reasons.push('already client');
  }
  if (Object.values(imports).some(Boolean)) {
    score += 3;
    reasons.push('already uses Motion');
  }
  if (signals.hasInteractionLogic) {
    score += 2;
    reasons.push('interactive logic');
  }
  if (signals.hasListMap) {
    score += 1;
    reasons.push('maps list');
  }
  if (signals.hasConditionalRender) {
    score += 1;
    reasons.push('conditional UI');
  }
  if (signals.importsNextImage) {
    reasons.push('next/image present');
  }

  let recommendedStrategy = 'unknown';
  if (imports['motion/react-client']) {
    recommendedStrategy = 'keep server-friendly motion/react-client pattern';
  } else if (signals.clientComponent || signals.hasInteractionLogic || hookHits.length > 0) {
    recommendedStrategy = 'small client leaf using motion/react or existing framer-motion';
  } else {
    recommendedStrategy = 'candidate for passive motion/react-client or tiny client leaf';
  }

  return {
    path: relative,
    score,
    reasons: reasons.slice(0, 6),
    imports,
    signals,
    motionHits,
    hookHits,
    recommendedStrategy,
  };
}

function chooseLibrary(deps, importCounter) {
  if (deps['framer-motion'] || importCounter['framer-motion'] > 0) {
    return {
      choice: 'framer-motion',
      reason: 'Repository already uses framer-motion. Preserve the import path unless the user explicitly asks to migrate.',
    };
  }
  if (deps.motion || importCounter['motion/react'] > 0 || importCounter['motion/react-client'] > 0) {
    return {
      choice: 'motion/react',
      reason: 'Repository already uses Motion or depends on the motion package.',
    };
  }
  return {
    choice: 'motion/react',
    reason: 'No existing Motion dependency found. Prefer motion for a new install.',
  };
}

function detectPackageManager(root) {
  if (exists(path.join(root, 'pnpm-lock.yaml'))) return 'pnpm';
  if (exists(path.join(root, 'package-lock.json'))) return 'npm';
  if (exists(path.join(root, 'yarn.lock'))) return 'yarn';
  if (exists(path.join(root, 'bun.lock')) || exists(path.join(root, 'bun.lockb'))) return 'bun';
  return 'unknown';
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    process.stdout.write(`${HELP}
`);
    return;
  }

  const root = path.resolve(args.root);
  if (!exists(root)) {
    throw new Error(`Root does not exist: ${root}`);
  }

  const pkgPath = path.join(root, 'package.json');
  const pkg = readJson(pkgPath) || {};
  const deps = flattenDependencies(pkg);
  const router = detectRouter(root);
  const stylingHints = detectStylingHints(root, deps);
  const fileAnalyses = iterSourceFiles(root).map((filePath) => analyseFile(root, filePath));

  const importCounter = {
    'motion/react': 0,
    'motion/react-client': 0,
    'motion/react-m': 0,
    'framer-motion': 0,
  };
  const motionUsageSummary = {};
  const warnings = [];

  for (const item of fileAnalyses) {
    for (const [name, present] of Object.entries(item.imports)) {
      if (present) importCounter[name] += 1;
    }
    for (const hit of item.motionHits) {
      motionUsageSummary[hit] = (motionUsageSummary[hit] || 0) + 1;
    }
  }

  const libraryRecommendation = chooseLibrary(deps, importCounter);

  if (importCounter['framer-motion'] && (importCounter['motion/react'] || importCounter['motion/react-client'])) {
    warnings.push('Mixed framer-motion and motion imports detected. Preserve consistency in the edited scope or migrate intentionally.');
  }
  if (router === 'app-router') {
    for (const item of fileAnalyses) {
      if (item.path.endsWith('app/layout.tsx') || item.path.endsWith('src/app/layout.tsx')) {
        if (item.signals.clientComponent) {
          warnings.push('Root App Router layout is a client component. Be careful not to widen the client boundary further.');
        }
      }
    }
  }
  if ((importCounter['motion/react'] || importCounter['framer-motion']) && !motionUsageSummary.useReducedMotion && !motionUsageSummary.MotionConfig) {
    warnings.push('Motion is present but reduced-motion handling was not detected. Consider whether the edited UI should add it.');
  }
  if (libraryRecommendation.choice === 'motion/react' && importCounter['motion/react-client'] === 0 && router === 'app-router') {
    warnings.push('App Router project detected. Consider motion/react-client for passive cases if the repo already uses the motion package.');
  }

  const candidateFiles = fileAnalyses
    .filter((item) => item.score > 0)
    .sort((a, b) => (b.score - a.score) || a.path.localeCompare(b.path))
    .slice(0, args.limit);

  const result = {
    root,
    router,
    packageJsonFound: exists(pkgPath),
    packageManager: detectPackageManager(root),
    dependencies: Object.fromEntries(
      Object.entries(deps).filter(([name]) => ['next', 'react', 'react-dom', 'motion', 'framer-motion', 'tailwindcss', 'styled-components', '@emotion/react', '@emotion/styled'].includes(name))
    ),
    stylingHints,
    libraryRecommendation,
    boundaries: {
      appLayout: findFirstExisting(root, ['app/layout.tsx', 'app/layout.jsx', 'app/layout.js', 'app/layout.mjs', 'src/app/layout.tsx', 'src/app/layout.jsx', 'src/app/layout.js', 'src/app/layout.mjs']),
      appTemplate: findFirstExisting(root, ['app/template.tsx', 'app/template.jsx', 'app/template.js', 'app/template.mjs', 'src/app/template.tsx', 'src/app/template.jsx', 'src/app/template.js', 'src/app/template.mjs']),
      pagesApp: findFirstExisting(root, ['pages/_app.tsx', 'pages/_app.jsx', 'pages/_app.js', 'pages/_app.mjs', 'src/pages/_app.tsx', 'src/pages/_app.jsx', 'src/pages/_app.js', 'src/pages/_app.mjs']),
    },
    importStyleSummary: importCounter,
    motionUsageSummary: Object.fromEntries(Object.entries(motionUsageSummary).sort(([a], [b]) => a.localeCompare(b))),
    candidateFiles,
    warnings,
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
