/**
 * RFC 5322 Email Header Utilities
 * 
 * Handles parsing and building of email threading headers:
 * - Message-ID: Unique identifier for each message
 * - In-Reply-To: Message-ID of the message being replied to
 * - References: Chain of all Message-IDs in the thread
 */

type HeaderEntry = {
  name?: unknown;
  key?: unknown;
  value?: unknown;
};

function coerceHeaderValue(value: unknown): string | null {
  if (typeof value === "string") return value;
  if (Array.isArray(value)) {
    const parts = value.filter((item) => typeof item === "string");
    return parts.length > 0 ? parts.join(", ") : null;
  }
  if (value && typeof value === "object" && "value" in value) {
    const nestedValue = (value as { value?: unknown }).value;
    return typeof nestedValue === "string" ? nestedValue : null;
  }
  return null;
}

/**
 * Extract a header value from various header formats
 * (Resend can return headers as array or object)
 */
export function getHeaderValue(headers: unknown, targetName: string): string | null {
  const normalizedTarget = targetName.toLowerCase();
  if (!headers) return null;

  if (Array.isArray(headers)) {
    for (const entry of headers) {
      if (!entry || typeof entry !== "object") continue;
      const header = entry as HeaderEntry;
      const name = typeof header.name === "string" ? header.name : header.key;
      if (typeof name === "string" && name.toLowerCase() === normalizedTarget) {
        return coerceHeaderValue(header.value);
      }
    }
  }

  if (typeof headers === "object") {
    for (const [key, value] of Object.entries(headers as Record<string, unknown>)) {
      if (key.toLowerCase() === normalizedTarget) {
        return coerceHeaderValue(value);
      }
    }
  }

  return null;
}

/**
 * Normalize a Message-ID by stripping angle brackets
 * "<abc123@domain.com>" → "abc123@domain.com"
 */
export function normalizeMessageId(value: string | null): string | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  const match = trimmed.match(/<([^>]+)>/);
  if (match?.[1]) return match[1].trim();
  return trimmed.replace(/^<|>$/g, "").trim();
}

/**
 * Parse a Message-ID header (returns first ID found)
 */
export function parseMessageIdHeader(value: string | null): string | null {
  if (!value) return null;
  const tokens = value.match(/<[^>]+>|[^\s]+/g) ?? [];
  const first = tokens[0] ? normalizeMessageId(tokens[0]) : null;
  return first || null;
}

/**
 * Parse a References header (returns all IDs)
 */
export function parseReferencesHeader(value: string | null): string[] {
  if (!value) return [];
  const tokens = value.match(/<[^>]+>|[^\s]+/g) ?? [];
  return tokens
    .map((token) => normalizeMessageId(token))
    .filter((token): token is string => Boolean(token));
}

/**
 * Merge existing references with a new message ID (deduped)
 */
export function mergeReferences(existing: string[], messageId: string | null): string[] {
  const seen = new Set<string>();
  const merged: string[] = [];

  for (const entry of existing) {
    const normalized = normalizeMessageId(entry);
    if (normalized && !seen.has(normalized)) {
      seen.add(normalized);
      merged.push(normalized);
    }
  }

  const normalizedMessageId = normalizeMessageId(messageId);
  if (normalizedMessageId && !seen.has(normalizedMessageId)) {
    seen.add(normalizedMessageId);
    merged.push(normalizedMessageId);
  }

  return merged;
}

/**
 * Format a Message-ID for use in headers (adds angle brackets)
 * "abc123@domain.com" → "<abc123@domain.com>"
 */
export function formatMessageIdHeader(value: string | null): string | null {
  const normalized = normalizeMessageId(value);
  return normalized ? `<${normalized}>` : null;
}

/**
 * Build a References header from an array of message IDs
 */
export function buildReferencesHeader(references: string[]): string | null {
  const normalized = references
    .map((entry) => normalizeMessageId(entry))
    .filter((entry): entry is string => Boolean(entry));
  if (normalized.length === 0) return null;
  return normalized.map((entry) => `<${entry}>`).join(" ");
}
