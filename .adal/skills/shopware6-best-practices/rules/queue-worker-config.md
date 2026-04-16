---
title: Message Queue Worker Configuration
impact: MEDIUM
impactDescription: Relying on Admin worker in production causes message backlogs, timeouts, and unreliable background processing.
tags: [shopware6, message-queue, worker, supervisor, production]
---

## Configure CLI Workers with Supervisor for Production

The Admin worker (browser-based) is only suitable for development. Production environments must use CLI workers managed by Supervisor or systemd for reliable message processing.

Reference: https://developer.shopware.com/docs/guides/hosting/infrastructure/message-queue

### Incorrect

```php
// Bad: Relying on Admin worker in production
// config/packages/shopware.yaml
shopware:
    admin_worker:
        enable_admin_worker: true  // Bad: Not suitable for production
        poll_interval: 30
        transports: ['async']

// Bad: No transport configuration, everything uses default sync
framework:
    messenger:
        transports:
            async: 'doctrine://default'  // Bad: No specific configuration

// Bad: No failure handling configured
// Bad: No worker process management
// Bad: Messages pile up when admin is not open

// Bad: Running worker without process manager
// $ bin/console messenger:consume async
// Process dies on error, no automatic restart
```

### Correct

```php
// Good: Disable Admin worker in production
// config/packages/prod/shopware.yaml
shopware:
    admin_worker:
        enable_admin_worker: false  // Good: Disabled for production

// Good: Configure transports properly
// config/packages/messenger.yaml
framework:
    messenger:
        failure_transport: failed

        transports:
            async:
                dsn: '%env(MESSENGER_TRANSPORT_DSN)%'
                options:
                    queue_name: shopware_async
                retry_strategy:
                    max_retries: 3
                    delay: 1000
                    multiplier: 2

            failed:
                dsn: 'doctrine://default?queue_name=failed'

// Good: Supervisor configuration for CLI worker
// /etc/supervisor/conf.d/shopware-worker.conf
/*
[program:shopware-worker]
command=/usr/bin/php /var/www/shopware/bin/console messenger:consume async --time-limit=300 --memory-limit=512M
user=www-data
numprocs=2
startsecs=0
autostart=true
autorestart=true
startretries=10
process_name=%(program_name)s_%(process_num)02d
stdout_logfile=/var/log/shopware/worker.log
stderr_logfile=/var/log/shopware/worker-error.log
*/

// Good: Environment-specific worker configuration
// .env.prod
// MESSENGER_TRANSPORT_DSN=doctrine://default?auto_setup=0

// Good: For high-load environments, use Redis or RabbitMQ
// MESSENGER_TRANSPORT_DSN=redis://localhost:6379/messages
// MESSENGER_TRANSPORT_DSN=amqp://guest:guest@localhost:5672/%2f/messages

// Good: Systemd alternative for worker management
// /etc/systemd/system/shopware-worker.service
/*
[Unit]
Description=Shopware Message Queue Worker
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/shopware
ExecStart=/usr/bin/php bin/console messenger:consume async --time-limit=300 --memory-limit=512M
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
*/

// Good: Multiple workers for different transports
/*
[program:shopware-worker-async]
command=/usr/bin/php /var/www/shopware/bin/console messenger:consume async --time-limit=300
numprocs=2

[program:shopware-worker-low-priority]
command=/usr/bin/php /var/www/shopware/bin/console messenger:consume low_priority --time-limit=600
numprocs=1
*/
```
