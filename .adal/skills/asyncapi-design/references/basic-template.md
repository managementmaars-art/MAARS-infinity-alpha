# AsyncAPI 3.0 Basic Template

**Load when:** Creating a new AsyncAPI specification from scratch

## Complete Order Events Example

```yaml
asyncapi: 3.0.0
info:
  title: Order Events API
  version: 1.0.0
  description: |
    Event-driven API for order lifecycle events.

    ## Overview
    This API publishes events when orders change state, enabling
    downstream systems to react to order lifecycle changes.
  contact:
    name: Events Team
    email: events@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  production:
    host: kafka.example.com:9092
    protocol: kafka
    description: Production Kafka cluster
    security:
      - $ref: '#/components/securitySchemes/sasl'

  development:
    host: localhost:9092
    protocol: kafka
    description: Local development Kafka

defaultContentType: application/json

channels:
  orderCreated:
    address: orders.created
    messages:
      orderCreatedMessage:
        $ref: '#/components/messages/OrderCreated'
    description: Published when a new order is created

  orderSubmitted:
    address: orders.submitted
    messages:
      orderSubmittedMessage:
        $ref: '#/components/messages/OrderSubmitted'

  orderStatusChanged:
    address: orders.status.changed
    messages:
      orderStatusChangedMessage:
        $ref: '#/components/messages/OrderStatusChanged'

operations:
  publishOrderCreated:
    action: send
    channel:
      $ref: '#/channels/orderCreated'
    summary: Publish order created event
    description: |
      Published when a customer creates a new order.
      Consumers should use this to initialize order tracking.

  consumeOrderCreated:
    action: receive
    channel:
      $ref: '#/channels/orderCreated'
    summary: Consume order created events
    description: Subscribe to receive new order notifications

  publishOrderSubmitted:
    action: send
    channel:
      $ref: '#/channels/orderSubmitted'

  publishOrderStatusChanged:
    action: send
    channel:
      $ref: '#/channels/orderStatusChanged'

components:
  messages:
    OrderCreated:
      name: OrderCreated
      title: Order Created Event
      summary: Event published when an order is created
      contentType: application/json
      headers:
        $ref: '#/components/schemas/EventHeaders'
      payload:
        $ref: '#/components/schemas/OrderCreatedPayload'
      examples:
        - name: basicOrder
          summary: Basic order creation
          headers:
            correlationId: "550e8400-e29b-41d4-a716-446655440000"
            eventType: "OrderCreated"
            eventVersion: "1.0"
            timestamp: "2025-01-15T10:30:00Z"
          payload:
            orderId: "ord-123456"
            customerId: "cust-789"
            items:
              - productId: "prod-001"
                quantity: 2
                unitPrice: 29.99
            createdAt: "2025-01-15T10:30:00Z"

    OrderSubmitted:
      name: OrderSubmitted
      title: Order Submitted Event
      contentType: application/json
      headers:
        $ref: '#/components/schemas/EventHeaders'
      payload:
        $ref: '#/components/schemas/OrderSubmittedPayload'

    OrderStatusChanged:
      name: OrderStatusChanged
      title: Order Status Changed Event
      contentType: application/json
      headers:
        $ref: '#/components/schemas/EventHeaders'
      payload:
        $ref: '#/components/schemas/OrderStatusChangedPayload'

  schemas:
    EventHeaders:
      type: object
      required:
        - correlationId
        - eventType
        - timestamp
      properties:
        correlationId:
          type: string
          format: uuid
          description: Unique identifier for request tracing
        eventType:
          type: string
          description: Type of the event
        eventVersion:
          type: string
          description: Schema version of the event
        timestamp:
          type: string
          format: date-time
          description: When the event occurred

    OrderCreatedPayload:
      type: object
      required:
        - orderId
        - customerId
        - createdAt
      properties:
        orderId:
          type: string
          description: Unique order identifier
        customerId:
          type: string
          description: Customer who created the order
        items:
          type: array
          items:
            $ref: '#/components/schemas/LineItem'
        createdAt:
          type: string
          format: date-time

    OrderSubmittedPayload:
      type: object
      required:
        - orderId
        - customerId
        - total
        - submittedAt
      properties:
        orderId:
          type: string
        customerId:
          type: string
        total:
          $ref: '#/components/schemas/Money'
        submittedAt:
          type: string
          format: date-time

    OrderStatusChangedPayload:
      type: object
      required:
        - orderId
        - previousStatus
        - newStatus
        - changedAt
      properties:
        orderId:
          type: string
        previousStatus:
          $ref: '#/components/schemas/OrderStatus'
        newStatus:
          $ref: '#/components/schemas/OrderStatus'
        reason:
          type: string
          description: Optional reason for status change
        changedAt:
          type: string
          format: date-time

    LineItem:
      type: object
      required:
        - productId
        - quantity
        - unitPrice
      properties:
        productId:
          type: string
        productName:
          type: string
        quantity:
          type: integer
          minimum: 1
        unitPrice:
          type: number
          format: decimal

    Money:
      type: object
      required:
        - amount
        - currency
      properties:
        amount:
          type: number
          format: decimal
        currency:
          type: string
          pattern: '^[A-Z]{3}$'

    OrderStatus:
      type: string
      enum:
        - draft
        - submitted
        - paid
        - shipped
        - delivered
        - cancelled

  securitySchemes:
    sasl:
      type: scramSha256
      description: SASL/SCRAM-SHA-256 authentication

    apiKey:
      type: apiKey
      in: user
      description: API key authentication
```

## Key Sections Explained

| Section | Purpose |
|---------|---------|
| `info` | Metadata about the API |
| `servers` | Message broker connection details |
| `channels` | Topics/queues where messages flow |
| `operations` | Actions (send/receive) on channels |
| `components` | Reusable messages, schemas, security schemes |
