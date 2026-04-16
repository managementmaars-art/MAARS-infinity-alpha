---
title: B2B Features & Company Handling
impact: MEDIUM
impactDescription: proper B2B customer and company structure handling
tags: b2b, company, customer, roles, permissions
---

## B2B Features & Company Handling

**Impact: MEDIUM (proper B2B customer and company structure handling)**

Shopware 6 B2B features require proper handling of company structures, employee roles, budgets, and approval workflows. Implement B2B-aware logic in plugins.

**Incorrect (ignoring B2B context):**

```php
// Bad: Not checking if customer is B2B
public function getCustomerPrice(CustomerEntity $customer): float
{
    return $this->basePrice; // Same price for everyone
}

// Bad: Not respecting company permissions
public function placeOrder(OrderEntity $order): void
{
    // No budget or approval check
    $this->orderService->create($order);
}
```

**Correct B2B-aware service:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

use Shopware\Commercial\B2B\BudgetLimits\Domain\BudgetService;
use Shopware\Commercial\B2B\EmployeeManagement\Domain\EmployeeEntity;
use Shopware\Core\Checkout\Customer\CustomerEntity;
use Shopware\Core\System\SalesChannel\SalesChannelContext;

class B2BOrderService
{
    public function __construct(
        private readonly EntityRepository $customerRepository,
        private readonly ?BudgetService $budgetService,
        private readonly EntityRepository $orderRepository
    ) {}

    public function canPlaceOrder(
        SalesChannelContext $context,
        float $orderTotal
    ): B2BOrderPermission {
        $customer = $context->getCustomer();

        if (!$customer) {
            return B2BOrderPermission::denied('Not logged in');
        }

        // Check if B2B customer (has company)
        if (!$this->isB2BCustomer($customer)) {
            return B2BOrderPermission::allowed(); // B2C - no restrictions
        }

        // Get employee info
        $employee = $this->getEmployeeForCustomer($customer, $context->getContext());

        if (!$employee) {
            return B2BOrderPermission::denied('Employee not found');
        }

        // Check if employee can place orders
        if (!$employee->getCanPlaceOrders()) {
            return B2BOrderPermission::denied('Not authorized to place orders');
        }

        // Check budget limits
        if ($this->budgetService) {
            $budgetCheck = $this->budgetService->checkBudget(
                $employee,
                $orderTotal,
                $context->getContext()
            );

            if (!$budgetCheck->isWithinBudget()) {
                if ($budgetCheck->requiresApproval()) {
                    return B2BOrderPermission::requiresApproval(
                        'Order exceeds budget limit',
                        $budgetCheck->getApprovers()
                    );
                }

                return B2BOrderPermission::denied(
                    sprintf('Budget limit exceeded. Available: %s', $budgetCheck->getAvailable())
                );
            }
        }

        return B2BOrderPermission::allowed();
    }

    public function submitForApproval(
        string $cartToken,
        SalesChannelContext $context
    ): string {
        $customer = $context->getCustomer();
        $employee = $this->getEmployeeForCustomer($customer, $context->getContext());

        // Get approvers based on company hierarchy
        $approvers = $this->getApprovers($employee, $context->getContext());

        // Create approval request
        $approvalId = Uuid::randomHex();
        $this->approvalRepository->create([
            [
                'id' => $approvalId,
                'cartToken' => $cartToken,
                'requesterId' => $employee->getId(),
                'status' => 'pending',
                'approvers' => array_map(fn($a) => ['id' => $a->getId()], $approvers)
            ]
        ], $context->getContext());

        // Send notification to approvers
        $this->notifyApprovers($approvers, $employee, $context);

        return $approvalId;
    }

    public function isB2BCustomer(CustomerEntity $customer): bool
    {
        // Check if customer has company assignment
        $customFields = $customer->getCustomFields() ?? [];

        return isset($customFields['b2b_company_id'])
            || $customer->getCompany() !== null;
    }

    private function getEmployeeForCustomer(
        CustomerEntity $customer,
        Context $context
    ): ?EmployeeEntity {
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('customerId', $customer->getId()));
        $criteria->addAssociation('role');
        $criteria->addAssociation('company');

