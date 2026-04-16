---
title: Deployment & Build Process
impact: HIGH
impactDescription: reliable production deployments
tags: devops, deployment, build, production, release
---

## Deployment & Build Process

**Impact: HIGH (reliable production deployments)**

Production deployments require proper build processes, asset compilation, and deployment procedures. Use CI/CD pipelines for consistent releases.

**Correct deployment script:**

```bash
#!/bin/bash
# deploy.sh

set -e

# Configuration
DEPLOY_PATH="/var/www/html"
SHARED_PATH="/var/www/shared"
RELEASES_PATH="/var/www/releases"
CURRENT_RELEASE=$(date +%Y%m%d%H%M%S)
KEEP_RELEASES=5

echo "Starting deployment: $CURRENT_RELEASE"

# Create release directory
mkdir -p "$RELEASES_PATH/$CURRENT_RELEASE"
cd "$RELEASES_PATH/$CURRENT_RELEASE"

# Clone/copy code
echo "Copying code..."
rsync -a --exclude='.git' --exclude='node_modules' --exclude='var' \
    /tmp/build/ "$RELEASES_PATH/$CURRENT_RELEASE/"

# Link shared directories
echo "Linking shared directories..."
ln -sfn "$SHARED_PATH/var/log" "$RELEASES_PATH/$CURRENT_RELEASE/var/log"
ln -sfn "$SHARED_PATH/var/cache" "$RELEASES_PATH/$CURRENT_RELEASE/var/cache"
ln -sfn "$SHARED_PATH/public/media" "$RELEASES_PATH/$CURRENT_RELEASE/public/media"
ln -sfn "$SHARED_PATH/public/thumbnail" "$RELEASES_PATH/$CURRENT_RELEASE/public/thumbnail"
ln -sfn "$SHARED_PATH/files" "$RELEASES_PATH/$CURRENT_RELEASE/files"
ln -sfn "$SHARED_PATH/config/jwt" "$RELEASES_PATH/$CURRENT_RELEASE/config/jwt"
ln -sfn "$SHARED_PATH/.env.local" "$RELEASES_PATH/$CURRENT_RELEASE/.env.local"

# Install dependencies (production)
echo "Installing dependencies..."
cd "$RELEASES_PATH/$CURRENT_RELEASE"
composer install --no-dev --optimize-autoloader --no-interaction

# Build assets (should be done in CI, but can be done here)
if [ ! -d "public/bundles" ]; then
    echo "Building storefront assets..."
    bin/build-storefront.sh

    echo "Building administration assets..."
    bin/build-administration.sh
fi

# Run migrations
echo "Running migrations..."
bin/console database:migrate --all --no-interaction

# Clear and warm up cache
echo "Clearing cache..."
bin/console cache:clear --no-debug
bin/console cache:warmup --no-debug

# Compile theme
echo "Compiling theme..."
bin/console theme:compile --no-debug

# Update DAL index
echo "Refreshing DAL index..."
bin/console dal:refresh:index --no-debug

# Update plugin list
echo "Refreshing plugins..."
bin/console plugin:refresh --no-debug

# Activate new release
echo "Activating release..."
ln -sfn "$RELEASES_PATH/$CURRENT_RELEASE" "$DEPLOY_PATH"

# Restart PHP-FPM
echo "Restarting PHP-FPM..."
sudo systemctl reload php8.2-fpm

# Cleanup old releases
echo "Cleaning up old releases..."
cd "$RELEASES_PATH"
ls -1t | tail -n +$((KEEP_RELEASES + 1)) | xargs -r rm -rf

echo "Deployment complete: $CURRENT_RELEASE"
```

**Correct CI build process (GitLab CI):**

