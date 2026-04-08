---
name: microservices-patterns
description: Service mesh, API gateway, circuit breaker, service discovery, event-driven architecture, and gRPC for microservices.
---

# Microservices Patterns

## Overview

Microservices architecture decomposes applications into independently deployable services. Key concerns include service communication, resilience, observability, service discovery, and data consistency.

## API Gateway Pattern

```python
# FastAPI API Gateway with reverse proxy
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import asyncio

app = FastAPI()

SERVICE_REGISTRY = {
    "/users": "http://user-service:8001",
    "/orders": "http://order-service:8002",
    "/products": "http://product-service:8003",
    "/payments": "http://payment-service:8004",
}

client = httpx.AsyncClient(timeout=30.0)

@app.middleware("http")
async def gateway_middleware(request: Request, call_next):
    # Rate limiting
    if not await rate_limiter.check(request.client.host):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Auth
    token = request.headers.get("Authorization")
    if token:
        user = await verify_token(token)
        request.state.user = user

    return await call_next(request)

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy(service: str, path: str, request: Request):
    target_base = SERVICE_REGISTRY.get(f"/{service}")
    if not target_base:
        raise HTTPException(status_code=404, detail="Service not found")

    target_url = f"{target_base}/{path}"
    if request.query_params:
        target_url += f"?{request.query_params}"

    # Forward request
    response = await client.request(
        method=request.method,
        url=target_url,
        content=await request.body(),
        headers={
            **dict(request.headers),
            "X-User-Id": getattr(request.state, "user_id", ""),
            "X-Request-Id": str(request.state.request_id),
        },
    )

    return StreamingResponse(
        content=response.aiter_bytes(),
        status_code=response.status_code,
        headers=dict(response.headers),
    )
```

## Circuit Breaker

```python
import asyncio
import time
from enum import Enum
from typing import Callable, Any
from functools import wraps

class CircuitState(Enum):
    CLOSED = "closed"         # Normal operation
    OPEN = "open"             # Failing, reject requests
    HALF_OPEN = "half_open"   # Testing if service recovered

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        success_threshold: int = 2,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            await self._before_call()
            try:
                result = await func(*args, **kwargs)
                await self._on_success()
                return result
            except Exception as e:
                await self._on_failure()
                raise

        return wrapper

    async def _before_call(self):
        if self.state == CircuitState.OPEN:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit {self.name} is OPEN. Retry after {self.recovery_timeout - elapsed:.1f}s"
                )

    async def _on_success(self):
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    async def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN

# Usage
payment_breaker = CircuitBreaker("payment-service", failure_threshold=3, recovery_timeout=30)

@payment_breaker
async def call_payment_service(order_id: str, amount: float):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://payment-service/charge", json={"order_id": order_id, "amount": amount})
        response.raise_for_status()
        return response.json()
```

## Event-Driven Communication with Redis Streams

```python
import redis.asyncio as redis
import json
import asyncio
from dataclasses import dataclass, asdict

@dataclass
class OrderCreatedEvent:
    event_type: str = "order.created"
    order_id: str = ""
    user_id: str = ""
    total: float = 0.0
    items: list = None

class EventBus:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.consumer_group = "service-consumers"

    async def publish(self, stream: str, event: dict):
        await self.redis.xadd(stream, {"data": json.dumps(event)})

    async def subscribe(self, stream: str, handler: Callable, consumer_name: str):
        # Create consumer group if not exists
        try:
            await self.redis.xgroup_create(stream, self.consumer_group, id="0", mkstream=True)
        except redis.ResponseError:
            pass  # Group already exists

        while True:
            messages = await self.redis.xreadgroup(
                self.consumer_group,
                consumer_name,
                {stream: ">"},
                count=10,
                block=1000,  # Block for 1 second
            )

            for stream_name, msgs in (messages or []):
                for msg_id, msg_data in msgs:
                    try:
                        event = json.loads(msg_data[b"data"])
                        await handler(event)
                        # Acknowledge successful processing
                        await self.redis.xack(stream, self.consumer_group, msg_id)
                    except Exception as e:
                        print(f"Error processing {msg_id}: {e}")
                        # Don't ack — will be retried

# Publisher (Order Service)
event_bus = EventBus("redis://redis:6379")

async def create_order(order_data: dict) -> dict:
    order = await db.orders.create(order_data)

    await event_bus.publish("orders", {
        "event_type": "order.created",
        "order_id": order["id"],
        "user_id": order["user_id"],
        "total": order["total"],
    })

    return order

# Subscriber (Inventory Service)
async def handle_order_event(event: dict):
    if event["event_type"] == "order.created":
        await reserve_inventory(event["order_id"], event["items"])

asyncio.create_task(
    event_bus.subscribe("orders", handle_order_event, "inventory-service-1")
)
```

## gRPC Service Definition

