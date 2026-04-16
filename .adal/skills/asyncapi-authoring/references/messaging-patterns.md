# Event-Driven Messaging Patterns

## Message Exchange Patterns

### Publish-Subscribe

```yaml
pattern:
  name: "Publish-Subscribe"
  description: "One publisher, many subscribers"

  characteristics:
    coupling: "Loose - publisher doesn't know subscribers"
    delivery: "Fan-out to all subscribers"
    ordering: "Per-partition ordering (Kafka) or none"

  use_cases:
    - "Domain events broadcast"
    - "Notifications"
    - "Real-time updates"
    - "Event sourcing"

  asyncapi_example:
    channels:
      orderEvents:
        address: "orders.events"
        description: "Order lifecycle events"

    operations:
      publishOrderCreated:
        action: send
        channel:
          $ref: "#/channels/orderEvents"

      subscribeOrderEvents:
        action: receive
        channel:
          $ref: "#/channels/orderEvents"

  considerations:
    - "No guaranteed delivery to specific consumer"
    - "Subscribers must handle duplicates"
    - "Message ordering challenges with multiple partitions"
```

### Point-to-Point (Queue)

```yaml
pattern:
  name: "Point-to-Point"
  description: "One sender, one receiver (competing consumers)"

  characteristics:
    coupling: "Loose - sender doesn't know receiver"
    delivery: "Exactly one consumer receives each message"
    ordering: "FIFO within queue"

  use_cases:
    - "Work queues"
    - "Command processing"
    - "Task distribution"
    - "Load leveling"

  asyncapi_example:
    channels:
      orderProcessing:
        address: "orders.processing"
        description: "Order processing work queue"

    operations:
      sendOrderForProcessing:
        action: send
        channel:
          $ref: "#/channels/orderProcessing"

      processOrder:
        action: receive
        channel:
          $ref: "#/channels/orderProcessing"

  considerations:
    - "Competing consumers for scalability"
    - "Message acknowledgment required"
    - "Dead letter queue for failures"
```

### Request-Reply

```yaml
pattern:
  name: "Request-Reply"
  description: "Synchronous-style messaging over async transport"

  characteristics:
    coupling: "Temporal coupling (waiting for response)"
    delivery: "Point-to-point in both directions"
    correlation: "Required - match response to request"

  use_cases:
    - "Query operations"
    - "Synchronous workflows over async"
    - "Service orchestration"

  asyncapi_example:
    channels:
      orderQueries:
        address: "orders.queries"
        messages:
          getOrderQuery:
            $ref: "#/components/messages/GetOrderQuery"

      orderQueryResponses:
        address: "orders.queries.responses.{correlationId}"
        parameters:
          correlationId:
            schema:
              type: string
        messages:
          getOrderResponse:
            $ref: "#/components/messages/GetOrderResponse"

  message_structure:
    request:
      correlationId: "unique-id"
      replyTo: "orders.queries.responses.unique-id"
      payload:
        orderId: "order-123"

    response:
      correlationId: "unique-id"
      payload:
        orderId: "order-123"
        status: "shipped"

  considerations:
    - "Timeout handling required"
    - "Response channel cleanup"
    - "Consider if sync API is simpler"
```

## Delivery Patterns

### At-Least-Once Delivery

```yaml
pattern:
  name: "At-Least-Once"
  description: "Messages delivered at least once, may have duplicates"

  characteristics:
    guarantee: "No message loss"
    duplicates: "Possible"
    complexity: "Lower"

  implementation:
    producer:
      - "Retry on failure"
      - "Wait for acknowledgment"
    consumer:
      - "Process message"
      - "Acknowledge after processing"
      - "Must be idempotent"

  asyncapi_bindings:
    kafka:
      acks: "all"
      retries: 3

  consumer_idempotency:
    approaches:
      deduplication_id:
        description: "Track processed message IDs"
        implementation: "Store in Redis/database"
        ttl: "24-48 hours typically"

      idempotent_operations:
        description: "Operations naturally idempotent"
        examples:
          - "SET operations (vs INCREMENT)"
          - "Upserts with same key"
```

### Exactly-Once Semantics

