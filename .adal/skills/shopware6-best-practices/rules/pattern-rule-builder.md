---
title: Rule Builder Conditions
impact: MEDIUM
impactDescription: dynamic conditions for pricing, shipping, and content
tags: rule, condition, builder, dynamic, pricing
---

## Rule Builder Conditions

**Impact: MEDIUM (dynamic conditions for pricing, shipping, and content)**

The Rule Builder enables dynamic conditions for pricing, promotions, shipping methods, and content. Create custom conditions to extend rule capabilities.

**Correct custom rule condition:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Rule;

use Shopware\Core\Framework\Rule\Rule;
use Shopware\Core\Framework\Rule\RuleComparison;
use Shopware\Core\Framework\Rule\RuleConfig;
use Shopware\Core\Framework\Rule\RuleConstraints;
use Shopware\Core\Framework\Rule\RuleScope;
use Shopware\Core\Checkout\Cart\Rule\CartRuleScope;

class CustomerTierRule extends Rule
{
    public const RULE_NAME = 'customerTier';

    protected string $operator = Rule::OPERATOR_EQ;
    protected ?string $tier = null;

    public function getName(): string
    {
        return self::RULE_NAME;
    }

    public function match(RuleScope $scope): bool
    {
        if (!$scope instanceof CartRuleScope) {
            return false;
        }

        $customer = $scope->getSalesChannelContext()->getCustomer();

        if (!$customer) {
            return RuleComparison::isNegativeOperator($this->operator);
        }

        $customerTier = $customer->getCustomFields()['my_plugin_tier'] ?? null;

        return RuleComparison::string($customerTier, $this->tier, $this->operator);
    }

    public function getConstraints(): array
    {
        return [
            'operator' => RuleConstraints::stringOperators(false),
            'tier' => RuleConstraints::string()
        ];
    }

    public function getConfig(): RuleConfig
    {
        return (new RuleConfig())
            ->operatorSet(RuleConfig::OPERATOR_SET_STRING)
            ->selectField('tier', [
                ['value' => 'bronze', 'label' => ['en-GB' => 'Bronze', 'de-DE' => 'Bronze']],
                ['value' => 'silver', 'label' => ['en-GB' => 'Silver', 'de-DE' => 'Silber']],
                ['value' => 'gold', 'label' => ['en-GB' => 'Gold', 'de-DE' => 'Gold']],
                ['value' => 'platinum', 'label' => ['en-GB' => 'Platinum', 'de-DE' => 'Platin']]
            ]);
    }
}
```

**Correct cart item condition:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Rule;

use Shopware\Core\Checkout\Cart\LineItem\LineItem;
use Shopware\Core\Checkout\Cart\Rule\CartRuleScope;
use Shopware\Core\Checkout\Cart\Rule\LineItemScope;
use Shopware\Core\Framework\Rule\Rule;
use Shopware\Core\Framework\Rule\RuleComparison;
use Shopware\Core\Framework\Rule\RuleConfig;
use Shopware\Core\Framework\Rule\RuleConstraints;
use Shopware\Core\Framework\Rule\RuleScope;

class ProductCustomFieldRule extends Rule
{
    public const RULE_NAME = 'productCustomField';

    protected string $operator = Rule::OPERATOR_EQ;
    protected ?string $fieldName = null;
    protected ?string $fieldValue = null;

    public function getName(): string
    {
        return self::RULE_NAME;
    }

    public function match(RuleScope $scope): bool
    {
        if ($scope instanceof LineItemScope) {
            return $this->matchLineItem($scope->getLineItem());
        }

        if ($scope instanceof CartRuleScope) {
            return $this->matchCart($scope);
        }

        return false;
    }

    private function matchLineItem(LineItem $lineItem): bool
    {
        $payload = $lineItem->getPayloadValue('customFields') ?? [];
        $value = $payload[$this->fieldName] ?? null;

        return RuleComparison::string($value, $this->fieldValue, $this->operator);
    }

    private function matchCart(CartRuleScope $scope): bool
    {
        foreach ($scope->getCart()->getLineItems()->filterType(LineItem::PRODUCT_LINE_ITEM_TYPE) as $lineItem) {
            if ($this->matchLineItem($lineItem)) {
                return true;
            }
        }

        return false;
    }

    public function getConstraints(): array
    {
        return [
            'operator' => RuleConstraints::stringOperators(false),
            'fieldName' => RuleConstraints::string(),
            'fieldValue' => RuleConstraints::string()
        ];
    }

    public function getConfig(): RuleConfig
    {
        return (new RuleConfig())
            ->operatorSet(RuleConfig::OPERATOR_SET_STRING)
            ->stringField('fieldName')
            ->stringField('fieldValue');
    }
}
```

