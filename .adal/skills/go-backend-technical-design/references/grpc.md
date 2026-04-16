# gRPC Design Notes

Use when the service exposes internal RPC APIs or high-throughput contracts.

## Guidelines

- Keep protobuf contracts stable and explicit.
- Separate transport protobuf models from domain models.
- Define timeout and retry expectations per method.
- Make idempotency explicit for write methods.
- Normalize error mapping from domain errors to gRPC status codes.

## Checklist

- service ownership clear
- versioning or evolution path clear
- request and response fields are minimal
- deadlines enforced
- observability interceptors defined
