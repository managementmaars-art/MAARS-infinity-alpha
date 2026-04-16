---
title: DAL Custom Entities
impact: MEDIUM
impactDescription: Improper entity definitions cause data integrity issues, API problems, and maintainability challenges
tags: [shopware6, dal, custom-entity, entity-definition, fields, flags]
---

## DAL Custom Entities

Custom entity definitions define the structure and behavior of your data in Shopware 6. Proper field types, flags, and relationships ensure data integrity and API compatibility.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/data-handling/add-custom-complex-data

### Incorrect

```php
// Bad: Missing required flags and fields
class BadgeDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_badge';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            new IdField('id', 'id'), // Missing PrimaryKey flag
            new StringField('name', 'name'), // Missing Required flag
            new StringField('color', 'color'),
        ]);
    }
}

// Bad: Wrong field type for the data
class ProductReviewDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_product_review';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),
            new StringField('rating', 'rating'), // Should be IntField or FloatField
            new StringField('is_verified', 'isVerified'), // Should be BoolField
            new StringField('content', 'content'), // Should be LongTextField for long content
            new StringField('created_at', 'createdAt'), // Should be DateTimeField
        ]);
    }
}

// Bad: Missing entity class reference
class WishlistDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_wishlist';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    // Missing getEntityClass() method

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),
            (new StringField('name', 'name'))->addFlags(new Required()),
        ]);
    }
}

// Bad: Foreign key without association
class ProductTagDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_product_tag';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),
            (new FkField('product_id', 'productId', ProductDefinition::class))->addFlags(new Required()),
            // Missing ManyToOneAssociationField for 'product'
            (new StringField('tag', 'tag'))->addFlags(new Required()),
        ]);
    }
}

// Bad: Not using translation for translatable fields
class CategoryExtendedDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_category_extended';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),
            // These should be in a translation entity
            (new StringField('seo_title', 'seoTitle')),
            (new LongTextField('seo_description', 'seoDescription')),
        ]);
    }
}

// Bad: Missing cascade delete on parent relation
class ProductVariantDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_product_variant';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),
            (new FkField('product_id', 'productId', ProductDefinition::class))->addFlags(new Required()),
            // When product is deleted, orphan variants remain!
            new ManyToOneAssociationField('product', 'product_id', ProductDefinition::class),
        ]);
    }
}
```

### Correct

