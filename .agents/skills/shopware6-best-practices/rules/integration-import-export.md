---
title: Import/Export Profiles
impact: HIGH
impactDescription: bulk data operations for products, customers, orders
tags: import, export, csv, profile, bulk
---

## Import/Export Profiles

**Impact: HIGH (bulk data operations for products, customers, orders)**

Custom import/export profiles enable bulk data operations. Implement proper field mappings, value converters, and validation for reliable data transfer.

**Incorrect (manual CSV processing):**

```php
// Bad: Manual CSV parsing without using Import/Export system
class ProductImporter
{
    public function import(string $csvPath): void
    {
        $file = fopen($csvPath, 'r');
        while ($row = fgetcsv($file)) {
            $this->productRepository->create([...], Context::createDefaultContext());
        }
    }
}
```

**Correct import/export profile definition:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Profile;

use Shopware\Core\Content\ImportExport\ImportExportProfileEntity;
use Shopware\Core\Framework\Context;

class ProductExtendedProfile
{
    public const PROFILE_NAME = 'My Extended Product Import';
    public const TECHNICAL_NAME = 'my_plugin_product_extended';

    public function __construct(
        private readonly EntityRepository $profileRepository
    ) {}

    public function install(Context $context): void
    {
        $this->profileRepository->upsert([
            [
                'name' => self::PROFILE_NAME,
                'technicalName' => self::TECHNICAL_NAME,
                'label' => 'Extended Product Import/Export',
                'type' => ImportExportProfileEntity::TYPE_IMPORT_EXPORT,
                'sourceEntity' => 'product',
                'fileType' => 'text/csv',
                'delimiter' => ';',
                'enclosure' => '"',
                'config' => [],
                'mapping' => [
                    // Standard mappings
                    ['key' => 'id', 'mappedKey' => 'id', 'position' => 0],
                    ['key' => 'productNumber', 'mappedKey' => 'product_number', 'position' => 1],
                    ['key' => 'name', 'mappedKey' => 'name', 'position' => 2],
                    ['key' => 'description', 'mappedKey' => 'description', 'position' => 3],
                    ['key' => 'active', 'mappedKey' => 'active', 'position' => 4],
                    ['key' => 'stock', 'mappedKey' => 'stock', 'position' => 5],

                    // Price mapping (nested)
                    ['key' => 'price.DEFAULT.gross', 'mappedKey' => 'price_gross', 'position' => 6],
                    ['key' => 'price.DEFAULT.net', 'mappedKey' => 'price_net', 'position' => 7],
                    ['key' => 'price.DEFAULT.linked', 'mappedKey' => 'price_linked', 'position' => 8, 'defaultValue' => 'true'],

                    // Tax mapping
                    ['key' => 'tax.id', 'mappedKey' => 'tax_id', 'position' => 9],
                    ['key' => 'tax.name', 'mappedKey' => 'tax_name', 'position' => 10],

                    // Manufacturer
                    ['key' => 'manufacturer.id', 'mappedKey' => 'manufacturer_id', 'position' => 11],
                    ['key' => 'manufacturer.name', 'mappedKey' => 'manufacturer_name', 'position' => 12],

                    // Categories (multiple via pipe separator)
                    ['key' => 'categories', 'mappedKey' => 'categories', 'position' => 13],

                    // Media
                    ['key' => 'cover.media.url', 'mappedKey' => 'cover_image_url', 'position' => 14],
                    ['key' => 'media', 'mappedKey' => 'additional_images', 'position' => 15],

                    // Custom fields
                    ['key' => 'customFields.my_plugin_external_id', 'mappedKey' => 'external_id', 'position' => 16],
                    ['key' => 'customFields.my_plugin_sync_status', 'mappedKey' => 'sync_status', 'position' => 17],

                    // Translations
                    ['key' => 'translations.DEFAULT.name', 'mappedKey' => 'name_default', 'position' => 18],
                    ['key' => 'translations.de-DE.name', 'mappedKey' => 'name_de', 'position' => 19],
                    ['key' => 'translations.en-GB.name', 'mappedKey' => 'name_en', 'position' => 20]
                ],
                'updateBy' => [
                    ['entityName' => 'product', 'mappedKey' => 'productNumber']
                ],
                'translations' => [
                    'de-DE' => ['label' => 'Erweiterter Produkt-Import/Export'],
                    'en-GB' => ['label' => 'Extended Product Import/Export']
                ]
            ]
        ], $context);
    }
}
```

**Correct custom value converter:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\ImportExport\Converter;

use Shopware\Core\Content\ImportExport\DataAbstractionLayer\Serializer\Field\AbstractFieldSerializer;
use Shopware\Core\Content\ImportExport\Struct\Config;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Field;

class ExternalIdConverter extends AbstractFieldSerializer
{
    public function serialize(Config $config, Field $field, $value): mixed
    {
        if ($value === null) {
            return '';
        }

        // Format external ID for export
        return 'EXT-' . $value;
    }

    public function deserialize(Config $config, Field $field, $value): mixed
    {
        if (empty($value)) {
            return null;
        }

        // Parse external ID from import
        if (str_starts_with($value, 'EXT-')) {
            return substr($value, 4);
        }

        return $value;
    }

    public function supports(Field $field): bool
    {
        return $field->getPropertyName() === 'my_plugin_external_id';
    }
}
```

