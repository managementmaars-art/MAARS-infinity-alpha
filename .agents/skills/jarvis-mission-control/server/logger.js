/**
 * JARVIS Mission Control — Structured Logger (v1.8.0)
 *
 * Uses pino for structured JSON logging in production,
 * and pino-pretty for human-readable output in development.
 *
 * Usage:
 *   const logger = require('./logger');
 *   logger.info({ event: 'request', method: 'GET', path: '/api/tasks' }, 'Request received');
 *   logger.error({ err }, 'Something went wrong');
 */

const pino = require('pino');

const isDev = process.env.NODE_ENV !== 'production';

const transport = isDev
    ? {
          transport: {
              target: 'pino-pretty',
              options: {
                  colorize: true,
                  translateTime: 'SYS:HH:MM:ss',
                  ignore: 'pid,hostname',
                  messageFormat: '{msg}',
              },
          },
      }
    : {};

const logger = pino(
    {
        level: process.env.LOG_LEVEL || 'info',
        base: { service: 'mission-control' },
        timestamp: pino.stdTimeFunctions.isoTime,
        ...transport,
    }
);

module.exports = logger;
