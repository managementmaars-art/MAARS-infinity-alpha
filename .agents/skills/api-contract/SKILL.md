---
name: api-contract
description: Generate OpenAPI, AsyncAPI, or Protobuf contract from requirements. Use for contract-first API development.
allowed-tools: Read, Glob, Grep, Write, Skill, Task
argument-hint: <api-description> [--format <openapi|asyncapi|protobuf>] [--version <x.y.z>]
---

# /api-contract Command

Generate contract-first API specifications from requirements or domain descriptions.

## Usage

```text
/api-contract "user registration with email verification"
/api-contract "order events for downstream systems" format=asyncapi
/api-contract "high-performance inventory service" format=protobuf
```

## Workflow

### Step 1: Analyze Requirements

Parse the API description to identify:

- Domain entities and resources
- Required operations (CRUD, queries, commands)
- Communication pattern (sync REST, async events, RPC)
- Key consumers and use cases

### Step 2: Select Contract Format

If format not specified, auto-detect based on description:

| Pattern | Recommended Format |
|---------|-------------------|
| "API", "REST", "endpoint" | OpenAPI 3.1 |
| "events", "messages", "streaming" | AsyncAPI 3.0 |
| "gRPC", "high-performance", "internal" | Protocol Buffers |

### Step 3: Invoke Appropriate Skill

Load the relevant skill:

- `openapi-design` for REST APIs
- `asyncapi-design` for event-driven APIs
- `protobuf-design` for gRPC services

### Step 4: Design Resource Model

Identify and structure:

- Core entities with properties
- Value objects and enumerations
- Relationships between entities
- Request/response wrappers

### Step 5: Generate Contract

Create the API specification including:

- Complete schema definitions
- All operations/methods
- Authentication configuration
- Error response schemas
- Examples for each operation

### Step 6: Output Result

Deliver:

1. Contract specification (YAML or .proto)
2. Summary of endpoints/channels/services
3. Implementation notes
4. Suggested test scenarios

## Format-Specific Output

### OpenAPI 3.1

```yaml
openapi: 3.1.0
info:
  title: Service Name API
  version: 1.0.0
paths:
  /resources:
    get: ...
    post: ...
components:
  schemas: ...
  securitySchemes: ...
```

### AsyncAPI 3.0

```yaml
asyncapi: 3.0.0
info:
  title: Service Events
  version: 1.0.0
channels:
  resourceCreated:
    address: resources.created
    messages: ...
components:
  messages: ...
  schemas: ...
```

### Protocol Buffers

```protobuf
syntax = "proto3";
package service.v1;

service ResourceService {
  rpc CreateResource(...) returns (...);
  rpc GetResource(...) returns (...);
}

message Resource {
  string id = 1;
  ...
}
```

## Examples

### REST API for User Registration

```text
/api-contract "user registration API with email verification and password reset"
```

Output:

- OpenAPI 3.1 specification
- POST /users (registration)
- POST /users/verify-email
- POST /users/forgot-password
- POST /users/reset-password
- JWT authentication scheme

### Event-Driven Order System

```text
/api-contract "order lifecycle events for fulfillment and notifications" format=asyncapi
```

Output:

- AsyncAPI 3.0 specification
- Channels: orders.created, orders.submitted, orders.shipped
- CloudEvents envelope
- Kafka bindings

### gRPC Product Catalog

```text
/api-contract "product catalog service with search and inventory" format=protobuf
```

Output:

- Protocol Buffers definition
- ProductService with CRUD + Search
- Streaming for bulk operations
- Well-known types for timestamps

## Integration

The command integrates with:

- **requirements-elicitation**: Uses functional requirements
- **enterprise-architecture**: Aligns with bounded contexts
- **test-strategy**: Generates contract test scenarios
- **systems-design**: Follows API design patterns