```php
// Good: Complete entity definition with proper flags
namespace MyPlugin\Core\Content\Badge;

use Shopware\Core\Framework\DataAbstractionLayer\EntityDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Field\BoolField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\CreatedAtField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\PrimaryKey;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\Required;
use Shopware\Core\Framework\DataAbstractionLayer\Field\IdField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\IntField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\StringField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\UpdatedAtField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class BadgeDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_plugin_badge';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    public function getEntityClass(): string
    {
        return BadgeEntity::class;
    }

    public function getCollectionClass(): string
    {
        return BadgeCollection::class;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required(), new ApiAware()),
            (new StringField('name', 'name'))->addFlags(new Required(), new ApiAware()),
            (new StringField('color', 'color'))->addFlags(new ApiAware()),
            (new StringField('icon', 'icon'))->addFlags(new ApiAware()),
            (new IntField('priority', 'priority'))->addFlags(new ApiAware()),
            (new BoolField('active', 'active'))->addFlags(new ApiAware()),
            new CreatedAtField(),
            new UpdatedAtField(),
        ]);
    }
}

// Good: Entity class
namespace MyPlugin\Core\Content\Badge;

use Shopware\Core\Framework\DataAbstractionLayer\Entity;
use Shopware\Core\Framework\DataAbstractionLayer\EntityIdTrait;

class BadgeEntity extends Entity
{
    use EntityIdTrait;

    protected string $name;
    protected ?string $color = null;
    protected ?string $icon = null;
    protected int $priority = 0;
    protected bool $active = true;

    public function getName(): string
    {
        return $this->name;
    }

    public function setName(string $name): void
    {
        $this->name = $name;
    }

    public function getColor(): ?string
    {
        return $this->color;
    }

    public function setColor(?string $color): void
    {
        $this->color = $color;
    }

    public function getIcon(): ?string
    {
        return $this->icon;
    }

    public function setIcon(?string $icon): void
    {
        $this->icon = $icon;
    }

    public function getPriority(): int
    {
        return $this->priority;
    }

    public function setPriority(int $priority): void
    {
        $this->priority = $priority;
    }

    public function isActive(): bool
    {
        return $this->active;
    }

    public function setActive(bool $active): void
    {
        $this->active = $active;
    }
}

// Good: Collection class
namespace MyPlugin\Core\Content\Badge;

use Shopware\Core\Framework\DataAbstractionLayer\EntityCollection;

/**
 * @method void add(BadgeEntity $entity)
 * @method void set(string $key, BadgeEntity $entity)
 * @method BadgeEntity[] getIterator()
 * @method BadgeEntity[] getElements()
 * @method BadgeEntity|null get(string $key)
 * @method BadgeEntity|null first()
 * @method BadgeEntity|null last()
 */
class BadgeCollection extends EntityCollection
{
    protected function getExpectedClass(): string
    {
        return BadgeEntity::class;
    }
}

// Good: Entity with foreign key and association
namespace MyPlugin\Core\Content\ProductBadge;

use MyPlugin\Core\Content\Badge\BadgeDefinition;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\EntityDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Field\FkField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\PrimaryKey;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\Required;
use Shopware\Core\Framework\DataAbstractionLayer\Field\IdField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\ManyToOneAssociationField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\ReferenceVersionField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class ProductBadgeDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_plugin_product_badge';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required(), new ApiAware()),

            (new FkField('product_id', 'productId', ProductDefinition::class))->addFlags(new Required(), new ApiAware()),
            (new ReferenceVersionField(ProductDefinition::class))->addFlags(new Required(), new ApiAware()),

            (new FkField('badge_id', 'badgeId', BadgeDefinition::class))->addFlags(new Required(), new ApiAware()),

            (new ManyToOneAssociationField('product', 'product_id', ProductDefinition::class, 'id', false))
                ->addFlags(new ApiAware()),

            (new ManyToOneAssociationField('badge', 'badge_id', BadgeDefinition::class, 'id', false))
                ->addFlags(new ApiAware()),
        ]);
    }
}

// Good: Translatable entity with translation definition
namespace MyPlugin\Core\Content\Banner;

use MyPlugin\Core\Content\Banner\Aggregate\BannerTranslation\BannerTranslationDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\EntityDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Field\BoolField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\PrimaryKey;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\Required;
use Shopware\Core\Framework\DataAbstractionLayer\Field\IdField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\TranslatedField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\TranslationsAssociationField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class BannerDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_plugin_banner';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    public function getEntityClass(): string
    {
        return BannerEntity::class;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required(), new ApiAware()),
            (new BoolField('active', 'active'))->addFlags(new ApiAware()),

            // Translated fields - values come from translation table
            (new TranslatedField('title'))->addFlags(new ApiAware()),
            (new TranslatedField('description'))->addFlags(new ApiAware()),
            (new TranslatedField('buttonText'))->addFlags(new ApiAware()),

            // Association to translations
            (new TranslationsAssociationField(BannerTranslationDefinition::class, 'my_plugin_banner_id'))
                ->addFlags(new ApiAware(), new Required()),
        ]);
    }
}

// Good: Translation definition
namespace MyPlugin\Core\Content\Banner\Aggregate\BannerTranslation;

use MyPlugin\Core\Content\Banner\BannerDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\EntityTranslationDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\Required;
use Shopware\Core\Framework\DataAbstractionLayer\Field\LongTextField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\StringField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class BannerTranslationDefinition extends EntityTranslationDefinition
{
    public const ENTITY_NAME = 'my_plugin_banner_translation';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    public function getParentDefinitionClass(): string
    {
        return BannerDefinition::class;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new StringField('title', 'title'))->addFlags(new Required(), new ApiAware()),
            (new LongTextField('description', 'description'))->addFlags(new ApiAware()),
            (new StringField('button_text', 'buttonText'))->addFlags(new ApiAware()),
        ]);
    }
}

// Good: Service registration in services.xml
/*
<service id="MyPlugin\Core\Content\Badge\BadgeDefinition">
    <tag name="shopware.entity.definition" entity="my_plugin_badge"/>
</service>

<service id="MyPlugin\Core\Content\Banner\BannerDefinition">
    <tag name="shopware.entity.definition" entity="my_plugin_banner"/>
</service>

<service id="MyPlugin\Core\Content\Banner\Aggregate\BannerTranslation\BannerTranslationDefinition">
    <tag name="shopware.entity.definition" entity="my_plugin_banner_translation"/>
</service>
*/

// Good: Migration for custom entity
namespace MyPlugin\Migration;

use Doctrine\DBAL\Connection;
use Shopware\Core\Framework\Migration\MigrationStep;

class Migration1234567890CreateBadgeTable extends MigrationStep
{
    public function getCreationTimestamp(): int
    {
        return 1234567890;
    }

    public function update(Connection $connection): void
    {
        $connection->executeStatement('
            CREATE TABLE IF NOT EXISTS `my_plugin_badge` (
                `id` BINARY(16) NOT NULL,
                `name` VARCHAR(255) NOT NULL,
                `color` VARCHAR(7) NULL,
                `icon` VARCHAR(255) NULL,
                `priority` INT NOT NULL DEFAULT 0,
                `active` TINYINT(1) NOT NULL DEFAULT 1,
                `created_at` DATETIME(3) NOT NULL,
                `updated_at` DATETIME(3) NULL,
                PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        ');
    }

    public function updateDestructive(Connection $connection): void
    {
        // Intentionally empty
    }
}
```
