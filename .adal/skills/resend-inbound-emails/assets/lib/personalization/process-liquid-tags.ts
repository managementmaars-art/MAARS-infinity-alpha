/**
 * Liquid Tag Processing Utilities
 * 
 * Detects and extracts {{ tag }} patterns from email content.
 * Used to determine if AI personalization is needed.
 */

// Regex to match {{ tag_name }} patterns
const LIQUID_TAG_REGEX = /\{\{\s*([^}]+?)\s*\}\}/g;

/**
 * Check if text contains any {{ }} tags
 */
export function hasLiquidTags(text: string): boolean {
  LIQUID_TAG_REGEX.lastIndex = 0; // Reset regex state
  return LIQUID_TAG_REGEX.test(text);
}

/**
 * Extract all tag names from text
 * @example extractTags("Hi {{ name }}, {{ compliment }}") → ["name", "compliment"]
 */
export function extractTags(text: string): string[] {
  const matches = text.matchAll(LIQUID_TAG_REGEX);
  return [...matches].map((m) =>
    m[1].trim().toLowerCase().replace(/[-_]/g, "")
  );
}

/**
 * Check if subject or body contains personalization tags
 */
export function containsPersonalization(subject: string, body: string): boolean {
  return hasLiquidTags(subject) || hasLiquidTags(body);
}

/**
 * Replace a specific tag with a value (simple replacement)
 * For AI replacement, use generatePersonalizedEmail instead.
 */
export function replaceTag(text: string, tagName: string, value: string): string {
  const pattern = new RegExp(`\\{\\{\\s*${tagName}\\s*\\}\\}`, "gi");
  return text.replace(pattern, value);
}

/**
 * Get all unique tags in a template
 */
export function getUniqueTags(subject: string, body: string): string[] {
  const subjectTags = extractTags(subject);
  const bodyTags = extractTags(body);
  return [...new Set([...subjectTags, ...bodyTags])];
}
