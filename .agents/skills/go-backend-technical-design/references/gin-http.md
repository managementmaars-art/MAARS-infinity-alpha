# Gin HTTP Design Notes

Use when the Go service is HTTP-first and Gin is already the transport framework.

## Guidelines

- Keep handlers thin.
- Bind and validate request DTOs at the edge.
- Map DTOs to application commands explicitly.
- Avoid passing `gin.Context` into domain or repository layers.
- Extract `context.Context` from the request and pass only that downward.

## Preferred flow

handler -> app service -> domain/repository -> presenter/response mapper

## Pitfalls

- business logic inside middleware
- direct DB access from handlers
- hidden status-code branching across services
