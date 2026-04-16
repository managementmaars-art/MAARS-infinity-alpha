# C# Implementation Patterns for AsyncAPI

**Load when:** Implementing AsyncAPI specifications in .NET/C#

## Table of Contents

- [Event Contracts](#event-contracts)
- [MassTransit Publisher](#masstransit-publisher)
- [Kafka with Confluent](#kafka-with-confluent)

## Event Contracts

### Domain Events

```csharp
public abstract record DomainEvent
{
    public Guid EventId { get; init; } = Guid.NewGuid();
    public DateTimeOffset OccurredAt { get; init; } = DateTimeOffset.UtcNow;
    public string EventType => GetType().Name;
    public string EventVersion { get; init; } = "1.0";
}

public sealed record OrderCreatedEvent(
    Guid OrderId,
    Guid CustomerId,
    IReadOnlyList<LineItemDto> Items,
    DateTimeOffset CreatedAt) : DomainEvent;

public sealed record OrderSubmittedEvent(
    Guid OrderId,
    Guid CustomerId,
    Money Total,
    DateTimeOffset SubmittedAt) : DomainEvent;

public sealed record OrderStatusChangedEvent(
    Guid OrderId,
    OrderStatus PreviousStatus,
    OrderStatus NewStatus,
    string? Reason,
    DateTimeOffset ChangedAt) : DomainEvent;
```

### Integration Events

```csharp
// For cross-boundary communication
public abstract record IntegrationEvent
{
    public Guid Id { get; init; } = Guid.NewGuid();
    public Guid CorrelationId { get; init; }
    public DateTimeOffset Timestamp { get; init; } = DateTimeOffset.UtcNow;
    public string Source { get; init; } = "OrderService";
}

public sealed record OrderCreatedIntegrationEvent(
    Guid OrderId,
    Guid CustomerId,
    decimal TotalAmount,
    string Currency) : IntegrationEvent;
```

## MassTransit Publisher

### Publisher Service

```csharp
using MassTransit;

public sealed class OrderService
{
    private readonly IPublishEndpoint _publishEndpoint;
    private readonly ILogger<OrderService> _logger;

    public OrderService(
        IPublishEndpoint publishEndpoint,
        ILogger<OrderService> logger)
    {
        _publishEndpoint = publishEndpoint;
        _logger = logger;
    }

    public async Task CreateOrderAsync(
        CreateOrderCommand command,
        CancellationToken ct = default)
    {
        // Create order logic...
        var order = Order.Create(command.CustomerId, command.Items);

        // Publish event
        await _publishEndpoint.Publish(
            new OrderCreatedEvent(
                order.Id,
                order.CustomerId,
                order.Items.Select(i => i.ToDto()).ToList(),
                order.CreatedAt),
            ct);

        _logger.LogInformation(
            "Published OrderCreatedEvent for order {OrderId}",
            order.Id);
    }
}
```

### Consumer

```csharp
public sealed class OrderCreatedConsumer : IConsumer<OrderCreatedEvent>
{
    private readonly ILogger<OrderCreatedConsumer> _logger;

    public OrderCreatedConsumer(ILogger<OrderCreatedConsumer> logger)
    {
        _logger = logger;
    }

    public async Task Consume(ConsumeContext<OrderCreatedEvent> context)
    {
        var @event = context.Message;

        _logger.LogInformation(
            "Processing OrderCreatedEvent: {OrderId}, Customer: {CustomerId}",
            @event.OrderId,
            @event.CustomerId);

        // Handle the event...
    }
}
```

### Registration

```csharp
services.AddMassTransit(x =>
{
    x.AddConsumer<OrderCreatedConsumer>();

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host("rabbitmq://localhost", h =>
        {
            h.Username("guest");
            h.Password("guest");
        });

        cfg.ConfigureEndpoints(context);
    });
});
```

## Kafka with Confluent

### Producer

```csharp
using Confluent.Kafka;
using System.Text.Json;

public sealed class KafkaOrderPublisher : IAsyncDisposable
{
    private readonly IProducer<string, string> _producer;
    private readonly string _topic;
    private readonly ILogger<KafkaOrderPublisher> _logger;

    public KafkaOrderPublisher(
        IConfiguration config,
        ILogger<KafkaOrderPublisher> logger)
    {
        _logger = logger;
        _topic = config["Kafka:OrdersTopic"] ?? "orders.events.v1";

        var producerConfig = new ProducerConfig
        {
            BootstrapServers = config["Kafka:BootstrapServers"],
            Acks = Acks.All,
            EnableIdempotence = true,
            MessageSendMaxRetries = 3,
            RetryBackoffMs = 1000
        };

        _producer = new ProducerBuilder<string, string>(producerConfig)
            .SetKeySerializer(Serializers.Utf8)
            .SetValueSerializer(Serializers.Utf8)
            .Build();
    }

    public async Task PublishAsync<TEvent>(
        TEvent @event,
        CancellationToken ct = default) where TEvent : DomainEvent
    {
        var key = GetPartitionKey(@event);
        var value = JsonSerializer.Serialize(@event);

        var message = new Message<string, string>
        {
            Key = key,
            Value = value,
            Headers = new Headers
            {
                { "event-type", Encoding.UTF8.GetBytes(@event.EventType) },
                { "event-version", Encoding.UTF8.GetBytes(@event.EventVersion) },
                { "correlation-id", Encoding.UTF8.GetBytes(Guid.NewGuid().ToString()) }
            }
        };

        var result = await _producer.ProduceAsync(_topic, message, ct);

        _logger.LogInformation(
            "Published {EventType} to {Topic}:{Partition}@{Offset}",
            @event.EventType,
            result.Topic,
            result.Partition.Value,
            result.Offset.Value);
    }

    private static string GetPartitionKey<TEvent>(TEvent @event) where TEvent : DomainEvent
    {
        return @event switch
        {
            OrderCreatedEvent e => e.OrderId.ToString(),
            OrderSubmittedEvent e => e.OrderId.ToString(),
            OrderStatusChangedEvent e => e.OrderId.ToString(),
            _ => Guid.NewGuid().ToString()
        };
    }

    public async ValueTask DisposeAsync()
    {
        _producer.Flush(TimeSpan.FromSeconds(10));
        _producer.Dispose();
    }
}
```

## Best Practices

| Practice | Implementation |
|----------|----------------|
| Idempotence | Use `EnableIdempotence = true` for Kafka |
| Correlation | Pass `CorrelationId` in headers |
| Partitioning | Use aggregate ID as partition key |
| Serialization | Use System.Text.Json or protobuf |
| Error handling | Use dead-letter queues |
