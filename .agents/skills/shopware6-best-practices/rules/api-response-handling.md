---
title: API Response Handling
impact: MEDIUM
impactDescription: Consistent response handling ensures API consumers receive predictable data structures and appropriate HTTP status codes
tags: [shopware6, api, responses, error-handling, http-status]
---

## API Response Handling

Proper response handling in Shopware 6 APIs involves using appropriate response classes, consistent error formatting, and correct HTTP status codes. This ensures API consumers can reliably process responses.

Reference: https://developer.shopware.com/docs/guides/plugins/plugins/framework/api/

### Incorrect

```php
<?php

// Bad: Inconsistent response format and wrong status codes
namespace MyPlugin\Controller\Api;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
class BadApiController extends AbstractController
{
    #[Route(path: '/api/_action/my-plugin/create', methods: ['POST'])]
    public function create(): JsonResponse
    {
        // Bad: Returning 200 for creation instead of 201
        return new JsonResponse(['created' => true]);
    }

    #[Route(path: '/api/_action/my-plugin/process', methods: ['POST'])]
    public function process(): JsonResponse
    {
        try {
            throw new \Exception('Something went wrong');
        } catch (\Exception $e) {
            // Bad: Returning 200 with error in body
            return new JsonResponse(['error' => $e->getMessage()]);
        }
    }

    #[Route(path: '/api/_action/my-plugin/validate', methods: ['POST'])]
    public function validate(): Response
    {
        // Bad: Inconsistent error format, plain text response
        return new Response('Invalid data', 400);
    }

    #[Route(path: '/api/_action/my-plugin/delete', methods: ['DELETE'])]
    public function delete(): JsonResponse
    {
        // Bad: Returning content for delete, should be 204 No Content
        return new JsonResponse(['deleted' => true, 'message' => 'Item was deleted']);
    }
}
```

### Correct

```php
<?php

// Good: Proper response handling with correct status codes
namespace MyPlugin\Controller\Api;

use Shopware\Core\Framework\Api\Response\JsonApiResponse;
use Shopware\Core\Framework\Context;
use Shopware\Core\Framework\Validation\DataBag\RequestDataBag;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route(defaults: ['_routeScope' => ['api']])]
class ProperApiController extends AbstractController
{
    #[Route(
        path: '/api/_action/my-plugin/create',
        methods: ['POST'],
        defaults: ['_acl' => ['my_plugin:create']]
    )]
    public function create(RequestDataBag $data, Context $context): JsonResponse
    {
        // Good: Return 201 Created with location header for resource creation
        $id = $this->createResource($data, $context);

        return new JsonResponse(
            [
                'data' => [
                    'id' => $id,
                    'type' => 'my_plugin_entity',
                ]
            ],
            Response::HTTP_CREATED,
            ['Location' => '/api/my-plugin-entity/' . $id]
        );
    }

    #[Route(
        path: '/api/_action/my-plugin/process',
        methods: ['POST'],
        defaults: ['_acl' => ['my_plugin:update']]
    )]
    public function process(RequestDataBag $data, Context $context): JsonResponse
    {
        try {
            $result = $this->processData($data, $context);

            return new JsonResponse([
                'data' => [
                    'type' => 'process_result',
                    'attributes' => $result,
                ]
            ]);
        } catch (MyPluginValidationException $e) {
            // Good: 400 for validation errors with proper structure
            return new JsonResponse(
                [
                    'errors' => [
                        [
                            'status' => (string) Response::HTTP_BAD_REQUEST,
                            'code' => $e->getErrorCode(),
                            'title' => 'Validation Error',
                            'detail' => $e->getMessage(),
                            'source' => ['pointer' => $e->getField()],
                        ]
                    ]
                ],
                Response::HTTP_BAD_REQUEST
            );
        } catch (MyPluginNotFoundException $e) {
            // Good: 404 for not found
            return new JsonResponse(
                [
                    'errors' => [
                        [
                            'status' => (string) Response::HTTP_NOT_FOUND,
                            'code' => $e->getErrorCode(),
                            'title' => 'Not Found',
                            'detail' => $e->getMessage(),
                        ]
                    ]
                ],
                Response::HTTP_NOT_FOUND
            );
        }
    }

    #[Route(
        path: '/api/_action/my-plugin/delete/{id}',
        methods: ['DELETE'],
        defaults: ['_acl' => ['my_plugin:delete']]
    )]
    public function delete(string $id, Context $context): Response
    {
        $this->deleteResource($id, $context);

        // Good: 204 No Content for successful deletion
        return new Response(null, Response::HTTP_NO_CONTENT);
    }

    #[Route(
        path: '/api/_action/my-plugin/async-process',
        methods: ['POST'],
        defaults: ['_acl' => ['my_plugin:create']]
    )]
    public function asyncProcess(RequestDataBag $data, Context $context): JsonResponse
    {
        $jobId = $this->queueAsyncJob($data, $context);

        // Good: 202 Accepted for async operations
        return new JsonResponse(
            [
                'data' => [
                    'type' => 'async_job',
                    'id' => $jobId,
                    'attributes' => [
                        'status' => 'queued',
                    ],
                ]
            ],
            Response::HTTP_ACCEPTED
        );
    }
}
```

```php
<?php

// Good: Custom exception with proper error code
namespace MyPlugin\Exception;

use Shopware\Core\Framework\ShopwareHttpException;
use Symfony\Component\HttpFoundation\Response;

class MyPluginValidationException extends ShopwareHttpException
{
    public function __construct(
        private readonly string $field,
        string $message
    ) {
        parent::__construct($message);
    }

    public function getErrorCode(): string
    {
        return 'MY_PLUGIN__VALIDATION_ERROR';
    }

    public function getStatusCode(): int
    {
        return Response::HTTP_BAD_REQUEST;
    }

    public function getField(): string
    {
        return $this->field;
    }
}
```

```php
<?php

// Good: Store API response struct with proper serialization
namespace MyPlugin\Core\Content\MyFeature\SalesChannel;

use Shopware\Core\Framework\Struct\Struct;

class MyFeatureStruct extends Struct
{
    public function __construct(
        protected string $id,
        protected string $name,
        protected array $attributes = []
    ) {
    }

    public function getId(): string
    {
        return $this->id;
    }

    public function getName(): string
    {
        return $this->name;
    }

    public function getAttributes(): array
    {
        return $this->attributes;
    }

    public function getApiAlias(): string
    {
        return 'my_feature_struct';
    }
}
```
