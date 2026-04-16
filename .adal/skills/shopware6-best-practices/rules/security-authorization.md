---
title: Implement Proper Authorization with ACL
impact: CRITICAL
impactDescription: prevents privilege escalation and unauthorized operations
tags: security, authorization, acl, permissions, roles
---

## Implement Proper Authorization with ACL

**Impact: CRITICAL (prevents privilege escalation and unauthorized operations)**

Shopware 6 uses Access Control Lists (ACL) to manage permissions. Every admin action must verify the user has appropriate privileges. Never rely solely on authentication - always check authorization for sensitive operations.

**Incorrect (missing permission checks):**

```php
// Bad: No permission check - any authenticated admin can delete products
#[Route(defaults: ['_routeScope' => ['api']])]
class ProductAdminController extends AbstractController
{
    #[Route(path: '/api/product/{id}', name: 'api.product.delete', methods: ['DELETE'])]
    public function deleteProduct(string $id, Context $context): Response
    {
        // Bad: No ACL check - anyone with API access can delete
        $this->productRepository->delete([['id' => $id]], $context);
        return new JsonResponse(['success' => true]);
    }
}
```

```php
// Bad: Hardcoded access checks instead of using ACL
class OrderService
{
    public function cancelOrder(string $orderId, Context $context): void
    {
        // Bad: Hardcoded user ID check instead of proper ACL
        $source = $context->getSource();
        if ($source instanceof AdminApiSource) {
            $userId = $source->getUserId();
            if ($userId !== 'some-admin-uuid') {
                throw new AccessDeniedException();
            }
        }

        $this->orderRepository->update([
            ['id' => $orderId, 'stateId' => $this->getCancelledStateId()]
        ], $context);
    }
}
```

```php
// Bad: Not defining ACL for custom entities
class CustomEntityDefinition extends EntityDefinition
{
    // Bad: No getDefaults() with ACL configuration
    // Any admin can read/write this entity
}
```

**Correct (using ACL properly):**

```php
// Good: Route with ACL annotation
use Shopware\Core\Framework\Routing\Annotation\Acl;

#[Route(defaults: ['_routeScope' => ['api']])]
class ProductAdminController extends AbstractController
{
    public function __construct(
        private readonly EntityRepository $productRepository
    ) {
    }

    #[Route(path: '/api/_action/product/bulk-delete', name: 'api.action.product.bulk-delete', methods: ['POST'])]
    #[Acl(['product.deleter'])]
    public function bulkDeleteProducts(RequestDataBag $data, Context $context): Response
    {
        // Good: ACL annotation ensures only users with 'product.deleter' can access
        $ids = $data->get('ids')->all();

        $deleteData = array_map(fn(string $id) => ['id' => $id], $ids);
        $this->productRepository->delete($deleteData, $context);

        return new JsonResponse(['success' => true, 'deleted' => count($ids)]);
    }

    #[Route(path: '/api/_action/product/update-prices', name: 'api.action.product.update-prices', methods: ['POST'])]
    #[Acl(['product.editor'])]
    public function updatePrices(RequestDataBag $data, Context $context): Response
    {
        // Good: Separate ACL permission for price updates
        // Implementation here
        return new JsonResponse(['success' => true]);
    }
}
```

```php
// Good: Checking permissions programmatically in services
use Shopware\Core\Framework\Api\Acl\AclCriteriaValidator;
use Shopware\Core\Framework\Api\Context\AdminApiSource;

class OrderService
{
    public function __construct(
        private readonly EntityRepository $orderRepository
    ) {
    }

    public function cancelOrder(string $orderId, Context $context): void
    {
        // Good: Programmatic ACL check
        $this->validatePermission($context, 'order.editor');

        $this->orderRepository->update([
            ['id' => $orderId, 'stateId' => $this->getCancelledStateId()]
        ], $context);
    }

    public function deleteOrder(string $orderId, Context $context): void
    {
        // Good: Check for delete permission
        $this->validatePermission($context, 'order.deleter');

        $this->orderRepository->delete([['id' => $orderId]], $context);
    }

    private function validatePermission(Context $context, string $privilege): void
    {
        $source = $context->getSource();

        if (!$source instanceof AdminApiSource) {
            throw new AccessDeniedException('Admin access required');
        }

        // Good: Check if the admin user has the required privilege
        if (!$source->isAllowed($privilege)) {
            throw new AccessDeniedException(sprintf('Missing privilege: %s', $privilege));
        }
    }
}
```

```php
// Good: Defining ACL for custom entities
use Shopware\Core\Framework\DataAbstractionLayer\EntityDefinition;
use Shopware\Core\Framework\DataAbstractionLayer\Field\Flag\ApiAware;

class CustomEntityDefinition extends EntityDefinition
{
    public const ENTITY_NAME = 'custom_entity';

    public function getEntityName(): string
    {
        return self::ENTITY_NAME;
    }

    protected function defineFields(): FieldCollection
    {
        return new FieldCollection([
            (new IdField('id', 'id'))->addFlags(new Required(), new PrimaryKey()),
            (new StringField('name', 'name'))->addFlags(new Required(), new ApiAware()),
        ]);
    }

    // Good: Define default privileges for this entity
    public function getDefaults(): array
    {
        return [
            // Define which roles can access this entity by default
        ];
    }
}
```

```php
// Good: Register custom ACL privileges in plugin
use Shopware\Core\Framework\Plugin;
use Shopware\Core\Framework\Plugin\Context\InstallContext;

class MyPlugin extends Plugin
{
    public function enrichPrivileges(): array
    {
        // Good: Define custom ACL privileges
        return [
            'product.viewer' => [
                'my_custom_entity:read',
            ],
            'product.editor' => [
                'my_custom_entity:read',
                'my_custom_entity:update',
            ],
            'product.creator' => [
                'my_custom_entity:read',
                'my_custom_entity:create',
            ],
            'product.deleter' => [
                'my_custom_entity:read',
                'my_custom_entity:delete',
            ],
        ];
    }
}
```

```php
// Good: Custom ACL role registration via migration
use Shopware\Core\Framework\Migration\MigrationStep;
use Doctrine\DBAL\Connection;

class Migration1234567890AddCustomRole extends MigrationStep
{
    public function update(Connection $connection): void
    {
        // Good: Create custom role with specific privileges
        $roleId = Uuid::randomBytes();

        $connection->insert('acl_role', [
            'id' => $roleId,
            'name' => 'Custom Order Manager',
            'privileges' => json_encode([
                'order:read',
                'order:update',
                'order_customer:read',
                'order_line_item:read',
                // Custom privileges
                'custom_order_export:read',
                'custom_order_export:create',
            ]),
            'created_at' => (new \DateTime())->format(Defaults::STORAGE_DATE_TIME_FORMAT),
        ]);
    }
}
```

**Standard ACL privilege patterns:**

| Privilege | Format | Example |
|-----------|--------|---------|
| Read | `entity:read` | `product:read` |
| Create | `entity:create` | `product:create` |
| Update | `entity:update` | `product:update` |
| Delete | `entity:delete` | `product:delete` |
| Viewer role | `entity.viewer` | `product.viewer` |
| Editor role | `entity.editor` | `product.editor` |
| Creator role | `entity.creator` | `product.creator` |
| Deleter role | `entity.deleter` | `product.deleter` |

Reference: [ACL System](https://developer.shopware.com/docs/guides/plugins/plugins/administration/add-acl-rules) | [Custom Privileges](https://developer.shopware.com/docs/guides/plugins/plugins/framework/custom-module/add-acl-rules)
