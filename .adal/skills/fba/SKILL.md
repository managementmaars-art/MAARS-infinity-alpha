---
name: fba
description: FastAPI Best Architecture (fba) project development guide. Provide complete architecture specifications, coding styles, and plugin development guidance.
metadata:
  author: FastAPI practices team
  version: 2026-02-25
---

# FastAPI Best Architecture

Official documentation: https://fastapi-practices.github.io/fastapi_best_architecture_docs/

## Core Architecture

Project adopts **Three-tier architecture**:

| Layer   | Responsibility                                                     |
|---------|--------------------------------------------------------------------|
| API     | Route processing, parameter validation, and response return        |
| Schema  | Data transfer objects, request/response data structure definitions |
| Service | Business logic, data processing, exception handling                |
| CRUD    | Database operations (inherits `CRUDPlus`)                          |
| Model   | ORM models (inherits `Base`)                                       |

## Development Workflow

1. Define database models (model)
2. Define data validation models (schema)
3. Define routes (router)
4. Write business logic (service)
5. Write database operations (crud)

## Detailed Guides

| Module       | Document                   |
|--------------|----------------------------|
| API          | references/api.md          |
| Schema       | references/schema.md       |
| Model        | references/model.md        |
| Naming       | references/naming.md       |
| Plugin       | references/plugin.md       |
| Coding Style | references/coding-style.md |
| Config       | references/config.md       |

## CLI

Execute `fba -h` for more details.