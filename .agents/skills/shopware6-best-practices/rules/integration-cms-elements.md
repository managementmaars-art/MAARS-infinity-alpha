---
title: CMS Elements & Blocks
impact: HIGH
impactDescription: reusable content elements for shopping experiences
tags: cms, content, block, element, shopping-experiences
---

## CMS Elements & Blocks

**Impact: HIGH (reusable content elements for shopping experiences)**

CMS elements are the building blocks for Shopping Experiences. Create custom elements with proper configuration, data resolving, and storefront rendering.

**Incorrect (element without proper structure):**

```php
// Bad: Missing data resolver, incomplete element
class MyCmsElement
{
    public function render(): string
    {
        return '<div>My Element</div>';
    }
}
```

**Correct CMS element structure:**

```
src/
├── Core/
│   └── Content/
│       └── Cms/
│           ├── MyProductSliderCmsElementResolver.php
│           └── DataResolver/
│               └── MyProductSliderCmsElementResolver.php
└── Resources/
    ├── config/
    │   └── cms.xml
    ├── views/
    │   └── storefront/
    │       └── element/
    │           └── cms-element-my-product-slider.html.twig
    └── app/
        └── administration/
            └── src/
                └── module/
                    └── sw-cms/
                        └── elements/
                            └── my-product-slider/
                                ├── index.js
                                ├── component/
                                │   ├── index.js
                                │   └── sw-cms-el-my-product-slider.html.twig
                                ├── config/
                                │   ├── index.js
                                │   └── sw-cms-el-config-my-product-slider.html.twig
                                └── preview/
                                    ├── index.js
                                    └── sw-cms-el-preview-my-product-slider.html.twig
```

**Correct CMS element registration (cms.xml):**

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<cms xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:noNamespaceSchemaLocation="https://raw.githubusercontent.com/shopware/shopware/trunk/src/Core/Framework/Resources/config/cms.xsd">

    <blocks>
        <block>
            <name>my-product-slider</name>
            <category>commerce</category>
            <label>My Product Slider</label>
            <label lang="de-DE">Mein Produkt-Slider</label>

            <slots>
                <slot name="productSlider" type="my-product-slider"/>
            </slots>

            <defaultConfig>
                <marginTop>20px</marginTop>
                <marginBottom>20px</marginBottom>
                <marginLeft>0</marginLeft>
                <marginRight>0</marginRight>
            </defaultConfig>
        </block>
    </blocks>

    <elements>
        <element>
            <name>my-product-slider</name>
            <label>Product Slider</label>
            <label lang="de-DE">Produkt-Slider</label>
            <component>sw-cms-el-my-product-slider</component>
            <previewComponent>sw-cms-el-preview-my-product-slider</previewComponent>
            <configComponent>sw-cms-el-config-my-product-slider</configComponent>
            <defaultConfig>
                <products>[]</products>
                <displayMode>standard</displayMode>
                <slidesPerView>4</slidesPerView>
                <autoplay>true</autoplay>
            </defaultConfig>
        </element>
    </elements>
</cms>
```

**Correct data resolver:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Content\Cms\DataResolver;

use Shopware\Core\Content\Cms\Aggregate\CmsSlot\CmsSlotEntity;
use Shopware\Core\Content\Cms\DataResolver\CriteriaCollection;
use Shopware\Core\Content\Cms\DataResolver\Element\AbstractCmsElementResolver;
use Shopware\Core\Content\Cms\DataResolver\Element\ElementDataCollection;
use Shopware\Core\Content\Cms\DataResolver\ResolverContext\ResolverContext;
use Shopware\Core\Content\Product\ProductDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Search\Criteria;

class MyProductSliderCmsElementResolver extends AbstractCmsElementResolver
{
    public function getType(): string
    {
        return 'my-product-slider';
    }

    public function collect(CmsSlotEntity $slot, ResolverContext $resolverContext): ?CriteriaCollection
    {
        $config = $slot->getFieldConfig();
        $productIds = $config->get('products')?->getArrayValue() ?? [];

        if (empty($productIds)) {
            return null;
        }

        $criteria = new Criteria($productIds);
        $criteria->addAssociation('cover');
        $criteria->addAssociation('manufacturer');

        $criteriaCollection = new CriteriaCollection();
        $criteriaCollection->add(
            'my_slider_products_' . $slot->getUniqueIdentifier(),
            ProductDefinition::class,
            $criteria
        );

        return $criteriaCollection;
    }

    public function enrich(CmsSlotEntity $slot, ResolverContext $resolverContext, ElementDataCollection $result): void
    {
        $config = $slot->getFieldConfig();
        $productIds = $config->get('products')?->getArrayValue() ?? [];

        $sliderData = new MyProductSliderStruct();

        if (!empty($productIds)) {
            $searchResult = $result->get('my_slider_products_' . $slot->getUniqueIdentifier());

            if ($searchResult) {
                // Preserve order from config
                $products = [];
                foreach ($productIds as $productId) {
                    $product = $searchResult->get($productId);
                    if ($product) {
                        $products[] = $product;
                    }
                }
                $sliderData->setProducts($products);
            }
        }

        // Add config values to struct
        $sliderData->setDisplayMode($config->get('displayMode')?->getStringValue() ?? 'standard');
        $sliderData->setSlidesPerView((int) ($config->get('slidesPerView')?->getValue() ?? 4));
        $sliderData->setAutoplay((bool) ($config->get('autoplay')?->getValue() ?? true));

        $slot->setData($sliderData);
    }
}
```

