---
title: Snippets & Entity Translations
impact: HIGH
impactDescription: proper internationalization for multi-language shops
tags: translation, snippet, i18n, language, localization
---

## Snippets & Entity Translations

**Impact: HIGH (proper internationalization for multi-language shops)**

Use Shopware's snippet system for UI translations and entity translations for data. Never hardcode translatable strings.

**Incorrect (hardcoded strings):**

```php
// Bad: Hardcoded English string
throw new \Exception('Product not found');

// Bad: Hardcoded error message in template
$this->addFlash('error', 'The product could not be saved.');
```

```twig
{# Bad: Hardcoded text #}
<button>Add to Cart</button>
<p>No products found</p>
```

**Correct snippet files:**

```json
// Resources/snippet/de_DE/storefront.de-DE.json
{
    "myPlugin": {
        "general": {
            "title": "Mein Plugin",
            "description": "Beschreibung des Plugins"
        },
        "product": {
            "syncButton": "Produkt synchronisieren",
            "syncSuccess": "Produkt wurde erfolgreich synchronisiert.",
            "syncFailed": "Synchronisierung fehlgeschlagen: %reason%",
            "notFound": "Produkt nicht gefunden"
        },
        "checkout": {
            "deliveryEstimate": "Voraussichtliche Lieferung: %date%",
            "stockWarning": "Nur noch %count% auf Lager"
        },
        "form": {
            "labelName": "Name",
            "labelEmail": "E-Mail-Adresse",
            "placeholderSearch": "Suchen...",
            "submitButton": "Absenden"
        },
        "messages": {
            "success": "Erfolgreich gespeichert!",
            "error": "Ein Fehler ist aufgetreten.",
            "confirmDelete": "Möchten Sie diesen Eintrag wirklich löschen?"
        }
    }
}
```

```json
// Resources/snippet/en_GB/storefront.en-GB.json
{
    "myPlugin": {
        "general": {
            "title": "My Plugin",
            "description": "Plugin description"
        },
        "product": {
            "syncButton": "Sync Product",
            "syncSuccess": "Product synced successfully.",
            "syncFailed": "Sync failed: %reason%",
            "notFound": "Product not found"
        },
        "checkout": {
            "deliveryEstimate": "Estimated delivery: %date%",
            "stockWarning": "Only %count% left in stock"
        },
        "form": {
            "labelName": "Name",
            "labelEmail": "Email Address",
            "placeholderSearch": "Search...",
            "submitButton": "Submit"
        },
        "messages": {
            "success": "Saved successfully!",
            "error": "An error occurred.",
            "confirmDelete": "Are you sure you want to delete this item?"
        }
    }
}
```

**Correct usage in Twig templates:**

```twig
{# Simple translation #}
<h1>{{ "myPlugin.general.title"|trans }}</h1>

{# Translation with parameters #}
<p>{{ "myPlugin.checkout.deliveryEstimate"|trans({'%date%': deliveryDate|date('d.m.Y')}) }}</p>

{# Pluralization #}
<p>{{ "myPlugin.checkout.stockWarning"|trans({'%count%': product.stock}) }}</p>

{# Translation in attribute #}
<input type="text" placeholder="{{ 'myPlugin.form.placeholderSearch'|trans }}">

{# Conditional with translation #}
{% if product.stock < 5 %}
    <span class="badge badge-warning">
        {{ "myPlugin.checkout.stockWarning"|trans({'%count%': product.stock}) }}
    </span>
{% endif %}
```

**Correct usage in PHP:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Storefront\Controller;

use Symfony\Contracts\Translation\TranslatorInterface;

class MyPluginController extends StorefrontController
{
    public function __construct(
        private readonly TranslatorInterface $translator
    ) {}

    public function syncAction(SalesChannelContext $context): Response
    {
        try {
            $this->syncService->sync();

            $this->addFlash(
                self::SUCCESS,
                $this->trans('myPlugin.product.syncSuccess')
            );

        } catch (SyncException $e) {
            $this->addFlash(
                self::DANGER,
                $this->trans('myPlugin.product.syncFailed', [
                    '%reason%' => $e->getMessage()
                ])
            );
        }

        return $this->redirectToRoute('frontend.my-plugin.list');
    }

    // Using translator service directly
    public function getMessage(): string
    {
        return $this->translator->trans('myPlugin.general.title');
    }
}
```

**Correct entity translations:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Content\MyEntity;

use Shopware\Core\Framework\DataAbstractionLayer\EntityDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Field\TranslatedField;
use Shopware\Core\Framework\DataAbstractionLayer\Field\TranslationsAssociationField;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class MyEntityDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'my_plugin_entity';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new PrimaryKey(), new Required()),

            // Non-translated fields
            (new StringField('technical_name', 'technicalName'))->addFlags(new Required()),
            (new BoolField('active', 'active')),

            // Translated fields
            (new TranslatedField('name')),
            (new TranslatedField('description')),
            (new TranslatedField('customData')),

            // Translation association
            (new TranslationsAssociationField(MyEntityTranslationDefinition::class, 'my_plugin_entity_id'))
        ]);
    }
}
```

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Content\MyEntity;

use Shopware\Core\Framework\DataAbstractionLayer\EntityTranslationDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\FieldCollection;

class MyEntityTranslationDefinition extends EntityTranslationDefinition
{
    public function getEntityName(): string
    {
        return 'my_plugin_entity_translation';
    }

    public function getParentDefinitionClass(): string
    {
        return MyEntityDefinition::class;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new StringField('name', 'name'))->addFlags(new Required()),
            (new LongTextField('description', 'description')),
            (new JsonField('custom_data', 'customData'))
        ]);
    }
}
```

**Creating entities with translations:**

```php
public function createEntity(array $data, Context $context): string
{
    $id = Uuid::randomHex();

    $this->repository->create([
        [
            'id' => $id,
            'technicalName' => $data['technicalName'],
            'active' => true,
            // Translations
            'translations' => [
                'de-DE' => [
                    'name' => $data['name_de'],
                    'description' => $data['description_de']
                ],
                'en-GB' => [
                    'name' => $data['name_en'],
                    'description' => $data['description_en']
                ]
            ]
        ]
    ], $context);

    return $id;
}
```

**Reading translated entities:**

```php
public function getEntity(string $id, Context $context): ?MyEntityEntity
{
    $criteria = new Criteria([$id]);

    // Entity is automatically returned in context language
    // Fallback to system language if translation missing
    return $this->repository->search($criteria, $context)->first();
}

// Access translation in different language
public function getEntityInLanguage(string $id, string $languageId, Context $context): ?MyEntityEntity
{
    // Create context with specific language
    $languageContext = new Context(
        $context->getSource(),
        $context->getRuleIds(),
        $context->getCurrencyId(),
        [$languageId, $context->getLanguageId()], // Language chain
        $context->getVersionId()
    );

    return $this->repository->search(new Criteria([$id]), $languageContext)->first();
}
```

Reference: [Snippets](https://developer.shopware.com/docs/guides/plugins/plugins/storefront/add-translations.html)
