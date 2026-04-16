/**
 * SSRF Protection Utilities
 *
 * Validates URLs before server-side fetching to prevent
 * Server-Side Request Forgery (SSRF) attacks.
 *
 * Blocks:
 * - Private IPv4 ranges (10.x, 172.16-31.x, 192.168.x, 127.x)
 * - Private IPv6 (::1, ::ffff:127.x, fe80::, fc00::, fd00::)
 * - Link-local addresses (169.254.x.x)
 * - Cloud metadata endpoints (169.254.169.254, metadata.google.internal)
 * - Non-HTTP(S) schemes (file://, ftp://, etc.)
 */

/**
 * Validate that a URL is safe to fetch server-side.
 * Returns null if safe, or an error message if blocked.
 */
export function validateExternalUrl(
  urlString: string,
  environment?: string
): string | null {
  let url: URL
  try {
    url = new URL(urlString)
  } catch {
    return 'Invalid URL format'
  }

  // Only allow HTTP and HTTPS schemes
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    return `Blocked scheme: ${url.protocol} — only http: and https: are allowed`
  }

  const hostname = url.hostname.toLowerCase()

  // Block localhost variants (except in development mode)
  if (
    environment !== 'development' &&
    (hostname === 'localhost' ||
      hostname === 'localhost.' ||
      hostname === '127.0.0.1' ||
      hostname === '[::1]' ||
      hostname === '::1' ||
      hostname === '0.0.0.0')
  ) {
    return 'Blocked: localhost addresses are not allowed'
  }

  // Block cloud metadata endpoints
  if (
    hostname === '169.254.169.254' ||
    hostname === 'metadata.google.internal' ||
    hostname === 'metadata.google.com' ||
    hostname === 'instance-data' // AWS
  ) {
    return 'Blocked: cloud metadata endpoints are not allowed'
  }

  // Block IPv4 private/reserved ranges
  const ipv4Match = hostname.match(
    /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/
  )
  if (ipv4Match) {
    const [, a, b] = ipv4Match
    const octet1 = parseInt(a!, 10)
    const octet2 = parseInt(b!, 10)

    // 10.0.0.0/8 — Private
    if (octet1 === 10) {
      return 'Blocked: private IP range (10.x.x.x)'
    }

    // 172.16.0.0/12 — Private
    if (octet1 === 172 && octet2 >= 16 && octet2 <= 31) {
      return 'Blocked: private IP range (172.16-31.x.x)'
    }

    // 192.168.0.0/16 — Private
    if (octet1 === 192 && octet2 === 168) {
      return 'Blocked: private IP range (192.168.x.x)'
    }

    // 127.0.0.0/8 — Loopback
    if (octet1 === 127) {
      return 'Blocked: loopback address'
    }

    // 169.254.0.0/16 — Link-local
    if (octet1 === 169 && octet2 === 254) {
      return 'Blocked: link-local address'
    }

    // 0.0.0.0/8 — "This" network
    if (octet1 === 0) {
      return 'Blocked: reserved address'
    }
  }

  // Block IPv6 private/reserved (bracket-wrapped in URLs)
  const ipv6Hostname = hostname.replace(/^\[|\]$/g, '')
  if (isPrivateIPv6(ipv6Hostname)) {
    return 'Blocked: private/reserved IPv6 address'
  }

  return null // URL is safe
}

/**
 * Check if an IPv6 address is private or reserved.
 */
function isPrivateIPv6(addr: string): boolean {
  const lower = addr.toLowerCase()

  // Loopback
  if (lower === '::1' || lower === '0:0:0:0:0:0:0:1') {
    return true
  }

  // IPv4-mapped IPv6 addresses (::ffff:x.x.x.x)
  const v4MappedMatch = lower.match(
    /^::ffff:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$/
  )
  if (v4MappedMatch) {
    // Recursively check the embedded IPv4
    const result = validateExternalUrl(`http://${v4MappedMatch[1]}`)
    return result !== null
  }

  // Unique Local Addresses (fc00::/7 — fd00::/8 is the commonly used subset)
  if (lower.startsWith('fc') || lower.startsWith('fd')) {
    return true
  }

  // Link-local (fe80::/10)
  if (lower.startsWith('fe80')) {
    return true
  }

  // Unspecified address
  if (lower === '::' || lower === '0:0:0:0:0:0:0:0') {
    return true
  }

  return false
}

/**
 * Assert that a URL is safe to fetch. Throws an Error if blocked.
 */
export function assertSafeUrl(urlString: string, environment?: string): void {
  const error = validateExternalUrl(urlString, environment)
  if (error) {
    throw new Error(`SSRF protection: ${error}`)
  }
}
