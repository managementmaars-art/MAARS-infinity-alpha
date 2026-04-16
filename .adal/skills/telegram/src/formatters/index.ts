export * from './json.js';
export * from './plain.js';
export * from './markdown.js';

export type OutputFormat = 'plain' | 'json' | 'markdown';

export function getOutputFormat(options: { json?: boolean; markdown?: boolean; plain?: boolean }): OutputFormat {
  if (options.json) return 'json';
  if (options.markdown) return 'markdown';
  return 'plain';
}
