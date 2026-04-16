---
title: Dockware & Local Development
impact: HIGH
impactDescription: efficient development environment setup
tags: devops, docker, dockware, development, environment
---

## Dockware & Local Development

**Impact: HIGH (efficient development environment setup)**

Dockware provides pre-configured Docker images for Shopware 6 development. Use proper environment configuration for efficient local development.

**Correct docker-compose.yml setup:**

```yaml
# docker-compose.yml
version: "3.8"

services:
  shopware:
    image: dockware/dev:6.6.0.0
    container_name: shopware
    ports:
      - "80:80"       # HTTP
      - "443:443"     # HTTPS
      - "8888:8888"   # Adminer
      - "9998:9998"   # Mailcatcher
      - "9999:9999"   # Watch mode
    environment:
      - PHP_VERSION=8.2
      - XDEBUG_ENABLED=1
      - COMPOSER_VERSION=2
      - SW_CURRENCY=EUR
    volumes:
      # Mount custom plugins
      - ./custom/plugins:/var/www/html/custom/plugins
      # Mount custom apps
      - ./custom/apps:/var/www/html/custom/apps
      # Mount for persistent var/log
      - ./var/log:/var/www/html/var/log
      # SSH keys for Git operations
      - ~/.ssh:/var/www/.ssh:ro
    networks:
      - shopware

  mysql:
    image: mysql:8.0
    container_name: shopware_mysql
    environment:
      - MYSQL_ROOT_PASSWORD=root
      - MYSQL_DATABASE=shopware
      - MYSQL_USER=shopware
      - MYSQL_PASSWORD=shopware
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"
    networks:
      - shopware

  # Optional: Elasticsearch for large catalogs
  elasticsearch:
    image: elasticsearch:7.17.10
    container_name: shopware_es
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - shopware

  # Optional: Redis for session/cache
  redis:
    image: redis:7-alpine
    container_name: shopware_redis
    ports:
      - "6379:6379"
    networks:
      - shopware

volumes:
  mysql_data:
  es_data:

networks:
  shopware:
```

**Correct .env for local development:**

```env
# .env.local

# Database
DATABASE_URL=mysql://shopware:shopware@mysql:3306/shopware

# Application
APP_ENV=dev
APP_DEBUG=1
APP_URL=http://localhost
APP_SECRET=devsecret123

# Admin credentials (initial setup)
SHOPWARE_ADMIN_USER=admin
SHOPWARE_ADMIN_PASSWORD=shopware

# Mailer (Mailcatcher)
MAILER_DSN=smtp://localhost:1025

# Elasticsearch (optional)
SHOPWARE_ES_ENABLED=0
SHOPWARE_ES_INDEXING_ENABLED=0
OPENSEARCH_URL=http://elasticsearch:9200

# Redis (optional)
REDIS_URL=redis://redis:6379

# Disable SSL verification for development
SHOPWARE_HTTP_CACHE_ENABLED=0
SHOPWARE_HTTP_DEFAULT_TTL=7200

# Worker settings
MESSENGER_TRANSPORT_DSN=doctrine://default?auto_setup=0

# Asset handling
SHOPWARE_CDN_STRATEGY_DEFAULT=id

# Logging
SHOPWARE_LOG_LEVEL=debug
```

**Correct development Makefile:**

```makefile
# Makefile

.PHONY: start stop shell logs build watch clear test

# Start containers
start:
	docker-compose up -d
	@echo "Shopware is starting at http://localhost"
	@echo "Admin: http://localhost/admin"

# Stop containers
stop:
	docker-compose down

# Shell into container
shell:
	docker exec -it shopware bash

# View logs
logs:
	docker-compose logs -f shopware

# Build storefront assets
build:
	docker exec shopware bash -c "cd /var/www/html && bin/build-storefront.sh"

# Build admin assets
build-admin:
	docker exec shopware bash -c "cd /var/www/html && bin/build-administration.sh"

# Watch mode for storefront
watch:
	docker exec shopware bash -c "cd /var/www/html && bin/watch-storefront.sh"

# Watch mode for admin
watch-admin:
	docker exec shopware bash -c "cd /var/www/html && bin/watch-administration.sh"

# Clear cache
clear:
	docker exec shopware bash -c "cd /var/www/html && bin/console cache:clear"

# Run tests
test:
	docker exec shopware bash -c "cd /var/www/html && vendor/bin/phpunit --configuration phpunit.xml.dist"

# Install plugin
plugin-install:
	docker exec shopware bash -c "cd /var/www/html && bin/console plugin:refresh && bin/console plugin:install --activate $(PLUGIN)"

# Refresh plugins
plugin-refresh:
	docker exec shopware bash -c "cd /var/www/html && bin/console plugin:refresh"

# Database migration
migrate:
	docker exec shopware bash -c "cd /var/www/html && bin/console database:migrate --all"

# Create migration
migration-create:
	docker exec shopware bash -c "cd /var/www/html && bin/console database:create-migration -p $(PLUGIN)"

# DAL refresh
dal-refresh:
	docker exec shopware bash -c "cd /var/www/html && bin/console dal:refresh:index"

# Theme compile
theme:
	docker exec shopware bash -c "cd /var/www/html && bin/console theme:compile"

# Reset (dangerous!)
reset:
	docker-compose down -v
	docker-compose up -d
	@echo "Waiting for services..."
	sleep 30
	docker exec shopware bash -c "cd /var/www/html && bin/console system:install --basic-setup"
```

**Correct plugin development workflow:**

```bash
# 1. Create new plugin skeleton
bin/console plugin:create MyVendorMyPlugin

# 2. Install and activate
bin/console plugin:refresh
bin/console plugin:install --activate MyVendorMyPlugin

# 3. Create migration
bin/console database:create-migration -p MyVendorMyPlugin

# 4. Run migration
bin/console database:migrate --all

# 5. Watch storefront changes
bin/watch-storefront.sh

# 6. Build for production
bin/build-storefront.sh
bin/build-administration.sh

# 7. Clear caches after changes
bin/console cache:clear
```

**Correct Xdebug configuration (.vscode/launch.json):**

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Listen for Xdebug",
            "type": "php",
            "request": "launch",
            "port": 9003,
            "pathMappings": {
                "/var/www/html": "${workspaceFolder}"
            },
            "hostname": "0.0.0.0"
        }
    ]
}
```

**Correct PHPStorm path mapping:**

```
Server path: /var/www/html
Local path: /Users/you/projects/shopware
```

**Common development commands:**

| Command | Description |
|---------|-------------|
| `bin/console cache:clear` | Clear all caches |
| `bin/console plugin:refresh` | Refresh plugin list |
| `bin/console theme:compile` | Compile theme assets |
| `bin/console dal:refresh:index` | Refresh entity indexes |
| `bin/console scheduled-task:run` | Run scheduled tasks |
| `bin/console messenger:consume` | Process message queue |
| `bin/console debug:event-dispatcher` | List event subscribers |
| `bin/console debug:container` | List services |

Reference: [Dockware](https://dockware.io/)