```yaml
# .gitlab-ci.yml

stages:
  - test
  - build
  - deploy

variables:
  COMPOSER_HOME: /cache/composer
  npm_config_cache: /cache/npm

# Test stage
test:
  stage: test
  image: dockware/dev:6.6.0.0
  services:
    - mysql:8.0
  variables:
    DATABASE_URL: mysql://root:root@mysql:3306/shopware_test
  script:
    - composer install --no-interaction
    - bin/console system:install --basic-setup --no-interaction
    - vendor/bin/phpunit --configuration phpunit.xml.dist
    - vendor/bin/phpstan analyse src --level 8
  only:
    - merge_requests
    - main

# Build assets
build:
  stage: build
  image: dockware/dev:6.6.0.0
  script:
    - composer install --no-dev --optimize-autoloader
    - bin/build-storefront.sh
    - bin/build-administration.sh
  artifacts:
    paths:
      - vendor/
      - public/bundles/
      - public/theme/
    expire_in: 1 hour
  only:
    - main
    - tags

# Deploy to staging
deploy:staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh rsync
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | ssh-add -
    - mkdir -p ~/.ssh && chmod 700 ~/.ssh
    - echo "$SSH_KNOWN_HOSTS" >> ~/.ssh/known_hosts
  script:
    - rsync -avz --delete --exclude='.git' ./ $STAGING_USER@$STAGING_HOST:$STAGING_PATH/
    - ssh $STAGING_USER@$STAGING_HOST "cd $STAGING_PATH && ./deploy.sh"
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main

# Deploy to production
deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh rsync
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | ssh-add -
    - mkdir -p ~/.ssh && chmod 700 ~/.ssh
    - echo "$SSH_KNOWN_HOSTS" >> ~/.ssh/known_hosts
  script:
    - rsync -avz --delete --exclude='.git' ./ $PROD_USER@$PROD_HOST:$PROD_PATH/
    - ssh $PROD_USER@$PROD_HOST "cd $PROD_PATH && ./deploy.sh"
  environment:
    name: production
    url: https://www.example.com
  when: manual
  only:
    - tags
```

**Correct production .env:**

```env
# .env (production template)

APP_ENV=prod
APP_DEBUG=0
APP_URL=https://www.example.com
APP_SECRET=${APP_SECRET}

DATABASE_URL=mysql://${DB_USER}:${DB_PASS}@${DB_HOST}:3306/${DB_NAME}

MAILER_DSN=smtp://${SMTP_HOST}:${SMTP_PORT}

# Caching
SHOPWARE_HTTP_CACHE_ENABLED=1
SHOPWARE_HTTP_DEFAULT_TTL=7200
CACHE_ADAPTER=redis
REDIS_URL=redis://${REDIS_HOST}:6379

# Elasticsearch
SHOPWARE_ES_ENABLED=1
SHOPWARE_ES_INDEXING_ENABLED=1
OPENSEARCH_URL=http://${ES_HOST}:9200

# Session
SESSION_HANDLER=redis
SESSION_REDIS_URL=redis://${REDIS_HOST}:6379/1

# Worker
MESSENGER_TRANSPORT_DSN=redis://${REDIS_HOST}:6379/messages

# Logging
LOG_CHANNEL=production
SHOPWARE_LOG_LEVEL=warning
```

**Correct rollback procedure:**

```bash
#!/bin/bash
# rollback.sh

set -e

DEPLOY_PATH="/var/www/html"
RELEASES_PATH="/var/www/releases"

# Get previous release
PREVIOUS=$(ls -1t "$RELEASES_PATH" | sed -n '2p')

if [ -z "$PREVIOUS" ]; then
    echo "No previous release found!"
    exit 1
fi

echo "Rolling back to: $PREVIOUS"

# Switch symlink
ln -sfn "$RELEASES_PATH/$PREVIOUS" "$DEPLOY_PATH"

# Clear cache
cd "$DEPLOY_PATH"
bin/console cache:clear --no-debug

# Restart PHP-FPM
sudo systemctl reload php8.2-fpm

echo "Rollback complete: $PREVIOUS"
```

**Deployment checklist:**

| Step | Command/Action |
|------|----------------|
| 1. Backup database | `mysqldump shopware > backup.sql` |
| 2. Enable maintenance | `bin/console sales-channel:maintenance:enable --all` |
| 3. Deploy code | Run deployment script |
| 4. Run migrations | `bin/console database:migrate --all` |
| 5. Clear cache | `bin/console cache:clear` |
| 6. Compile theme | `bin/console theme:compile` |
| 7. Warm cache | `bin/console cache:warmup` |
| 8. Disable maintenance | `bin/console sales-channel:maintenance:disable --all` |
| 9. Verify | Check logs, test checkout |

Reference: [Deployment](https://developer.shopware.com/docs/guides/hosting/installation-updates/deployments/deployment-with-deployer.html)
