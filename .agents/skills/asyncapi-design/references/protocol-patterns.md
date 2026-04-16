# Protocol-Specific AsyncAPI Patterns

**Load when:** Configuring AsyncAPI for specific message brokers (Kafka, RabbitMQ, MQTT, WebSocket)

## Table of Contents

- [Kafka](#kafka)
- [RabbitMQ](#rabbitmq)
- [MQTT (IoT)](#mqtt-iot)
- [WebSocket](#websocket)

## Kafka

```yaml
servers:
  kafka:
    host: broker1.example.com:9092,broker2.example.com:9092
    protocol: kafka
    protocolVersion: '3.0'
    bindings:
      kafka:
        schemaRegistryUrl: http://schema-registry:8081
        schemaRegistryVendor: confluent

channels:
  orderEvents:
    address: orders.events.v1
    bindings:
      kafka:
        topic: orders.events.v1
        partitions: 12
        replicas: 3
        topicConfiguration:
          cleanup.policy: ['delete']
          retention.ms: 604800000
          segment.bytes: 1073741824

operations:
  publishOrderEvent:
    action: send
    channel:
      $ref: '#/channels/orderEvents'
    bindings:
      kafka:
        groupId:
          type: string
        clientId:
          type: string
        bindingVersion: '0.5.0'
```

### Kafka Configuration Reference

| Setting | Purpose | Typical Value |
|---------|---------|---------------|
| `partitions` | Parallelism level | 3-12 for most cases |
| `replicas` | Fault tolerance | 3 for production |
| `retention.ms` | Message retention | 604800000 (7 days) |
| `cleanup.policy` | delete or compact | delete for events |

## RabbitMQ

```yaml
servers:
  rabbitmq:
    host: rabbitmq.example.com:5672
    protocol: amqp
    protocolVersion: '0.9.1'

channels:
  orderQueue:
    address: order-processing-queue
    bindings:
      amqp:
        is: queue
        queue:
          name: order-processing
          durable: true
          exclusive: false
          autoDelete: false
        exchange:
          name: orders-exchange
          type: topic
          durable: true
        bindingVersion: '0.3.0'
```

### RabbitMQ Exchange Types

| Type | Use Case |
|------|----------|
| `direct` | Exact routing key match |
| `topic` | Pattern-based routing |
| `fanout` | Broadcast to all queues |
| `headers` | Route by message headers |

## MQTT (IoT)

```yaml
servers:
  mqtt:
    host: mqtt.example.com:1883
    protocol: mqtt
    protocolVersion: '5.0'

channels:
  deviceTelemetry:
    address: devices/{deviceId}/telemetry
    parameters:
      deviceId:
        description: Unique device identifier
        schema:
          type: string
    bindings:
      mqtt:
        qos: 1
        retain: false
        bindingVersion: '0.2.0'
```

### MQTT QoS Levels

| Level | Guarantee | Use Case |
|-------|-----------|----------|
| 0 | At most once | Telemetry, high frequency |
| 1 | At least once | Commands, important events |
| 2 | Exactly once | Financial, critical |

## WebSocket

```yaml
servers:
  websocket:
    host: ws.example.com
    protocol: ws
    protocolVersion: '13'

channels:
  orderUpdates:
    address: /orders/updates
    bindings:
      ws:
        method: GET
        headers:
          type: object
          properties:
            Authorization:
              type: string
```

### WebSocket Security

For secure WebSocket connections:

```yaml
servers:
  websocketSecure:
    host: wss.example.com
    protocol: wss
    security:
      - $ref: '#/components/securitySchemes/bearerAuth'
```