**Correct data struct:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Content\Cms;

use Shopware\Core\Framework\Struct\Struct;

class MyProductSliderStruct extends Struct
{
    protected array $products = [];
    protected string $displayMode = 'standard';
    protected int $slidesPerView = 4;
    protected bool $autoplay = true;

    public function getProducts(): array
    {
        return $this->products;
    }

    public function setProducts(array $products): void
    {
        $this->products = $products;
    }

    public function getDisplayMode(): string
    {
        return $this->displayMode;
    }

    public function setDisplayMode(string $displayMode): void
    {
        $this->displayMode = $displayMode;
    }

    public function getSlidesPerView(): int
    {
        return $this->slidesPerView;
    }

    public function setSlidesPerView(int $slidesPerView): void
    {
        $this->slidesPerView = $slidesPerView;
    }

    public function getAutoplay(): bool
    {
        return $this->autoplay;
    }

    public function setAutoplay(bool $autoplay): void
    {
        $this->autoplay = $autoplay;
    }
}
```

**Correct storefront template:**

```twig
{# Resources/views/storefront/element/cms-element-my-product-slider.html.twig #}

{% block element_my_product_slider %}
    {% set config = element.fieldConfig.elements %}
    {% set sliderData = element.data %}

    <div class="cms-element-my-product-slider"
         data-my-product-slider="true"
         data-my-product-slider-options='{{ {
             "slidesPerView": sliderData.slidesPerView,
             "autoplay": sliderData.autoplay,
             "breakpoints": {
                 "768": { "slidesPerView": 2 },
                 "992": { "slidesPerView": 3 },
                 "1200": { "slidesPerView": sliderData.slidesPerView }
             }
         }|json_encode }}'>

        {% block element_my_product_slider_inner %}
            <div class="product-slider-container swiper">
                <div class="swiper-wrapper">
                    {% for product in sliderData.products %}
                        <div class="swiper-slide">
                            {% sw_include '@Storefront/storefront/component/product/card/box.html.twig' with {
                                'product': product,
                                'layout': sliderData.displayMode,
                                'displayMode': 'cover'
                            } %}
                        </div>
                    {% endfor %}
                </div>

                <div class="swiper-button-prev"></div>
                <div class="swiper-button-next"></div>
                <div class="swiper-pagination"></div>
            </div>
        {% endblock %}
    </div>
{% endblock %}
```

**Correct admin element component:**

```javascript
// administration/src/module/sw-cms/elements/my-product-slider/index.js
import './component';
import './config';
import './preview';

Shopware.Service('cmsService').registerCmsElement({
    name: 'my-product-slider',
    label: 'my-plugin.elements.productSlider.label',
    component: 'sw-cms-el-my-product-slider',
    configComponent: 'sw-cms-el-config-my-product-slider',
    previewComponent: 'sw-cms-el-preview-my-product-slider',
    defaultConfig: {
        products: {
            source: 'static',
            value: [],
            required: true,
            entity: {
                name: 'product'
            }
        },
        displayMode: {
            source: 'static',
            value: 'standard'
        },
        slidesPerView: {
            source: 'static',
            value: 4
        },
        autoplay: {
            source: 'static',
            value: true
        }
    }
});
```

**Service registration:**

```xml
<service id="MyVendor\MyPlugin\Core\Content\Cms\DataResolver\MyProductSliderCmsElementResolver">
    <tag name="shopware.cms.data_resolver"/>
</service>
```

Reference: [CMS Elements](https://developer.shopware.com/docs/guides/plugins/plugins/content/cms/add-cms-element.html)
