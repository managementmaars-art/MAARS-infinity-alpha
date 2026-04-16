---
title: Implement Plugin Configuration Correctly
impact: MEDIUM
impactDescription: enables flexible and maintainable plugin settings
tags: configuration, settings, admin, system-config
---

## Implement Plugin Configuration Correctly

**Impact: MEDIUM (enables flexible and maintainable plugin settings)**

Plugin configuration allows merchants to customize behavior without code changes. Proper implementation ensures type safety and admin UI integration.

**Incorrect (configuration anti-patterns):**

```php
// Bad: Hardcoded values
class MyService
{
    private const API_URL = 'https://api.example.com';
    private const TIMEOUT = 30;

    public function callApi(): void
    {
        // Hardcoded - can't change without code deployment
        $client->request('GET', self::API_URL, ['timeout' => self::TIMEOUT]);
    }
}

// Bad: Reading config without sales channel context
class ConfigReader
{
    public function getApiKey(): string
    {
        // Bad: No sales channel - gets global value only
        return $this->systemConfigService->get('MyPlugin.config.apiKey');
    }
}

// Bad: No validation of config values
class PaymentProcessor
{
    public function process(): void
    {
        $timeout = $this->systemConfigService->get('MyPlugin.config.timeout');
        // $timeout could be null, empty string, negative number...
        $this->client->setTimeout($timeout);  // Potential error!
    }
}

// Bad: Config in environment variables for shop-specific settings
// .env
MY_PLUGIN_API_KEY=secret123  // Can't differ per sales channel!
```

**Correct (proper configuration implementation):**

```xml
<!-- Good: config.xml in src/Resources/config/ -->
<?xml version="1.0" encoding="UTF-8"?>
<config xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/platform/trunk/src/Core/System/SystemConfig/Schema/config.xsd">

    <card>
        <title>API Settings</title>
        <title lang="de-DE">API Einstellungen</title>

        <input-field type="text">
            <name>apiUrl</name>
            <label>API URL</label>
            <label lang="de-DE">API URL</label>
            <placeholder>https://api.example.com</placeholder>
            <helpText>The base URL for API calls</helpText>
            <required>true</required>
        </input-field>

        <input-field type="password">
            <name>apiKey</name>
            <label>API Key</label>
            <label lang="de-DE">API Schlüssel</label>
            <required>true</required>
        </input-field>

        <input-field type="int">
            <name>timeout</name>
            <label>Timeout (seconds)</label>
            <defaultValue>30</defaultValue>
            <helpText>Request timeout in seconds</helpText>
        </input-field>

        <input-field type="bool">
            <name>debugMode</name>
            <label>Debug Mode</label>
            <defaultValue>false</defaultValue>
        </input-field>

        <input-field type="single-select">
            <name>environment</name>
            <label>Environment</label>
            <defaultValue>production</defaultValue>
            <options>
                <option>
                    <id>sandbox</id>
                    <name>Sandbox</name>
                </option>
                <option>
                    <id>production</id>
                    <name>Production</name>
                </option>
            </options>
        </input-field>
    </card>

    <card>
        <title>Feature Flags</title>

        <input-field type="bool">
            <name>enableFeatureX</name>
            <label>Enable Feature X</label>
            <defaultValue>false</defaultValue>
        </input-field>

        <input-field type="multi-select">
            <name>enabledPaymentMethods</name>
            <label>Enabled Payment Methods</label>
            <options>
                <option>
                    <id>credit_card</id>
                    <name>Credit Card</name>
                </option>
                <option>
                    <id>paypal</id>
                    <name>PayPal</name>
                </option>
                <option>
                    <id>invoice</id>
                    <name>Invoice</name>
                </option>
            </options>
        </input-field>
    </card>
</config>
```

```php
// Good: Typed configuration service
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\System\SystemConfig\SystemConfigService;

class PluginConfigService
{
    private const CONFIG_PREFIX = 'MyVendorMyPlugin.config.';

    public function __construct(
        private readonly SystemConfigService $systemConfigService
    ) {}

    // Good: Sales channel aware with fallback
    public function getApiUrl(?string $salesChannelId = null): string
    {
        $value = $this->systemConfigService->get(
            self::CONFIG_PREFIX . 'apiUrl',
            $salesChannelId
        );

        return is_string($value) && $value !== ''
            ? $value
            : 'https://api.example.com';  // Fallback default
    }

    public function getApiKey(?string $salesChannelId = null): string
    {
        $value = $this->systemConfigService->get(
            self::CONFIG_PREFIX . 'apiKey',
            $salesChannelId
        );

        if (!is_string($value) || $value === '') {
            throw new ConfigurationException('API key is not configured');
        }

        return $value;
    }

    public function getTimeout(?string $salesChannelId = null): int
    {
        $value = $this->systemConfigService->get(
            self::CONFIG_PREFIX . 'timeout',
            $salesChannelId
        );

        return is_int($value) && $value > 0 ? $value : 30;
    }

    public function isDebugMode(?string $salesChannelId = null): bool
    {
        return (bool) $this->systemConfigService->get(
            self::CONFIG_PREFIX . 'debugMode',
            $salesChannelId
        );
    }

    public function isFeatureEnabled(string $feature, ?string $salesChannelId = null): bool
    {
        return (bool) $this->systemConfigService->get(
            self::CONFIG_PREFIX . 'enable' . ucfirst($feature),
            $salesChannelId
        );
    }
}
```

```php
// Good: Using config in service
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class ApiClient
{
    public function __construct(
        private readonly PluginConfigService $config,
        private readonly HttpClientInterface $httpClient
    ) {}

    public function request(string $endpoint, SalesChannelContext $context): array
    {
        $salesChannelId = $context->getSalesChannelId();

        // Good: Get sales channel specific config
        $baseUrl = $this->config->getApiUrl($salesChannelId);
        $apiKey = $this->config->getApiKey($salesChannelId);
        $timeout = $this->config->getTimeout($salesChannelId);

        $response = $this->httpClient->request('GET', $baseUrl . $endpoint, [
            'timeout' => $timeout,
            'headers' => [
                'Authorization' => 'Bearer ' . $apiKey,
            ],
        ]);

        return json_decode($response->getContent(), true);
    }
}
```

**Configuration field types:**

| Type | PHP Type | Use Case |
|------|----------|----------|
| `text` | string | Short text, URLs |
| `textarea` | string | Long text, JSON |
| `password` | string | API keys, secrets |
| `int` | int | Numbers, timeouts |
| `float` | float | Prices, percentages |
| `bool` | bool | Feature flags |
| `single-select` | string | Dropdown |
| `multi-select` | array | Multiple choice |
| `colorpicker` | string | Color values |
| `datetime` | string | Date/time values |

Reference: [Plugin Configuration](https://developer.shopware.com/docs/guides/plugins/plugins/plugin-fundamentals/add-plugin-configuration.html)
