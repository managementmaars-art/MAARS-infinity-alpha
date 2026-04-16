/**
 * SafeMarkdown Component
 *
 * Renders markdown content securely by:
 * 1. Parsing with marked
 * 2. Syntax highlighting with highlight.js
 * 3. Rewriting image URLs through our proxy
 * 4. Sanitizing HTML with DOMPurify
 */

import { useMemo, useEffect } from 'react'
import { marked, Renderer } from 'marked'
import DOMPurify from 'dompurify'
// Import highlight.js core with only common languages to reduce bundle size
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import json from 'highlight.js/lib/languages/json'
import bash from 'highlight.js/lib/languages/bash'
import css from 'highlight.js/lib/languages/css'
import xml from 'highlight.js/lib/languages/xml' // Includes HTML
import sql from 'highlight.js/lib/languages/sql'
import go from 'highlight.js/lib/languages/go'
import rust from 'highlight.js/lib/languages/rust'
import markdown from 'highlight.js/lib/languages/markdown'

// Register languages
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('js', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('ts', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('py', python)
hljs.registerLanguage('json', json)
hljs.registerLanguage('bash', bash)
hljs.registerLanguage('sh', bash)
hljs.registerLanguage('shell', bash)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('sql', sql)
hljs.registerLanguage('go', go)
hljs.registerLanguage('rust', rust)
hljs.registerLanguage('rs', rust)
hljs.registerLanguage('markdown', markdown)
hljs.registerLanguage('md', markdown)

// Import a dark theme for syntax highlighting
import 'highlight.js/styles/github-dark.css'

// API base URL for the image proxy
const API_BASE =
  typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? 'http://localhost:8787'
    : 'https://api.abund.ai'

interface SafeMarkdownProps {
  content: string
  className?: string
}

/**
 * Highlight code with highlight.js
 */
function highlightCode(code: string, lang: string | undefined): string {
  if (lang && hljs.getLanguage(lang)) {
    try {
      return hljs.highlight(code, { language: lang }).value
    } catch {
      // Fall through to auto-detection
    }
  }
  // Try auto-detection
  try {
    return hljs.highlightAuto(code).value
  } catch {
    // Fall back to plain escaped code
    return escapeHtml(code)
  }
}

/**
 * Creates a custom marked renderer that proxies all images
 */
function createSecureRenderer(): Renderer {
  const renderer = new Renderer()

  // Override image rendering to proxy through our worker
  renderer.image = ({ href, title, text }) => {
    // Rewrite URL through our proxy
    const proxyUrl = `${API_BASE}/api/v1/proxy/image?url=${encodeURIComponent(href)}`

    const titleAttr = title ? ` title="${escapeHtml(title)}"` : ''
    const altAttr = text ? ` alt="${escapeHtml(text)}"` : ''

    return `<img src="${proxyUrl}"${altAttr}${titleAttr} loading="lazy" class="rounded-lg max-w-full h-auto" />`
  }

  // Override link rendering to add security attributes
  renderer.link = ({ href, title, text }) => {
    const titleAttr = title ? ` title="${escapeHtml(title)}"` : ''
    // External links open in new tab with security attributes
    return `<a href="${escapeHtml(href)}"${titleAttr} target="_blank" rel="noopener noreferrer nofollow" class="text-primary-500 hover:underline">${text}</a>`
  }

  // Override code block rendering with syntax highlighting
  renderer.code = ({ text, lang }) => {
    const highlighted = highlightCode(text, lang)
    const langLabel = lang
      ? `<div class="absolute top-2 right-2 text-xs text-[var(--text-muted)] font-mono opacity-60">${escapeHtml(lang)}</div>`
      : ''
    return `<div class="relative"><pre class="bg-[var(--bg-void)] rounded-lg p-4 overflow-x-auto text-sm font-mono"><code class="hljs">${highlighted}</code></pre>${langLabel}</div>`
  }

  // Override inline code
  renderer.codespan = ({ text }) => {
    return `<code class="bg-[var(--bg-hover)] px-1.5 py-0.5 rounded text-sm font-mono text-[var(--text-primary)]">${escapeHtml(text)}</code>`
  }

  return renderer
}

/**
 * Escape HTML entities
 */
function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;')
}

/**
 * Configure DOMPurify with strict settings
 */
function sanitizeHtml(html: string): string {
  return DOMPurify.sanitize(html, {
    // Allowed tags (no scripts, iframes, objects, etc.)
    ALLOWED_TAGS: [
      'p',
      'br',
      'strong',
      'b',
      'em',
      'i',
      'u',
      's',
      'strike',
      'h1',
      'h2',
      'h3',
      'h4',
      'h5',
      'h6',
      'ul',
      'ol',
      'li',
      'blockquote',
      'pre',
      'code',
      'a',
      'img',
      'table',
      'thead',
      'tbody',
      'tr',
      'th',
      'td',
      'hr',
      'span',
      'div',
    ],
    // Allowed attributes
    ALLOWED_ATTR: [
      'href',
      'src',
      'alt',
      'title',
      'class',
      'target',
      'rel',
      'loading',
    ],
    // Force links to have security attributes
    ADD_ATTR: ['target', 'rel'],
    // Don't allow data: URLs for images (could contain XSS)
    ALLOW_DATA_ATTR: false,
    // Force all URLs to be safe
    ALLOWED_URI_REGEXP:
      /^(?:(?:https?|mailto):|[^a-z]|[a-z+.-]+(?:[^a-z+.\-:]|$))/i,
  })
}

/**
 * Parse markdown and return safe HTML
 */
function parseMarkdown(content: string): string {
  // Preprocess: Convert literal escape sequences to actual characters
  // This handles cases where JSON data contains escaped characters
  let preprocessed = content

  // Handle escaped newlines (literal \n becomes actual newline)
  preprocessed = preprocessed.replace(/\\n/g, '\n')
  // Handle escaped tabs (literal \t becomes actual tab)
  preprocessed = preprocessed.replace(/\\t/g, '\t')
  // Handle escaped quotes
  preprocessed = preprocessed.replace(/\\"/g, '"')
  preprocessed = preprocessed.replace(/\\'/g, "'")

  // Configure marked with our secure renderer
  marked.setOptions({
    gfm: true, // GitHub Flavored Markdown
    breaks: true, // Line breaks as <br>
  })

  // Parse markdown
  const rawHtml = marked.parse(preprocessed, {
    renderer: createSecureRenderer(),
    async: false,
  })

  // Sanitize the output
  return sanitizeHtml(rawHtml)
}

export function SafeMarkdown({ content, className = '' }: SafeMarkdownProps) {
  // Memoize the parsed content to avoid re-parsing on every render
  const safeHtml = useMemo(() => parseMarkdown(content), [content])

  // Ensure highlight.js styles are available
  useEffect(() => {
    // highlight.js CSS is imported at module level
  }, [])

  return (
    <div
      className={`prose prose-invert max-w-none ${className}`}
      dangerouslySetInnerHTML={{ __html: safeHtml }}
    />
  )
}

/**
 * Inline version for single-line content (no block elements)
 */
export function SafeMarkdownInline({
  content,
  className = '',
}: SafeMarkdownProps) {
  const preprocessed = content.replace(/\\n/g, '\n')

  const safeHtml = useMemo(() => {
    const rawHtml = marked.parseInline(preprocessed, {
      renderer: createSecureRenderer(),
    }) as string
    return sanitizeHtml(rawHtml)
  }, [preprocessed])

  return (
    <span
      className={className}
      dangerouslySetInnerHTML={{ __html: safeHtml }}
    />
  )
}
