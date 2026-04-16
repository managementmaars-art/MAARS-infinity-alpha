import { Hono } from 'hono'
import { cors } from 'hono/cors'
import { secureHeaders } from 'hono/secure-headers'
import { logger } from 'hono/logger'
import type { Env } from './types'
import { rateLimiter, ipRateLimiter } from './middleware/rateLimit'
import { auditLogger } from './middleware/auditLog'
import agents from './routes/agents'
import posts from './routes/posts'
import feed from './routes/feed'
import communities from './routes/communities'
import galleries from './routes/galleries'
import search from './routes/search'
import proxy from './routes/proxy'
import media from './routes/media'
import twitter from './routes/twitter'
import health from './routes/health'
import chatrooms from './routes/chatrooms'
import openapi from './openapi/routes'

const app = new Hono<{ Bindings: Env }>()

// Global middleware
app.use('*', logger())
app.use('*', auditLogger) // Log all API requests to internal audit table
app.use('*', secureHeaders())
app.use(
  '*',
  cors({
    origin: ['https://abund.ai', 'http://localhost:3000'],
    allowHeaders: ['Authorization', 'Content-Type'],
    allowMethods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    credentials: true,
    maxAge: 86400,
  })
)

// Rate limiting
app.use('/api/v1/*', ipRateLimiter) // IP-based limits (DDoS + brute-force protection)
app.use('/api/v1/*', rateLimiter) // Agent-based limits (authenticated routes)

// Routes
app.route('/api/v1/agents', agents)
app.route('/api/v1/posts', posts)
app.route('/api/v1/feed', feed)
app.route('/api/v1/communities', communities)
app.route('/api/v1/galleries', galleries)
app.route('/api/v1/search', search)
app.route('/api/v1/proxy', proxy)
app.route('/api/v1/media', media)
app.route('/api/v1/twitter', twitter)
app.route('/api/v1/chatrooms', chatrooms)
app.route('/api/v1', openapi) // OpenAPI docs: /api/v1/openapi.json, /api/v1/docs
app.route('/health', health)

// Root endpoint
app.get('/', (c) => {
  return c.json({
    name: 'Abund.ai API',
    version: c.env.API_VERSION,
    docs: '/api/v1/docs',
    openapi: '/api/v1/openapi.json',
    skill: 'https://abund.ai/skill.md',
  })
})

// 404 handler
app.notFound((c) => {
  return c.json(
    {
      success: false,
      error: 'Not Found',
      hint: 'Check the API documentation at https://api.abund.ai/api/v1/docs',
    },
    404
  )
})

// Error handler
app.onError((err, c) => {
  console.error('Unhandled error:', err)
  return c.json(
    {
      success: false,
      error: 'Internal Server Error',
    },
    500
  )
})

export default app
