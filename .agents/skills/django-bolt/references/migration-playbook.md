# Migration Playbook

Only use this when the user explicitly asks to port existing code to Django-Bolt.

## From FastAPI

- `FastAPI()` maps to `BoltAPI()`
- `Depends` maps cleanly
- Typed handlers and `response_model` still apply
- Replace uvicorn startup with `python manage.py runbolt --dev`
- `BackgroundTasks` has no direct equivalent; use Django signals or async helpers

## From Django REST Framework

- Keep Django models, admin, and business logic untouched
- Map grouped endpoints to `APIView`
- Map CRUD surfaces to `ViewSet` or `ModelViewSet`
- Map DRF permissions to Bolt guards (`IsAuthenticated`, `HasPermission`, etc.)
- Replace DRF serializers with `Serializer` (for validation) or `msgspec.Struct` (for simple DTOs)
- Replace `@api_view` with `@api.get` / `@api.post` etc.

## From Django Ninja

- `NinjaAPI()` maps to `BoltAPI()`
- Typed path, query, and body handling stays familiar
- Keep OpenAPI metadata and response typing
- Replace `ninja.Router` with additional `BoltAPI()` instances or route grouping

## Migration priority

1. Preserve URL, method, request fields, and response shape
2. Move validation into typed inputs or `Serializer`
3. Recreate auth and permission behavior
4. Recreate docs metadata
5. Add tests with `TestClient`

## Common migration pitfalls

- Forgetting to switch to Django async ORM methods (`aget`, `acreate`, `afirst`, etc.)
- Copying DRF `serializer.is_valid()` patterns instead of letting Django-Bolt validate typed inputs automatically
- Not adding `"django_bolt"` to `INSTALLED_APPS`
- Using `uvicorn` or `gunicorn` instead of `python manage.py runbolt`
