/**
 * RootSpec Cypress Reporter Plugin
 *
 * Automatically writes rootspec/tests-status.json after each Cypress run.
 * Extracts story IDs from suite titles (US-nnn) and criterion IDs from
 * test titles (AC-nnn-nnn), computes pass/fail, and merges with existing
 * status file.
 *
 * Usage in cypress.config.ts:
 *
 *   import { rootspecReporter } from './cypress/support/rootspec-reporter';
 *
 *   export default defineConfig({
 *     e2e: {
 *       setupNodeEvents(on) {
 *         rootspecReporter(on, { statusPath: 'rootspec/tests-status.json' });
 *       }
 *     }
 *   });
 */

import * as fs from 'fs';
import * as path from 'path';

interface ReporterOptions {
  statusPath?: string;
}

interface CriterionResult {
  status: 'pass' | 'fail';
}

interface StoryResult {
  status: 'pass' | 'fail';
  criteria: Record<string, string>;
}

interface TestsStatus {
  lastRun: string;
  stories: Record<string, StoryResult>;
}

const STORY_PATTERN = /US-\d+/;
const CRITERION_PATTERN = /AC-\d+-\d+/;

function extractResults(runs: CypressCommandLine.RunResult['runs']): Record<string, StoryResult> {
  const stories: Record<string, Record<string, CriterionResult>> = {};

  for (const run of runs) {
    for (const suite of flattenSuites(run.tests, run.spec)) {
      const storyMatch = suite.title.match(STORY_PATTERN);
      if (!storyMatch) continue;
      const storyId = storyMatch[0];

      if (!stories[storyId]) {
        stories[storyId] = {};
      }

      for (const test of suite.tests) {
        const critMatch = test.title.join(' ').match(CRITERION_PATTERN);
        if (!critMatch) continue;
        const critId = critMatch[0];
        const passed = test.state === 'passed';
        stories[storyId][critId] = { status: passed ? 'pass' : 'fail' };
      }
    }
  }

  // Convert to StoryResult format
  const result: Record<string, StoryResult> = {};
  for (const [storyId, criteria] of Object.entries(stories)) {
    const allPass = Object.values(criteria).every((c) => c.status === 'pass');
    const criteriaFlat: Record<string, string> = {};
    for (const [critId, crit] of Object.entries(criteria)) {
      criteriaFlat[critId] = crit.status;
    }
    result[storyId] = {
      status: allPass ? 'pass' : 'fail',
      criteria: criteriaFlat
    };
  }

  return result;
}

/**
 * Cypress run results structure varies between versions.
 * We need to walk through the nested suites to find tests.
 */
interface SuiteInfo {
  title: string;
  tests: Array<{ title: string[]; state: string }>;
}

function flattenSuites(
  tests: CypressCommandLine.TestResult[] | undefined,
  spec: CypressCommandLine.SpecResult | undefined
): SuiteInfo[] {
  // In Cypress 13+, run results have a nested structure.
  // We extract from the raw results object by walking suites.
  const suites: SuiteInfo[] = [];

  // Approach: use tests array grouped by their title hierarchy
  if (!tests || tests.length === 0) return suites;

  // Group tests by the title element containing the story ID (US-nnn).
  // Tests may be nested under a wrapper describe, so title[0] might not
  // contain the story ID — scan all title elements to find it.
  const storyPattern = /US-\d+/;
  const grouped: Record<string, Array<{ title: string[]; state: string }>> = {};
  for (const test of tests) {
    const storyTitle = test.title.find(t => storyPattern.test(t))
      || (test.title.length > 1 ? test.title[0] : spec?.name || 'unknown');
    if (!grouped[storyTitle]) {
      grouped[storyTitle] = [];
    }
    grouped[storyTitle].push(test);
  }

  for (const [title, groupTests] of Object.entries(grouped)) {
    suites.push({ title, tests: groupTests });
  }

  return suites;
}

function mergeStatus(
  existing: TestsStatus | null,
  newStories: Record<string, StoryResult>,
  timestamp: string
): TestsStatus {
  const merged: TestsStatus = {
    lastRun: timestamp,
    stories: {}
  };

  // Preserve existing stories not in this run
  if (existing?.stories) {
    for (const [storyId, story] of Object.entries(existing.stories)) {
      if (!(storyId in newStories)) {
        merged.stories[storyId] = story;
      }
    }
  }

  // Add new results (overwrite if existed)
  for (const [storyId, story] of Object.entries(newStories)) {
    merged.stories[storyId] = story;
  }

  return merged;
}

function readExisting(statusPath: string): TestsStatus | null {
  try {
    const content = fs.readFileSync(statusPath, 'utf-8');
    return JSON.parse(content);
  } catch {
    return null;
  }
}

export function rootspecReporter(
  on: Cypress.PluginEvents,
  options: ReporterOptions = {}
) {
  const statusPath = options.statusPath || 'rootspec/tests-status.json';

  on('after:run', (results) => {
    if (!results) return;
    const runResults = results as CypressCommandLine.CypressRunResult;
    if (!runResults.runs || runResults.runs.length === 0) return;

    const newStories = extractResults(runResults.runs);
    if (Object.keys(newStories).length === 0) return;

    const absPath = path.resolve(statusPath);
    const existing = readExisting(absPath);
    const timestamp = new Date().toISOString();
    const merged = mergeStatus(existing, newStories, timestamp);

    // Ensure directory exists
    fs.mkdirSync(path.dirname(absPath), { recursive: true });
    fs.writeFileSync(absPath, JSON.stringify(merged, null, 2) + '\n');

    const total = Object.keys(merged.stories).length;
    const passing = Object.values(merged.stories).filter((s) => s.status === 'pass').length;
    console.log(`\n[rootspec] Updated ${statusPath} — ${passing}/${total} stories passing\n`);
  });
}