        return $this->employeeRepository->search($criteria, $context)->first();
    }

    private function getApprovers(EmployeeEntity $employee, Context $context): array
    {
        // Get direct supervisor
        if ($employee->getSupervisorId()) {
            $supervisor = $this->employeeRepository->search(
                new Criteria([$employee->getSupervisorId()]),
                $context
            )->first();

            if ($supervisor) {
                return [$supervisor];
            }
        }

        // Fallback to company admins
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('companyId', $employee->getCompanyId()));
        $criteria->addFilter(new EqualsFilter('role.canApproveOrders', true));

        return $this->employeeRepository->search($criteria, $context)->getElements();
    }
}
```

**Correct B2B pricing service:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class B2BPricingService
{
    public function __construct(
        private readonly EntityRepository $productRepository,
        private readonly SystemConfigService $configService
    ) {}

    public function getCustomerPrice(
        string $productId,
        SalesChannelContext $context
    ): ?CalculatedPrice {
        $customer = $context->getCustomer();

        if (!$customer) {
            return null; // Use default price
        }

        // Check for customer-specific price
        $customerPrice = $this->getCustomerSpecificPrice($productId, $customer, $context);
        if ($customerPrice) {
            return $customerPrice;
        }

        // Check for company-level pricing
        $companyPrice = $this->getCompanyPrice($productId, $customer, $context);
        if ($companyPrice) {
            return $companyPrice;
        }

        // Check for customer group pricing (standard Shopware)
        return null; // Fall back to default pricing
    }

    private function getCustomerSpecificPrice(
        string $productId,
        CustomerEntity $customer,
        SalesChannelContext $context
    ): ?CalculatedPrice {
        $customFields = $customer->getCustomFields() ?? [];
        $priceListId = $customFields['b2b_price_list_id'] ?? null;

        if (!$priceListId) {
            return null;
        }

        // Look up price in customer's assigned price list
        $criteria = new Criteria();
        $criteria->addFilter(new EqualsFilter('priceListId', $priceListId));
        $criteria->addFilter(new EqualsFilter('productId', $productId));

        $priceListItem = $this->priceListRepository->search($criteria, $context->getContext())->first();

        if (!$priceListItem) {
            return null;
        }

        return $this->calculatePrice(
            $priceListItem->getPrice(),
            $context
        );
    }

    private function getCompanyPrice(
        string $productId,
        CustomerEntity $customer,
        SalesChannelContext $context
    ): ?CalculatedPrice {
        $customFields = $customer->getCustomFields() ?? [];
        $companyId = $customFields['b2b_company_id'] ?? null;

        if (!$companyId) {
            return null;
        }

        // Get company discount tier
        $company = $this->companyRepository->search(
            new Criteria([$companyId]),
            $context->getContext()
        )->first();

        if (!$company) {
            return null;
        }

        $discountPercent = $company->getCustomFields()['discount_percent'] ?? 0;

        if ($discountPercent <= 0) {
            return null;
        }

        // Apply company discount to product price
        $product = $this->productRepository->search(
            new Criteria([$productId]),
            $context->getContext()
        )->first();

        $basePrice = $product->getCalculatedPrice()->getUnitPrice();
        $discountedPrice = $basePrice * (1 - ($discountPercent / 100));

        return $this->calculatePrice($discountedPrice, $context);
    }
}
```

**Correct company structure handling:**

```php
<?php declare(strict_types=1);

namespace MyVendor\MyPlugin\Service;

class CompanyService
{
    public function createCompanyWithAdmin(
        array $companyData,
        array $adminData,
        Context $context
    ): string {
        $companyId = Uuid::randomHex();
        $adminId = Uuid::randomHex();

        // Create company
        $this->companyRepository->create([
            [
                'id' => $companyId,
                'name' => $companyData['name'],
                'email' => $companyData['email'],
                'vatId' => $companyData['vatId'] ?? null,
                'status' => 'active',
                'customFields' => [
                    'credit_limit' => $companyData['creditLimit'] ?? null,
                    'payment_terms' => $companyData['paymentTerms'] ?? 'net30',
                    'discount_percent' => $companyData['discountPercent'] ?? 0
                ]
            ]
        ], $context);

        // Create customer for admin
        $customerId = $this->createCustomerAccount($adminData, $context);

        // Create admin employee
        $this->employeeRepository->create([
            [
                'id' => $adminId,
                'companyId' => $companyId,
                'customerId' => $customerId,
                'email' => $adminData['email'],
                'firstName' => $adminData['firstName'],
                'lastName' => $adminData['lastName'],
                'role' => [
                    'name' => 'Company Admin',
                    'canPlaceOrders' => true,
                    'canApproveOrders' => true,
                    'canManageEmployees' => true,
                    'canViewAllOrders' => true
                ]
            ]
        ], $context);

        return $companyId;
    }

    public function addEmployee(
        string $companyId,
        array $employeeData,
        string $roleId,
        Context $context
    ): string {
        // Create customer account
        $customerId = $this->createCustomerAccount($employeeData, $context);

        // Link as employee
        $employeeId = Uuid::randomHex();

        $this->employeeRepository->create([
            [
                'id' => $employeeId,
                'companyId' => $companyId,
                'customerId' => $customerId,
                'email' => $employeeData['email'],
                'firstName' => $employeeData['firstName'],
                'lastName' => $employeeData['lastName'],
                'roleId' => $roleId,
                'supervisorId' => $employeeData['supervisorId'] ?? null,
                'budgetLimit' => $employeeData['budgetLimit'] ?? null
            ]
        ], $context);

        return $employeeId;
    }
}
```

**B2B role permissions:**

| Permission | Description |
|------------|-------------|
| `canPlaceOrders` | Can submit orders |
| `canApproveOrders` | Can approve pending orders |
| `canManageEmployees` | Can add/edit employees |
| `canViewAllOrders` | See all company orders |
| `canEditCompany` | Edit company settings |
| `budgetLimit` | Maximum order value |

Reference: [B2B Components](https://developer.shopware.com/docs/guides/plugins/plugins/b2b-components/)