```yaml
pattern:
  name: "Exactly-Once"
  description: "Each message processed exactly once"

  characteristics:
    guarantee: "No loss, no duplicates"
    complexity: "High"
    cost: "Performance overhead"

  implementation_approaches:
    transactional_outbox:
      description: "Write event and state in same transaction"
      steps:
        - "Begin transaction"
        - "Update business state"
        - "Write to outbox table"
        - "Commit transaction"
        - "Background: poll outbox, publish, mark sent"

    kafka_transactions:
      description: "Kafka's transactional producer"
      steps:
        - "beginTransaction()"
        - "send() messages"
        - "sendOffsetsToTransaction()"
        - "commitTransaction()"

  asyncapi_bindings:
    kafka:
      transactionalId: "order-service-producer"
      enableIdempotence: true
```

### At-Most-Once Delivery

```yaml
pattern:
  name: "At-Most-Once"
  description: "Messages delivered at most once, may be lost"

  characteristics:
    guarantee: "No duplicates"
    loss: "Possible"
    use_case: "Metrics, logs, non-critical updates"

  implementation:
    producer:
      - "Fire and forget"
      - "No retry on failure"
    consumer:
      - "Acknowledge before processing"

  asyncapi_bindings:
    kafka:
      acks: 0

  when_acceptable:
    - "Real-time metrics (next value replaces)"
    - "Heartbeats"
    - "Progress updates"
    - "Non-critical notifications"
```

## Event Patterns

### Event Notification

```yaml
pattern:
  name: "Event Notification"
  description: "Minimal event, receiver queries for details"

  characteristics:
    payload_size: "Small - just identifiers"
    coupling: "Higher - receiver needs API access"
    freshness: "Guaranteed - always fetches latest"

  example:
    event:
      eventType: "OrderCreated"
      orderId: "order-123"
      _links:
        order: "https://api.example.com/orders/order-123"

  use_when:
    - "Payload would be large"
    - "Freshness critical"
    - "Security concerns with event data"
    - "Existing API available"

  drawbacks:
    - "Extra API calls"
    - "API must be available"
    - "Point-in-time state lost"
```

### Event-Carried State Transfer

```yaml
pattern:
  name: "Event-Carried State Transfer"
  description: "Event contains all relevant data"

  characteristics:
    payload_size: "Larger - includes state"
    coupling: "Lower - no API needed"
    freshness: "Point-in-time snapshot"

  example:
    event:
      eventType: "OrderCreated"
      orderId: "order-123"
      customerId: "customer-456"
      items:
        - productId: "prod-1"
          quantity: 2
          price: 29.99
      totalAmount: 59.98
      shippingAddress:
        street: "123 Main St"
        city: "Seattle"

  use_when:
    - "Consumers need full context"
    - "Reduce API coupling"
    - "Enable offline processing"
    - "Support event replay"

  considerations:
    - "Larger message sizes"
    - "Schema evolution complexity"
    - "May include stale data"
```

### Event Sourcing

```yaml
pattern:
  name: "Event Sourcing"
  description: "Store state as sequence of events"

  characteristics:
    storage: "Append-only event log"
    state: "Derived by replaying events"
    audit: "Complete history"

  event_types:
    domain_events:
      - "OrderCreated"
      - "OrderItemAdded"
      - "OrderShipped"
      - "OrderCancelled"

  event_store_operations:
    append: "Add new event to stream"
    read_stream: "Get all events for aggregate"
    subscribe: "Listen for new events"

  projection_pattern:
    description: "Build read models from events"
    types:
      live: "Updated in real-time"
      catch_up: "Rebuild from start"
      partitioned: "Separate by criteria"

  asyncapi_modeling:
    channels:
      orderEventStore:
        address: "orders.store.{orderId}"
        description: "Event store for order aggregate"
        parameters:
          orderId:
            schema:
              type: string
              format: uuid

  considerations:
    - "Event schema versioning critical"
    - "Snapshotting for long streams"
    - "Eventual consistency"
    - "Event replay capability"
```

## Integration Patterns

### Saga Pattern

