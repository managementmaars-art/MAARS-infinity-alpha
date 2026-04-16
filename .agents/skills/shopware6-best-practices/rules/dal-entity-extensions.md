---
title: DAL Entity Extensions
impact: MEDIUM
impactDescription: Incorrect entity extension patterns cause upgrade conflicts, data loss, and system instability
tags: [shopware6, dal, entity-extension, custom-fields, extensibility]
---

## DAL Entity Extensions

Entity extensions allow adding fields and associations to existing Shopware entities without modifying core files. Use EntityExtension for structural changes and custom fields for user-configurable data.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/add-complex-data-to-existing-entities

### Incorrect

```php
// Bad: Modifying core entity definition directly
// src/Core/Content/Product/ProductDefinition.php (DO NOT DO THIS)
class ProductDefinition extends EntityDefinition
{
    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            // ... core fields
            new StringField('my_custom_field', 'myCustomField'), // Wrong!
        ]);
    }
}

// Bad: Extending the wrong way - inheritance instead of extension
class CustomProductDefinition extends ProductDefinition
{
    public const ENTITY_NAME = 'product';

    protected function defineFields(): FieldCollection
    {
        $fields = parent::defineFields();
        $fields->add(new StringField('my_custom_field', 'myCustomField'));
        return $fields;
    }
}

// Bad: Missing service tag registration
class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        $collection->add(new StringField('custom_field', 'customField'));
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}
// Missing in services.xml: <tag name="shopware.entity.extension"/>

// Bad: Using wrong field for the data type
class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        // Using StringField for a boolean value
        $collection->add(new StringField('is_featured', 'isFeatured'));
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}

// Bad: Adding required field to existing entity
class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        $collection->add(
            (new StringField('external_id', 'externalId'))
                ->addFlags(new Required()) // Will break existing products!
        );
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}

// Bad: Not handling the database migration
class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        $collection->add(new StringField('custom_sku', 'customSku'));
        // Missing migration to add the column to product table
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}
```

### Correct

```php
// Good: Proper EntityExtension class
namespace MyPlugin\Core\Content\Product;

use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\EntityExtension;
use Shopware\Core\Framework\DataAbstractionLayer\Field\BoolField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\StringField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        $collection->add(
            (new StringField('my_plugin_external_id', 'myPluginExternalId'))
                ->addFlags(new ApiAware())
        );

        $collection->add(
            (new BoolField('my_plugin_is_featured', 'myPluginIsFeatured'))
                ->addFlags(new ApiAware())
        );
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}

// Good: Service registration in services.xml
/*
<service id="MyPlugin\Core\Content\Product\ProductExtension">
    <tag name="shopware.entity.extension"/>
</service>
*/

// Good: Corresponding migration
namespace MyPlugin\Migration;

use Doctrine\DBAL\Connection;
use Shopware\Core\Framework\Migration\MigrationStep;

class Migration1234567890AddProductExtensionFields extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1234567890;
    }

    public function update(Connection $connection): void
    {
        $connection->executeStatement('
            ALTER TABLE `product`
            ADD COLUMN `my_plugin_external_id` VARCHAR(255) NULL,
            ADD COLUMN `my_plugin_is_featured` TINYINT(1) NOT NULL DEFAULT 0
        ');
    }

    public function updateDestructive(Connection $connection): void
    {
        // Intentionally empty
    }
}

// Good: Adding OneToOne association via extension
namespace MyPlugin\Core\Content\Product;

use MyPlugin\Core\Content\ProductMeta\ProductMetaDefinition;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\EntityExtension;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\OneToOneAssociationField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        $collection->add(
            (new OneToOneAssociationField(
                'myPluginMeta',
                'id',
                'product_id',
                ProductMetaDefinition::class,
                false
            ))->addFlags(new ApiAware())
        );
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}

// Good: Adding ManyToMany association via extension
namespace MyPlugin\Core\Content\Product;

use MyPlugin\Core\Content\Badge\BadgeDefinition;
use MyPlugin\Core\Content\Product\Aggregate\ProductBadge\ProductBadgeDefinition;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\EntityExtension;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\CascadeDelete;
use Shopware\Core\Framework\DataAbstractionLayer\Field\ManyToManyAssociationField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        $collection->add(
            (new ManyToManyAssociationField(
                'myPluginBadges',
                BadgeDefinition::class,
                ProductBadgeDefinition::class,
                'product_id',
                'badge_id'
            ))->addFlags(new ApiAware(), new CascadeDelete())
        );
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}

// Good: Using custom fields for simple user-configurable data
// Custom fields don't require entity extensions - they use the existing customFields JSON column
public function setProductCustomField(string $productId, Context $context): void
{
    $this->productRepository->update([
        [
            'id' => $productId,
            'customFields' => [
                'my_plugin_warranty_months' => 24,
                'my_plugin_is_eco_friendly' => true,
            ]
        ]
    ], $context);
}

// Good: Reading extended fields
public function getProductWithExtension(string $productId, Context $context): ?ProductEntity
{
    $criteria = new Criteria([$productId]);
    $criteria->addAssociation('myPluginMeta');

    $product = $this->productRepository->search($criteria, $context)->first();

    // Access extension data
    $externalId = $product->get('myPluginExternalId');
    $meta = $product->getExtension('myPluginMeta');

    return $product;
}

// Good: Creating custom entity extension with proper struct
namespace MyPlugin\Core\Content\Product;

use Shopware\Core\Framework\Struct\Struct;

class ProductExtensionStruct extends Struct
{
    protected ?string $myPluginExternalId = null;
    protected bool $myPluginIsFeatured = false;

    public function getMyPluginExternalId(): ?string
    {
        return $this->myPluginExternalId;
    }

    public function setMyPluginExternalId(?string $externalId): void
    {
        $this->myPluginExternalId = $externalId;
    }

    public function isMyPluginIsFeatured(): bool
    {
        return $this->myPluginIsFeatured;
    }

    public function setMyPluginIsFeatured(bool $isFeatured): void
    {
        $this->myPluginIsFeatured = $isFeatured;
    }
}

// Good: Prefix extension fields with plugin name to avoid conflicts
class ProductExtension extends EntityExtension
{
    public function extendFields(FieldCollection $collection): void
    {
        // Using prefix 'my_plugin_' prevents conflicts with other plugins
        $collection->add(
            (new StringField('my_plugin_vendor_code', 'myPluginVendorCode'))
                ->addFlags(new ApiAware())
        );
    }

    public function getDefinitionClass(): string
    {
        return ProductDefinition::class;
    }
}
```
