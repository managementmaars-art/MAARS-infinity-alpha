---
name: arch-event-driven
cluster: se-architecture
description: "Event-driven: Kafka/RabbitMQ, event sourcing, CQRS, pub/sub, dead letter queues, schema registry"
tags: ["event-driven","kafka","eventsourcing","cqrs","architecture"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "event driven kafka event sourcing cqrs pub sub dead letter queue"
---

# arch-event-driven

## Purpose
This skill implements event-driven architectures using Kafka, RabbitMQ, and related patterns like event sourcing, CQRS, pub/sub, dead letter queues, and schema registries. It helps design scalable, decoupled systems for real-time event processing in microservices environments.

## When to Use
Use this skill for scenarios requiring asynchronous communication, such as microservices that need to react to events without direct dependencies. Apply it in high-volume data pipelines, real-time analytics, or when decoupling producers and consumers is essential, like in e-commerce order processing or IoT data streams. Avoid it for simple synchronous operations where polling suffices.

## Key Capabilities
- Set up Kafka topics and partitions for event streaming.
- Implement event sourcing by storing events in Kafka for state reconstruction.
- Apply CQRS to separate read and write models, using Kafka for commands and queries.
- Manage pub/sub with Kafka consumer groups for fan-out scenarios.
- Handle failures via dead letter queues in Kafka or RabbitMQ.
- Enforce schema validation using Confluent Schema Registry for Avro schemas.

## Usage Patterns
To implement pub/sub, create a Kafka topic and have producers publish events; consumers subscribe via groups. For event sourcing, store all state changes as events in a Kafka stream and replay them to build current state. In CQRS, route commands to a write service (e.g., via Kafka producer) and queries to a read service (e.g., from a materialized view). Use dead letter queues by configuring Kafka topics to redirect failed messages. Always define event schemas in JSON or Avro format for consistency.

## Common Commands/API
Use Kafka CLI for topic management: run `kafka-topics.sh --bootstrap-server localhost:9092 --create --topic orders --partitions 3 --replication-factor 2`. To produce events, use:  
```bash
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic orders
{"orderId": 123, "status": "placed"}
```
Consume events with:  
```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic orders --from-beginning
```
For RabbitMQ, declare exchanges and queues via CLI: `rabbitmqadmin declare exchange name=events type=fanout`. API endpoints: Use Kafka REST Proxy at `/topics/{topic}/messages` with POST for producing (e.g., curl -X POST -H "Content-Type: application/vnd.kafka.json.v2+json" --data '{"records":[{"value":{"orderId":123}}]}' http://localhost:8082/topics/orders). Authenticate with env var: `$KAFKA_API_KEY` in headers like `-H "Authorization: Bearer $KAFKA_API_KEY"`. Config formats: Use Kafka properties file like `key.serializer=org.apache.kafka.common.serialization.StringSerializer` in producer configs.

## Integration Notes
Integrate Kafka with applications by adding the Kafka client library (e.g., in Java: `kafka-clients:3.0.0`). Set environment variables for credentials: export `RABBITMQ_URL=amqp://user:$RABBITMQ_PASSWORD@localhost`. For schema registry, point to Confluent's endpoint: `schema.registry.url=http://localhost:8081` in producer configs. When linking with databases, use Kafka Connect for JDBC sources: configure with JSON file like {"name": "jdbc-source", "connector.class": "io.confluent.connect.jdbc.JdbcSourceConnector", "connection.url": "jdbc:postgresql://localhost:5432/db"}. Ensure producers handle retries on transient errors.

## Error Handling
Configure dead letter queues in Kafka by setting up a separate topic for failures: in consumer code, catch exceptions and produce to "dead-letter-topic". Example:  
```java
try { consumer.poll(Duration.ofMillis(100)); } catch (Exception e) { producer.send(new ProducerRecord("dead-letter-topic", record.value())); }
```
In RabbitMQ, bind a queue to a dead letter exchange. Always log errors with details like error code and timestamp. Use schema registry to validate events and reject invalid ones, e.g., via `SchemaRegistryClient` API. Monitor with tools like Kafka's JMX for lag and errors; set up alerts if consumer lag exceeds 1000 messages.

## Concrete Usage Examples
**Example 1: Basic Kafka Pub/Sub Setup**  
To set up a pub/sub for user events: First, create a topic: `kafka-topics.sh --bootstrap-server localhost:9092 --create --topic user-events`. Produce an event:  
```bash
kafka-console-producer.sh --bootstrap-server localhost:9092 --topic user-events
{"userId": 1, "action": "login"}
```
Consume it: `kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic user-events --group mygroup`. This decouples producers from consumers for scalable event handling.

**Example 2: Implementing CQRS with Event Sourcing**  
For an e-commerce app, use Kafka for commands: Produce to "commands-topic" with `producer.send(new ProducerRecord("commands-topic", "{\"command\": \"placeOrder\", \"orderId\": 123}"))`. For queries, maintain a read model by consuming events and updating a database. Example consumer code:  
```java
consumer.subscribe(Arrays.asList("events-topic"));
while (true) { ConsumerRecords<String, String> records = consumer.poll(Duration.ofSeconds(1)); for (ConsumerRecord<String, String> record : records) { updateReadModel(record.value()); } }
```
This ensures write operations are handled separately from reads, improving performance.

## Graph Relationships
- Related to cluster: se-architecture
- Connected tags: event-driven, kafka, eventsourcing, cqrs
- Links to: se-deployment (for Kafka cluster setup), se-data-pipelines (for event streaming integrations)
