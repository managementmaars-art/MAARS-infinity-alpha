# Event Design Patterns for AsyncAPI

**Load when:** Designing event schemas, versioning strategies, or implementing best practices

## Table of Contents

- [Event Envelope Pattern](#event-envelope-pattern)
- [Event Versioning](#event-versioning)
- [Channel Naming](#channel-naming)
- [Message Design Guidelines](#message-design-guidelines)
- [Security Schemes](#security-schemes)

## Event Envelope Pattern

Using CloudEvents specification for consistent event structure:

```yaml
components:
  schemas:
    CloudEventEnvelope:
      type: object
      required:
        - specversion
        - type
        - source
        - id
        - time
        - data
      properties:
        specversion:
          type: string
          const: "1.0"
        type:
          type: string
          description: Event type (e.g., com.example.order.created)
        source:
          type: string
          format: uri
          description: Event source URI
        id:
          type: string
          format: uuid
        time:
          type: string
          format: date-time
        datacontenttype:
          type: string
          default: application/json
        dataschema:
          type: string
          format: uri
        subject:
          type: string
          description: Subject of event (e.g., order ID)
        data:
          type: object
          description: Event payload
```

## Event Versioning

### Parallel Version Channels

```yaml
channels:
  orderEventsV1:
    address: orders.events.v1
    messages:
      orderCreatedV1:
        $ref: '#/components/messages/OrderCreatedV1'

  orderEventsV2:
    address: orders.events.v2
    messages:
      orderCreatedV2:
        $ref: '#/components/messages/OrderCreatedV2'

components:
  messages:
    OrderCreatedV1:
      name: OrderCreatedV1
      schemaFormat: application/vnd.aai.asyncapi+json;version=3.0.0
      payload:
        type: object
        properties:
          orderId:
            type: string
          # V1 schema

    OrderCreatedV2:
      name: OrderCreatedV2
      schemaFormat: application/vnd.aai.asyncapi+json;version=3.0.0
      payload:
        type: object
        properties:
          orderId:
            type: string
            format: uuid
          metadata:
            type: object
          # V2 schema with breaking changes
```

### Versioning Strategies

| Strategy | When to Use | Example |
|----------|-------------|---------|
| **Additive** | New optional fields | Add `metadata` field |
| **URL/Channel** | Breaking changes | `orders.events.v2` |
| **Header** | Runtime routing | `event-version: 2.0` |
| **Schema registry** | Strong typing | Confluent Schema Registry |

## Channel Naming

### Recommended Hierarchy

```yaml
# Pattern: {domain}.{entity}.{action}.{version}
channels:
  orderCreated:
    address: orders.order.created.v1
  orderItemAdded:
    address: orders.lineitem.added.v1
  paymentProcessed:
    address: payments.payment.processed.v1
```

### Naming Conventions

| Component | Convention | Example |
|-----------|------------|---------|
| Domain | lowercase, singular | `orders`, `payments` |
| Entity | lowercase, singular | `order`, `lineitem` |
| Action | past tense verb | `created`, `updated`, `deleted` |
| Version | `v` + number | `v1`, `v2` |

## Message Design Guidelines

### Core Principles

1. **Self-describing**: Include type and version in headers
2. **Idempotent**: Use event ID for deduplication
3. **Ordered**: Use partition keys for ordering (aggregate ID)
4. **Backward compatible**: Add fields, don't remove
5. **Complete**: Include all data consumers need (avoid chatty patterns)

### Header Standards

```yaml
components:
  schemas:
    StandardHeaders:
      type: object
      required:
        - correlationId
        - eventType
        - eventVersion
        - timestamp
      properties:
        correlationId:
          type: string
          format: uuid
          description: Request tracing ID
        eventType:
          type: string
          description: Fully qualified event type
        eventVersion:
          type: string
          pattern: '^\d+\.\d+$'
        timestamp:
          type: string
          format: date-time
        causationId:
          type: string
          format: uuid
          description: ID of event that caused this event
```

## Security Schemes

### OAuth 2.0

```yaml
components:
  securitySchemes:
    oauth2:
      type: oauth2
      description: OAuth 2.0 authentication
      flows:
        clientCredentials:
          tokenUrl: https://auth.example.com/oauth/token
          scopes:
            orders:read: Read order events
            orders:write: Publish order events
```

### Mutual TLS

```yaml
components:
  securitySchemes:
    mtls:
      type: X509
      description: Mutual TLS authentication
```

### SASL (Kafka)

```yaml
components:
  securitySchemes:
    sasl:
      type: scramSha256
      description: SASL/SCRAM-SHA-256 authentication
```

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| Fat events | Too much data | Include only necessary fields |
| Chatty events | Multiple round trips | Include all needed data |
| No versioning | Breaking consumers | Always version schemas |
| Mutable events | Lost history | Events are immutable facts |
| No correlation | Can't trace requests | Always include correlationId |