**Correct date-based condition:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Core\Rule;

use Shopware\Core\Framework\Rule\Rule;
use Shopware\Core\Framework\Rule\RuleConfig;
use Shopware\Core\Framework\Rule\RuleConstraints;
use Shopware\Core\Framework\Rule\RuleScope;

class CustomerRegistrationAgeRule extends Rule
{
    public const RULE_NAME = 'customerRegistrationAge';

    protected string $operator = Rule::OPERATOR_GTE;
    protected int $days = 0;

    public function getName(): string
    {
        return self::RULE_NAME;
    }

    public function match(RuleScope $scope): bool
    {
        $customer = $scope->getSalesChannelContext()->getCustomer();

        if (!$customer) {
            return false;
        }

        $registrationDate = $customer->getCreatedAt();

        if (!$registrationDate) {
            return false;
        }

        $daysSinceRegistration = (int) $registrationDate->diff(new \DateTime())->days;

        return match ($this->operator) {
            Rule::OPERATOR_EQ => $daysSinceRegistration === $this->days,
            Rule::OPERATOR_NEQ => $daysSinceRegistration !== $this->days,
            Rule::OPERATOR_LTE => $daysSinceRegistration <= $this->days,
            Rule::OPERATOR_GTE => $daysSinceRegistration >= $this->days,
            Rule::OPERATOR_LT => $daysSinceRegistration < $this->days,
            Rule::OPERATOR_GT => $daysSinceRegistration > $this->days,
            default => false
        };
    }

    public function getConstraints(): array
    {
        return [
            'operator' => RuleConstraints::numericOperators(false),
            'days' => RuleConstraints::int()
        ];
    }

    public function getConfig(): RuleConfig
    {
        return (new RuleConfig())
            ->operatorSet(RuleConfig::OPERATOR_SET_NUMBER)
            ->intField('days');
    }
}
```

**Service registration:**

```xml
<!-- services.xml -->
<service id="MyVendor\MyPlugin\Core\Rule\CustomerTierRule">
    <tag name="shopware.rule.definition"/>
</service>

<service id="MyVendor\MyPlugin\Core\Rule\ProductCustomFieldRule">
    <tag name="shopware.rule.definition"/>
</service>

<service id="MyVendor\MyPlugin\Core\Rule\CustomerRegistrationAgeRule">
    <tag name="shopware.rule.definition"/>
</service>
```

**Using rules programmatically:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class RuleBasedService
{
    public function __construct(
        private readonly EntityRepository $ruleRepository,
        private readonly RuleConditionRegistry $conditionRegistry
    ) {}

    public function createRule(Context $context): string
    {
        $ruleId = Uuid::randomHex();

        $this->ruleRepository->create([
            [
                'id' => $ruleId,
                'name' => 'VIP Customer Rule',
                'priority' => 100,
                'conditions' => [
                    [
                        'id' => Uuid::randomHex(),
                        'type' => 'andContainer',
                        'children' => [
                            [
                                'id' => Uuid::randomHex(),
                                'type' => 'customerTier',
                                'value' => [
                                    'operator' => '=',
                                    'tier' => 'gold'
                                ]
                            ],
                            [
                                'id' => Uuid::randomHex(),
                                'type' => 'customerRegistrationAge',
                                'value' => [
                                    'operator' => '>=',
                                    'days' => 365
                                ]
                            ]
                        ]
                    ]
                ]
            ]
        ], $context);

        return $ruleId;
    }

    public function evaluateRule(string $ruleId, RuleScope $scope, Context $context): bool
    {
        $criteria = new Criteria([$ruleId]);
        $criteria->addAssociation('conditions');

        $rule = $this->ruleRepository->search($criteria, $context)->first();

        if (!$rule) {
            return false;
        }

        // Use RuleConditionRegistry to evaluate
        return $this->evaluateConditions($rule->getConditions(), $scope);
    }
}
```

**Available rule config field types:**

| Method | Description |
|--------|-------------|
| `stringField()` | Text input |
| `intField()` | Integer input |
| `floatField()` | Decimal input |
| `boolField()` | Boolean switch |
| `selectField()` | Dropdown |
| `multiSelectField()` | Multi-select |
| `entitySelectField()` | Entity picker |

Reference: [Custom Rules](https://developer.shopware.com/docs/guides/plugins/plugins/framework/rule/add-custom-rules.html)