```protobuf
// proto/user_service.proto
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (GetUserRequest) returns (UserResponse);
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);
  rpc WatchUserActivity (WatchRequest) returns (stream ActivityEvent);
}

message GetUserRequest {
  string user_id = 1;
}

message CreateUserRequest {
  string email = 1;
  string name = 2;
  string role = 3;
}

message UserResponse {
  string id = 1;
  string email = 2;
  string name = 3;
  string role = 4;
  int64 created_at = 5;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
  string role_filter = 3;
}

message WatchRequest {
  string user_id = 1;
}

message ActivityEvent {
  string user_id = 1;
  string action = 2;
  int64 timestamp = 3;
}
```

```python
# gRPC server implementation
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserServiceServicer(user_pb2_grpc.UserServiceServicer):
    async def GetUser(self, request, context):
        user = await db.get_user(request.user_id)
        if not user:
            await context.abort(grpc.StatusCode.NOT_FOUND, f"User {request.user_id} not found")

        return user_pb2.UserResponse(
            id=user["id"],
            email=user["email"],
            name=user["name"],
            role=user["role"],
            created_at=int(user["created_at"].timestamp()),
        )

    async def ListUsers(self, request, context):
        async for user in db.stream_users(page=request.page, page_size=request.page_size):
            yield user_pb2.UserResponse(**user)

async def serve():
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ("grpc.max_send_message_length", 50 * 1024 * 1024),
            ("grpc.max_receive_message_length", 50 * 1024 * 1024),
            ("grpc.keepalive_time_ms", 10000),
        ],
    )
    user_pb2_grpc.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    await server.start()
    await server.wait_for_termination()

# gRPC client with retry and circuit breaker
async def get_user_grpc(user_id: str) -> dict:
    async with grpc.aio.insecure_channel("user-service:50051") as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        try:
            response = await stub.GetUser(
                user_pb2.GetUserRequest(user_id=user_id),
                timeout=5.0,
            )
            return {"id": response.id, "email": response.email, "name": response.name}
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            raise
```

## Service Discovery with Consul

```python
import consul.aio

class ServiceDiscovery:
    def __init__(self, consul_host: str = "consul", consul_port: int = 8500):
        self.consul = consul.aio.Consul(host=consul_host, port=consul_port)
        self._cache = {}

    async def register(self, service_name: str, service_id: str, port: int, tags: list = None):
        await self.consul.agent.service.register(
            name=service_name,
            service_id=service_id,
            port=port,
            tags=tags or [],
            check=consul.Check.http(
                url=f"http://localhost:{port}/health",
                interval="10s",
                timeout="5s",
                deregister="30s",
            ),
        )

    async def deregister(self, service_id: str):
        await self.consul.agent.service.deregister(service_id)

    async def discover(self, service_name: str) -> list[str]:
        """Get healthy service instances."""
        index, services = await self.consul.health.service(
            service_name, passing=True
        )
        return [
            f"http://{svc['Service']['Address']}:{svc['Service']['Port']}"
            for svc in services
        ]

    async def get_one(self, service_name: str) -> str:
        """Get a random healthy instance (simple load balancing)."""
        import random
        instances = await self.discover(service_name)
        if not instances:
            raise RuntimeError(f"No healthy instances of {service_name}")
        return random.choice(instances)
```

## Saga Pattern (Distributed Transactions)

```python
from enum import Enum
from dataclasses import dataclass

class SagaStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"

@dataclass
class SagaStep:
    name: str
    action: Callable
    compensation: Callable  # Rollback action

class OrderSaga:
    """Orchestration-based saga for order creation."""

    steps = [
        SagaStep("reserve_inventory", reserve_inventory, release_inventory),
        SagaStep("charge_payment", charge_payment, refund_payment),
        SagaStep("create_shipment", create_shipment, cancel_shipment),
        SagaStep("send_confirmation", send_email, None),
    ]

    async def execute(self, order_data: dict) -> dict:
        completed_steps = []
        context = {"order_data": order_data, "results": {}}

        for step in self.steps:
            try:
                result = await step.action(context)
                context["results"][step.name] = result
                completed_steps.append(step)
            except Exception as e:
                # Compensate in reverse order
                for completed in reversed(completed_steps):
                    if completed.compensation:
                        try:
                            await completed.compensation(context)
                        except Exception as comp_error:
                            # Log but continue compensation
                            print(f"Compensation failed for {completed.name}: {comp_error}")

                raise OrderCreationError(f"Saga failed at {step.name}: {e}") from e

        return context["results"]
```

## Key Patterns

- **Circuit breaker** prevents cascade failures — open on threshold, test recovery gradually
- **Event sourcing + CQRS** separates read/write models and provides audit trail
- **Saga pattern** manages distributed transactions without 2PC — use choreography for simple flows, orchestration for complex
- **API gateway** handles cross-cutting concerns: auth, rate limiting, routing, observability
- **gRPC** over REST for internal service communication — typed, faster, supports streaming
- **Health endpoints** (`/health`, `/ready`) are required for Kubernetes and service mesh

## Models to Use

- **claude-opus-4-5**: Distributed system design, saga orchestration, service mesh configuration
- **claude-sonnet-4-5**: Circuit breaker implementation, gRPC services, event-driven patterns
- **claude-haiku-3-5**: Health check endpoints, simple service clients, basic routing