```yaml
pattern:
  name: "Saga (Choreography)"
  description: "Distributed transaction via event chain"

  flow:
    step_1:
      service: "Order Service"
      action: "Create order"
      event: "OrderCreated"

    step_2:
      service: "Inventory Service"
      trigger: "OrderCreated"
      action: "Reserve inventory"
      success_event: "InventoryReserved"
      failure_event: "InventoryReservationFailed"

    step_3:
      service: "Payment Service"
      trigger: "InventoryReserved"
      action: "Process payment"
      success_event: "PaymentProcessed"
      failure_event: "PaymentFailed"

    step_4:
      service: "Order Service"
      trigger: "PaymentProcessed"
      action: "Confirm order"
      event: "OrderConfirmed"

  compensation:
    on_PaymentFailed:
      - "Inventory Service: Release reservation"
      - "Order Service: Mark order failed"

  asyncapi_channels:
    orderEvents:
      address: "orders.events"
    inventoryEvents:
      address: "inventory.events"
    paymentEvents:
      address: "payments.events"
```

### Dead Letter Queue

```yaml
pattern:
  name: "Dead Letter Queue"
  description: "Handle unprocessable messages"

  triggers:
    - "Processing failures after max retries"
    - "Schema validation failures"
    - "Business rule violations"
    - "Expired messages"

  asyncapi_example:
    channels:
      orderProcessing:
        address: "orders.processing"
        description: "Main processing queue"

      orderProcessingDLQ:
        address: "orders.processing.dlq"
        description: "Dead letter queue for failed orders"
        messages:
          deadLetter:
            $ref: "#/components/messages/DeadLetterMessage"

  dead_letter_envelope:
    original_message: "The failed message"
    failure_reason: "Exception message"
    failure_timestamp: "When it failed"
    retry_count: "Number of attempts"
    original_topic: "Source topic/queue"
    stack_trace: "For debugging"

  handling_strategies:
    manual_review: "Alert and investigate"
    automatic_retry: "Retry with backoff"
    redirect: "Route to different processor"
    discard: "Log and drop"
```

### Outbox Pattern

```yaml
pattern:
  name: "Transactional Outbox"
  description: "Reliable event publishing with database transactions"

  problem: "Dual-write problem - DB + message broker"

  solution:
    steps:
      - "Begin database transaction"
      - "Update domain entities"
      - "Insert event to outbox table"
      - "Commit transaction"
      - "Background: poll outbox, publish, mark sent"

  outbox_table:
    schema:
      id: "UUID primary key"
      aggregate_type: "e.g., 'Order'"
      aggregate_id: "e.g., order ID"
      event_type: "e.g., 'OrderCreated'"
      payload: "JSON event data"
      created_at: "Timestamp"
      published_at: "Null until published"

  polling_approaches:
    simple_polling:
      interval: "100-500ms"
      batch_size: "100 messages"

    change_data_capture:
      tool: "Debezium"
      approach: "Read database log"
      benefit: "Lower latency, no polling"

  asyncapi_consideration:
    description: "Outbox is implementation detail, not in spec"
    expose: "Only the resulting events"
```

## Protocol Considerations

### Kafka-Specific

```yaml
kafka_patterns:
  partitioning:
    strategy: "By aggregate ID for ordering"
    example:
      key: "order-123"
      partition: "hash(key) % num_partitions"

    asyncapi_binding:
      kafka:
        key:
          type: string
          description: "Partition key (aggregate ID)"
        partitions: 12

  consumer_groups:
    purpose: "Parallel consumption with ordering"
    behavior: "One partition per consumer max"

  compaction:
    purpose: "Keep latest value per key"
    use_case: "State snapshots, CDC"
```

### RabbitMQ-Specific

```yaml
rabbitmq_patterns:
  exchange_types:
    direct: "Exact routing key match"
    fanout: "Broadcast to all queues"
    topic: "Pattern matching on routing key"
    headers: "Match on message headers"

  asyncapi_binding:
    amqp:
      exchange:
        name: "order-events"
        type: "topic"
        durable: true
      queue:
        name: "order-processor"
        durable: true
        exclusive: false
      routingKey: "orders.created.#"
```

---

**Last Updated:** 2025-12-26
