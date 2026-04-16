import { Hono } from 'hono'
import type { Env } from '../types'

const health = new Hono<{ Bindings: Env }>()

health.get('/', (c) => {
  return c.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    environment: c.env.ENVIRONMENT,
  })
})

export default health
