---
title: Custom Fields via App
impact: MEDIUM
impactDescription: extend entities with custom data without database migrations
tags: app, custom-fields, entity, extension
---

## Custom Fields via App

**Impact: MEDIUM (extend entities with custom data without database migrations)**

Apps can define custom fields that appear in the administration without database migrations. Use appropriate field types and configure visibility for the best user experience.

**Incorrect (poor custom field design):**

```xml
<!-- Bad: Generic names, missing translations, wrong types -->
<custom-field-set>
    <name>my_fields</name>
    <fields>
        <text name="field1">
            <label>Field 1</label>
        </text>
        <text name="field2">
            <label>Field 2</label>
        </text>
        <!-- Using text for everything -->
    </fields>
</custom-field-set>
```

**Correct custom field configuration:**

```xml
<!-- manifest.xml -->
<custom-fields>
    <!-- Product custom fields -->
    <custom-field-set>
        <name>my_app_product_extended</name>
        <label>My App Product Data</label>
        <label lang="de-DE">Meine App Produktdaten</label>

        <related-entities>
            <product/>
        </related-entities>

        <fields>
            <!-- Text field -->
            <text name="my_app_external_sku">
                <label>External SKU</label>
                <label lang="de-DE">Externe SKU</label>
                <help-text>The SKU used in the external system</help-text>
                <help-text lang="de-DE">Die SKU im externen System</help-text>
                <placeholder>Enter external SKU...</placeholder>
                <required>false</required>
                <position>1</position>
            </text>

            <!-- Boolean/Switch field -->
            <bool name="my_app_sync_enabled">
                <label>Sync Enabled</label>
                <label lang="de-DE">Synchronisierung aktiviert</label>
                <help-text>Enable synchronization with external system</help-text>
                <required>false</required>
                <position>2</position>
            </bool>

            <!-- Number field -->
            <int name="my_app_priority">
                <label>Sync Priority</label>
                <label lang="de-DE">Sync-Priorität</label>
                <help-text>Higher priority items sync first (1-100)</help-text>
                <required>false</required>
                <position>3</position>
                <steps>1</steps>
                <min>1</min>
                <max>100</max>
            </int>

            <!-- Float field -->
            <float name="my_app_weight_factor">
                <label>Weight Factor</label>
                <required>false</required>
                <position>4</position>
                <steps>0.01</steps>
                <min>0</min>
                <max>10</max>
            </float>

            <!-- Select/Dropdown field -->
            <single-select name="my_app_sync_status">
                <label>Sync Status</label>
                <label lang="de-DE">Sync-Status</label>
                <required>false</required>
                <position>5</position>
                <options>
                    <option value="pending">
                        <name>Pending</name>
                        <name lang="de-DE">Ausstehend</name>
                    </option>
                    <option value="synced">
                        <name>Synced</name>
                        <name lang="de-DE">Synchronisiert</name>
                    </option>
                    <option value="error">
                        <name>Error</name>
                        <name lang="de-DE">Fehler</name>
                    </option>
                </options>
            </single-select>

            <!-- Multi-select field -->
            <multi-select name="my_app_categories">
                <label>External Categories</label>
                <required>false</required>
                <position>6</position>
                <options>
                    <option value="electronics">
                        <name>Electronics</name>
                    </option>
                    <option value="clothing">
                        <name>Clothing</name>
                    </option>
                    <option value="home">
                        <name>Home & Garden</name>
                    </option>
                </options>
            </multi-select>

            <!-- DateTime field -->
            <datetime name="my_app_last_sync">
                <label>Last Synced At</label>
                <label lang="de-DE">Zuletzt synchronisiert</label>
                <required>false</required>
                <position>7</position>
            </datetime>

            <!-- JSON field (for complex data) -->
            <json name="my_app_metadata">
                <label>Sync Metadata</label>
                <required>false</required>
                <position>8</position>
            </json>

            <!-- Media selection field -->
            <single-entity-select name="my_app_document" entity="media">
                <label>Associated Document</label>
                <required>false</required>
                <position>9</position>
            </single-entity-select>

            <!-- Color picker field -->
            <colorpicker name="my_app_highlight_color">
                <label>Highlight Color</label>
                <required>false</required>
                <position>10</position>
            </colorpicker>

            <!-- Text area (multiline) -->
            <text-area name="my_app_notes">
                <label>Sync Notes</label>
                <required>false</required>
                <position>11</position>
            </text-area>

            <!-- HTML editor -->
            <html name="my_app_rich_description">
                <label>Rich Description</label>
                <required>false</required>
                <position>12</position>
            </html>
        </fields>
    </custom-field-set>

    <!-- Order custom fields -->
    <custom-field-set>
        <name>my_app_order_data</name>
        <label>My App Order Data</label>

        <related-entities>
            <order/>
        </related-entities>

        <fields>
            <text name="my_app_external_order_id">
                <label>External Order ID</label>
                <required>false</required>
                <position>1</position>
            </text>

            <bool name="my_app_exported">
                <label>Exported to ERP</label>
                <required>false</required>
                <position>2</position>
            </bool>

            <datetime name="my_app_export_date">
                <label>Export Date</label>
                <required>false</required>
                <position>3</position>
            </datetime>
        </fields>
    </custom-field-set>

    <!-- Customer custom fields -->
    <custom-field-set>
        <name>my_app_customer_data</name>
        <label>My App Customer Data</label>

        <related-entities>
            <customer/>
        </related-entities>

        <fields>
            <text name="my_app_crm_id">
                <label>CRM ID</label>
                <required>false</required>
                <position>1</position>
            </text>

            <single-select name="my_app_customer_tier">
                <label>Customer Tier</label>
                <required>false</required>
                <position>2</position>
                <options>
                    <option value="bronze"><name>Bronze</name></option>
                    <option value="silver"><name>Silver</name></option>
                    <option value="gold"><name>Gold</name></option>
                    <option value="platinum"><name>Platinum</name></option>
                </options>
            </single-select>
        </fields>
    </custom-field-set>
</custom-fields>
```

**Reading custom fields via API:**

```php
// In webhook handler or API call
$product = $shopwareClient->getProduct($shop, $productId);

$customFields = $product['customFields'] ?? [];
$externalSku = $customFields['my_app_external_sku'] ?? null;
$syncEnabled = $customFields['my_app_sync_enabled'] ?? false;
$lastSync = $customFields['my_app_last_sync'] ?? null;
```

**Writing custom fields via API:**

```php
// Update custom fields via Admin API
$this->shopwareClient->updateProduct($shop, $productId, [
    'customFields' => [
        'my_app_external_sku' => 'EXT-12345',
        'my_app_sync_enabled' => true,
        'my_app_sync_status' => 'synced',
        'my_app_last_sync' => (new \DateTime())->format('c'),
        'my_app_metadata' => [
            'source' => 'erp',
            'version' => '2.0'
        ]
    ]
]);
```

**Available field types:**

| Type | Use Case |
|------|----------|
| `text` | Single line text |
| `text-area` | Multi-line text |
| `html` | Rich text with HTML |
| `bool` | Yes/No toggle |
| `int` | Whole numbers |
| `float` | Decimal numbers |
| `datetime` | Date and time |
| `single-select` | Dropdown selection |
| `multi-select` | Multiple selection |
| `colorpicker` | Color value |
| `single-entity-select` | Entity reference |
| `multi-entity-select` | Multiple entity references |
| `json` | Complex JSON data |
| `price` | Price values |
| `media` | Media selection |

Reference: [Custom Fields](https://developer.shopware.com/docs/guides/plugins/apps/custom-data/custom-fields.html)
