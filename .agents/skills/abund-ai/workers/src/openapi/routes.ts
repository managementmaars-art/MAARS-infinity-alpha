/**
 * OpenAPI Routes
 *
 * Serves the OpenAPI specification and optional Swagger UI.
 */

import { Hono } from 'hono'
import type { Env } from '../types'
import { generateOpenAPIDocument } from './registry'

const openapi = new Hono<{ Bindings: Env }>()

// Cache the generated document (it's static)
let cachedDocument: ReturnType<typeof generateOpenAPIDocument> | null = null

/**
 * GET /api/v1/openapi.json
 * Returns the full OpenAPI 3.1 specification
 */
openapi.get('/openapi.json', (c) => {
  if (!cachedDocument) {
    cachedDocument = generateOpenAPIDocument()
  }

  return c.json(cachedDocument)
})

/**
 * GET /api/v1/openapi.yaml
 * Returns the OpenAPI spec as YAML (for tools that prefer it)
 */
openapi.get('/openapi.yaml', (c) => {
  if (!cachedDocument) {
    cachedDocument = generateOpenAPIDocument()
  }

  // Simple JSON to YAML conversion for readability
  const yaml = jsonToYaml(cachedDocument)

  return c.text(yaml, 200, {
    'Content-Type': 'application/yaml',
  })
})

/**
 * GET /api/v1/docs
 * Serves a simple Swagger UI page
 */
openapi.get('/docs', (c) => {
  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Abund.ai API Documentation</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
  <style>
    body { margin: 0; padding: 0; }
    .swagger-ui .topbar { display: none; }
    .swagger-ui .info { margin: 20px 0; }
    .swagger-ui .info .title { color: #8b5cf6; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: '/api/v1/openapi.json',
      dom_id: '#swagger-ui',
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: 'BaseLayout',
      deepLinking: true,
      tryItOutEnabled: true,
    });
  </script>
</body>
</html>`

  return c.html(html)
})

/**
 * Simple JSON to YAML converter
 * Only handles basic structures - good enough for OpenAPI
 */
function jsonToYaml(obj: unknown, indent = 0): string {
  const spaces = '  '.repeat(indent)

  if (obj === null) return 'null'
  if (obj === undefined) return ''
  if (typeof obj === 'boolean') return obj.toString()
  if (typeof obj === 'number') return obj.toString()
  if (typeof obj === 'string') {
    // Check if string needs quoting
    if (
      obj.includes('\n') ||
      obj.includes(':') ||
      obj.includes('#') ||
      obj.includes("'") ||
      obj.startsWith(' ') ||
      obj.endsWith(' ')
    ) {
      // Use block scalar for multi-line
      if (obj.includes('\n')) {
        const lines = obj.split('\n')
        return `|\n${lines.map((l) => spaces + '  ' + l).join('\n')}`
      }
      // Quote strings with special chars
      return `"${obj.replace(/"/g, '\\"')}"`
    }
    return obj
  }

  if (Array.isArray(obj)) {
    if (obj.length === 0) return '[]'
    return obj
      .map((item) => `\n${spaces}- ${jsonToYaml(item, indent + 1).trimStart()}`)
      .join('')
  }

  if (typeof obj === 'object') {
    const entries = Object.entries(obj)
    if (entries.length === 0) return '{}'
    return entries
      .map(([key, value]) => {
        const valueYaml = jsonToYaml(value, indent + 1)
        if (
          typeof value === 'object' &&
          value !== null &&
          !Array.isArray(value)
        ) {
          return `\n${spaces}${key}:${valueYaml}`
        }
        if (Array.isArray(value)) {
          return `\n${spaces}${key}:${valueYaml}`
        }
        return `\n${spaces}${key}: ${valueYaml}`
      })
      .join('')
  }

  return String(obj)
}

export default openapi
