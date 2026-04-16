---
title: CI/CD Pipeline Configuration
impact: MEDIUM
impactDescription: automated testing and deployment workflows
tags: devops, ci-cd, github-actions, gitlab-ci, automation
---

## CI/CD Pipeline Configuration

**Impact: MEDIUM (automated testing and deployment workflows)**

Configure CI/CD pipelines for automated testing, building, and deployment of Shopware plugins and projects.

**Correct GitHub Actions workflow:**

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PHP_VERSION: '8.2'
  NODE_VERSION: '18'
  COMPOSER_VERSION: '2'

jobs:
  # Lint and static analysis
  code-quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ env.PHP_VERSION }}
          extensions: mbstring, xml, ctype, iconv, intl, pdo_mysql, dom
          coverage: none

      - name: Cache Composer dependencies
        uses: actions/cache@v3
        with:
          path: vendor
          key: composer-${{ hashFiles('composer.lock') }}

      - name: Install dependencies
        run: composer install --no-progress --prefer-dist

      - name: PHPStan
        run: vendor/bin/phpstan analyse --error-format=github

      - name: PHP CS Fixer
        run: vendor/bin/php-cs-fixer fix --dry-run --diff

  # Unit tests
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ env.PHP_VERSION }}
          extensions: mbstring, xml, ctype, iconv, intl, pdo_mysql, dom
          coverage: xdebug

      - name: Install dependencies
        run: composer install --no-progress --prefer-dist

      - name: Run unit tests
        run: vendor/bin/phpunit --testsuite unit --coverage-clover coverage.xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: coverage.xml

  # Integration tests
  integration-tests:
    runs-on: ubuntu-latest
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: shopware_test
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=5

      elasticsearch:
        image: elasticsearch:7.17.10
        env:
          discovery.type: single-node
        ports:
          - 9200:9200

    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ env.PHP_VERSION }}
          extensions: mbstring, xml, ctype, iconv, intl, pdo_mysql, dom

      - name: Install dependencies
        run: composer install --no-progress --prefer-dist

      - name: Setup Shopware
        run: |
          cp .env.test.dist .env.test
          bin/console system:install --basic-setup --no-interaction
        env:
          DATABASE_URL: mysql://root:root@127.0.0.1:3306/shopware_test

      - name: Run integration tests
        run: vendor/bin/phpunit --testsuite integration
        env:
          DATABASE_URL: mysql://root:root@127.0.0.1:3306/shopware_test

  # Build assets
  build-assets:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: src/Resources/app/storefront/package-lock.json

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ env.PHP_VERSION }}

      - name: Install Composer dependencies
        run: composer install --no-progress --prefer-dist

      - name: Build Storefront
        run: |
          npm ci --prefix src/Resources/app/storefront
          npm run build --prefix src/Resources/app/storefront

      - name: Build Administration
        run: |
          npm ci --prefix src/Resources/app/administration
          npm run build --prefix src/Resources/app/administration

      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: assets
          path: |
            src/Resources/public
            src/Resources/app/storefront/dist
            src/Resources/app/administration/dist

  # Create release package
  package:
    needs: [code-quality, unit-tests, integration-tests, build-assets]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    steps:
      - uses: actions/checkout@v4

      - name: Download assets
        uses: actions/download-artifact@v3
        with:
          name: assets

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: ${{ env.PHP_VERSION }}

      - name: Install production dependencies
        run: composer install --no-dev --optimize-autoloader

      - name: Create ZIP package
        run: |
          PLUGIN_NAME=$(basename $GITHUB_REPOSITORY)
          VERSION=${GITHUB_REF#refs/tags/}
          zip -r "${PLUGIN_NAME}-${VERSION}.zip" . \
            -x ".git/*" \
            -x ".github/*" \
            -x "tests/*" \
            -x "*.md" \
            -x ".env*" \
            -x "phpunit.xml*" \
            -x "phpstan.neon*"

      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          files: "*.zip"
          generate_release_notes: true

  # Deploy to staging
  deploy-staging:
    needs: [code-quality, unit-tests, build-assets]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/develop'
    environment:
      name: staging
      url: https://staging.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Download assets
        uses: actions/download-artifact@v3
        with:
          name: assets

      - name: Deploy to staging
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /var/www/staging
            git pull origin develop
            composer install --no-dev
            bin/console cache:clear
            bin/console theme:compile

  # Deploy to production
  deploy-production:
    needs: [code-quality, unit-tests, integration-tests, build-assets]
    runs-on: ubuntu-latest
    if: startsWith(github.ref, 'refs/tags/')
    environment:
      name: production
      url: https://www.example.com
    steps:
      - uses: actions/checkout@v4

      - name: Download assets
        uses: actions/download-artifact@v3
        with:
          name: assets

      - name: Deploy to production
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /var/www/production
            ./deploy.sh
```

**Correct plugin release workflow:**

```yaml
# .github/workflows/release.yml

name: Release Plugin

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup PHP
        uses: shivammathur/setup-php@v2
        with:
          php-version: '8.2'

      - name: Validate composer.json
        run: composer validate

      - name: Get version
        id: version
        run: echo "version=${GITHUB_REF#refs/tags/v}" >> $GITHUB_OUTPUT

      - name: Update version in composer.json
        run: |
          jq '.version = "${{ steps.version.outputs.version }}"' composer.json > tmp.json
          mv tmp.json composer.json

      - name: Install dependencies
        run: composer install --no-dev --optimize-autoloader

      - name: Build assets
        run: |
          if [ -f "src/Resources/app/storefront/package.json" ]; then
            npm ci --prefix src/Resources/app/storefront
            npm run build --prefix src/Resources/app/storefront
          fi
          if [ -f "src/Resources/app/administration/package.json" ]; then
            npm ci --prefix src/Resources/app/administration
            npm run build --prefix src/Resources/app/administration
          fi

      - name: Create plugin package
        run: |
          PLUGIN_NAME=$(jq -r '.extra."shopware-plugin-class"' composer.json | sed 's/.*\\//')
          mkdir -p dist/$PLUGIN_NAME
          rsync -av --exclude='.git' --exclude='.github' --exclude='tests' --exclude='node_modules' \
            --exclude='.env*' --exclude='phpunit.xml*' --exclude='phpstan.neon*' \
            ./ dist/$PLUGIN_NAME/
          cd dist && zip -r "../${PLUGIN_NAME}-${{ steps.version.outputs.version }}.zip" $PLUGIN_NAME

      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: "*.zip"
          body: |
            ## Changes in ${{ steps.version.outputs.version }}

            See [CHANGELOG.md](CHANGELOG.md) for details.

            ### Installation
            1. Download the ZIP file
            2. Upload via Administration > Extensions > Upload plugin
            3. Install and activate
```

**Environment secrets needed:**

| Secret | Description |
|--------|-------------|
| `STAGING_HOST` | Staging server hostname |
| `STAGING_USER` | SSH username |
| `STAGING_SSH_KEY` | SSH private key |
| `PROD_HOST` | Production server hostname |
| `PROD_USER` | SSH username |
| `PROD_SSH_KEY` | SSH private key |
| `CODECOV_TOKEN` | Code coverage token |

Reference: [GitHub Actions](https://docs.github.com/en/actions)