**Correct programmatic import:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Core\Content\ImportExport\ImportExportFactory;
use Shopware\Core\Content\ImportExport\Service\ImportExportService;
use Shopware\Core\Framework\Context;
use Symfony\Component\HttpFoundation\File\UploadedFile;

class ProductImportService
{
    public function __construct(
        private readonly ImportExportFactory $importExportFactory,
        private readonly ImportExportService $importExportService,
        private readonly EntityRepository $profileRepository,
        private readonly LoggerInterface $logger
    ) {}

    public function importFromFile(string $filePath, Context $context): array
    {
        // Find profile
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('technicalName', 'my_plugin_product_extended'));
        $profile = $this->profileRepository->search($criteria, $context)->first();

        if (!$profile) {
            throw new \RuntimeException('Import profile not found');
        }

        // Create import log entry
        $expireDate = new \DateTime();
        $expireDate->modify('+1 week');

        $file = new UploadedFile($filePath, basename($filePath), 'text/csv', null, true);

        $log = $this->importExportService->prepareImport(
            $context,
            $profile->getId(),
            $expireDate,
            $file
        );

        $this->logger->info('Starting import', [
            'logId' => $log->getId(),
            'file' => $filePath
        ]);

        // Execute import
        $importExport = $this->importExportFactory->create($log->getId());
        $progress = $importExport->import($context);

        // Process in chunks
        while (!$progress->isFinished()) {
            $progress = $importExport->import($context, $progress->getOffset());

            $this->logger->info('Import progress', [
                'processed' => $progress->getProcessedRecords(),
                'total' => $progress->getTotalRecords()
            ]);
        }

        return [
            'total' => $progress->getTotalRecords(),
            'processed' => $progress->getProcessedRecords(),
            'errors' => $progress->getInvalidRecordsLogId() ? $this->getErrors($progress->getInvalidRecordsLogId(), $context) : []
        ];
    }

    public function exportToFile(Criteria $criteria, Context $context): string
    {
        $criteria->addFilter(new EqualsFilter('technicalName', 'my_plugin_product_extended'));
        $profile = $this->profileRepository->search($criteria, $context)->first();

        $expireDate = new \DateTime();
        $expireDate->modify('+1 week');

        $log = $this->importExportService->prepareExport(
            $context,
            $profile->getId(),
            $expireDate
        );

        $importExport = $this->importExportFactory->create($log->getId());
        $progress = $importExport->export($context, new Criteria());

        while (!$progress->isFinished()) {
            $progress = $importExport->export($context, new Criteria(), $progress->getOffset());
        }

        return $log->getFile()->getPath();
    }

    private function getErrors(string $invalidLogId, Context $context): array
    {
        // Fetch invalid records for error reporting
        $criteria = new Criteria([$invalidLogId]);
        $log = $this->importExportService->getLogRepository()->search($criteria, $context)->first();

        return $log?->getRecords() ?? [];
    }
}
```

**Correct message handler for async import:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\MessageHandler;

use Symfony\Component\Messenger\Attribute\AsMessageHandler;

#[AsMessageHandler]
class ProductImportHandler
{
    public function __construct(
        private readonly ProductImportService $importService,
        private readonly LoggerInterface $logger
    ) {}

    public function __invoke(ProductImportMessage $message): void
    {
        $context = Context::createDefaultContext();

        try {
            $result = $this->importService->importFromFile(
                $message->getFilePath(),
                $context
            );

            $this->logger->info('Import completed', $result);

        } catch (\Exception $e) {
            $this->logger->error('Import failed', [
                'file' => $message->getFilePath(),
                'error' => $e->getMessage()
            ]);
            throw $e;
        }
    }
}
```

**Service registration:**

```xml
<service id="MyVendor\MyPlugin\ImportExport\Converter\ExternalIdConverter">
    <tag name="shopware.import_export.field_serializer"/>
</service>

<service id="MyVendor\MyPlugin\Service\ProductImportService">
    <argument type="service" id="Shopware\Core\Content\ImportExport\ImportExportFactory"/>
    <argument type="service" id="Shopware\Core\Content\ImportExport\Service\ImportExportService"/>
    <argument type="service" id="import_export_profile.repository"/>
    <argument type="service" id="logger"/>
</service>
```

Reference: [Import/Export](https://developer.shopware.com/docs/guides/plugins/plugins/content/import-export/add-custom-profile.html)
