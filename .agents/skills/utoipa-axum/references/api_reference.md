# utoipa API Reference

Complete reference for utoipa macros and attributes.

## ToSchema Derive

```rust
use utoipa::ToSchema;
```

### Container Attributes

```rust
#[derive(ToSchema)]
#[schema(
    // Alternative name in OpenAPI spec
    as = path::to::Schema,
    // Rename all fields
    rename_all = "camelCase",
    // Add example for entire schema
    example = json!({"email": "user@example.com"}),
    // Mark as deprecated
    deprecated,
    // Title in spec
    title = "User Request",
    // Override description
    description = "Request body for creating user"
)]
pub struct MySchema { ... }
```

### Field Attributes

```rust
#[derive(ToSchema)]
pub struct User {
    /// Field description from doc comment
    pub id: Uuid,

    #[schema(example = "user@example.com")]
    pub email: String,

    #[schema(min_length = 8, max_length = 128)]
    pub password: String,

    #[schema(minimum = 0, maximum = 150)]
    pub age: u8,

    #[schema(pattern = r"^\+[1-9]\d{1,14}$")]
    pub phone: String,

    // Override type in spec
    #[schema(value_type = String, format = "date-time")]
    pub created_at: DateTime<Utc>,

    // Nullable field
    #[schema(nullable)]
    pub deleted_at: Option<DateTime<Utc>>,

    // Read-only (only in GET responses)
    #[schema(read_only)]
    pub computed_field: String,

    // Write-only (only in POST/PUT/PATCH)
    #[schema(write_only)]
    pub password_confirm: String,

    // Default value
    #[schema(default = "active")]
    pub status: String,

    // Custom schema
    #[schema(schema_with = custom_schema)]
    pub custom: MyType,
}
```

### Enum Schemas

```rust
// Simple enum
#[derive(ToSchema)]
pub enum Status {
    Active,
    Inactive,
    Pending,
}

// Enum with serde rename
#[derive(ToSchema)]
#[serde(rename_all = "SCREAMING_SNAKE_CASE")]
pub enum Priority {
    Low,
    Medium,
    High,
}

// Tagged enum
#[derive(ToSchema)]
#[serde(tag = "type", rename_all = "snake_case")]
pub enum Event {
    Created { id: Uuid },
    Updated { id: Uuid, changes: Vec<String> },
    Deleted { id: Uuid },
}

// Untagged enum
#[derive(ToSchema)]
#[serde(untagged)]
pub enum IdOrSlug {
    Id(Uuid),
    Slug(String),
}

// Integer repr enum
#[derive(ToSchema)]
#[repr(i32)]
pub enum HttpCode {
    Ok = 200,
    Created = 201,
    BadRequest = 400,
}
```

### Generic Schemas

```rust
#[derive(ToSchema)]
pub struct PaginatedResponse<T: ToSchema> {
    pub items: Vec<T>,
    pub total: u64,
    pub page: u32,
    pub per_page: u32,
}

// When registering, use concrete type
#[openapi(components(schemas(PaginatedResponse<UserResponse>)))]
```

## #[utoipa::path] Macro

### HTTP Methods

```rust
#[utoipa::path(get, path = "/users")]
#[utoipa::path(post, path = "/users")]
#[utoipa::path(put, path = "/users/{id}")]
#[utoipa::path(patch, path = "/users/{id}")]
#[utoipa::path(delete, path = "/users/{id}")]
#[utoipa::path(head, path = "/users")]
#[utoipa::path(options, path = "/users")]

// Multiple methods
#[utoipa::path(method(get, head), path = "/users")]
```

### Path Parameters

```rust
#[utoipa::path(
    get,
    path = "/users/{id}/posts/{post_id}",
    params(
        ("id" = Uuid, Path, description = "User ID"),
        ("post_id" = i64, Path, description = "Post ID")
    )
)]
```

### Query Parameters

```rust
#[utoipa::path(
    get,
    path = "/users",
    params(
        ("page" = Option<u32>, Query, description = "Page number"),
        ("limit" = Option<u32>, Query, description = "Items per page"),
        ("status" = Option<Status>, Query, description = "Filter by status")
    )
)]

// Or use IntoParams struct
#[utoipa::path(
    get,
    path = "/users",
    params(PaginationParams, UserFilters)
)]
```

### Request Body

```rust
// Simple
#[utoipa::path(
    post,
    path = "/users",
    request_body = CreateUserRequest
)]

// With options
#[utoipa::path(
    post,
    path = "/users",
    request_body(
        content = CreateUserRequest,
        description = "User creation payload",
        content_type = "application/json"
    )
)]

// Inline schema (not referenced)
#[utoipa::path(
    post,
    path = "/upload",
    request_body = inline(UploadRequest)
)]

// Multiple content types
#[utoipa::path(
    post,
    path = "/data",
    request_body(
        content(
            (CreateRequest = "application/json"),
            (CreateRequestXml = "application/xml")
        )
    )
)]
```

### Responses

```rust
#[utoipa::path(
    get,
    path = "/users/{id}",
    responses(
        (status = 200, description = "Success", body = UserResponse),
        (status = 400, description = "Bad request", body = ErrorResponse),
        (status = 401, description = "Unauthorized"),
        (status = 404, description = "Not found", body = ErrorResponse),
        (status = 500, description = "Server error", body = ErrorResponse)
    )
)]

// With headers
#[utoipa::path(
    get,
    path = "/users",
    responses(
        (status = 200, body = Vec<UserResponse>,
         headers(
             ("X-Total-Count" = i64, description = "Total items"),
             ("X-Page" = i32, description = "Current page")
         ))
    )
)]

// Response ranges
#[utoipa::path(
    responses(
        (status = "2XX", description = "Success"),
        (status = "4XX", description = "Client error"),
        (status = "5XX", description = "Server error")
    )
)]

// Multiple content types in response
#[utoipa::path(
    responses(
        (status = 200, content(
            (UserResponse = "application/json"),
            (UserResponseXml = "application/xml")
        ))
    )
)]
```

### Security

```rust
// Require bearer token
#[utoipa::path(
    security(("bearer" = []))
)]

// Require API key
#[utoipa::path(
    security(("api_key" = []))
)]

// OAuth with scopes
#[utoipa::path(
    security(("oauth2" = ["read:users", "write:users"]))
)]

// Multiple options (OR)
#[utoipa::path(
    security(
        ("bearer" = []),
        ("api_key" = [])
    )
)]

// Optional security (empty = no auth required)
#[utoipa::path(
    security(
        (),
        ("bearer" = [])
    )
)]
```

### Tags and Metadata

```rust
#[utoipa::path(
    get,
    path = "/users",
    tag = "users",
    operation_id = "list_users",
    summary = "List all users",
    description = "Returns paginated list of users"
)]

// Multiple tags
#[utoipa::path(
    tags = ["users", "admin"]
)]

// Context path prefix
#[utoipa::path(
    context_path = "/api/v1",
    path = "/users"  // Becomes /api/v1/users
)]

// Deprecated endpoint
#[deprecated]
#[utoipa::path(...)]
```

## IntoParams Derive

```rust
use utoipa::IntoParams;

#[derive(Deserialize, IntoParams)]
pub struct Pagination {
    #[param(minimum = 1, default = 1, example = 1)]
    pub page: Option<u32>,

    #[param(minimum = 1, maximum = 100, default = 20)]
    pub per_page: Option<u32>,

    #[param(style = Form, explode = true)]
    pub sort: Option<Vec<String>>,

    #[param(rename = "q")]
    pub query: Option<String>,

    #[param(nullable)]
    pub filter: Option<String>,
}

// For path parameters
#[derive(Deserialize, IntoParams)]
#[into_params(parameter_in = Path)]
pub struct UserPath {
    pub id: Uuid,
}
```

### Param Attributes

```rust
#[param(
    // Examples
    example = "value",
    examples("val1", "val2"),

    // Validation
    minimum = 0,
    maximum = 100,
    exclusive_minimum = 0,
    exclusive_maximum = 100,
    min_length = 1,
    max_length = 255,
    pattern = r"^\d+$",
    multiple_of = 5,
    min_items = 1,
    max_items = 10,

    // Metadata
    rename = "apiName",
    deprecated,
    nullable,
    required,

    // Format
    value_type = String,
    format = "uuid",

    // Style
    style = Form,     // Query default
    style = Simple,   // Path default
    explode = true,
)]
```

## OpenApi Derive

```rust
#[derive(OpenApi)]
#[openapi(
    info(
        title = "My API",
        version = "1.0.0",
        description = "API description",
        license(name = "MIT"),
        contact(
            name = "Support",
            email = "support@example.com",
            url = "https://example.com"
        )
    ),
    servers(
        (url = "https://api.example.com", description = "Production"),
        (url = "https://staging.example.com", description = "Staging")
    ),
    tags(
        (name = "users", description = "User operations"),
        (name = "posts", description = "Post operations")
    ),
    paths(
        list_users,
        get_user,
        create_user,
        update_user,
        delete_user
    ),
    components(
        schemas(
            UserResponse,
            CreateUserRequest,
            UpdateUserRequest,
            ErrorResponse,
            PaginatedResponse<UserResponse>
        ),
        responses(
            NotFound,
            Unauthorized
        )
    ),
    modifiers(&SecurityAddon),
    external_docs(
        url = "https://docs.example.com",
        description = "External documentation"
    )
)]
pub struct ApiDoc;
```

## Security Schemes

```rust
use utoipa::openapi::security::*;

struct SecurityAddon;

impl Modify for SecurityAddon {
    fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
        let components = openapi.components.get_or_insert_with(Default::default);

        // Bearer token
        components.add_security_scheme(
            "bearer",
            SecurityScheme::Http(Http::new(HttpAuthScheme::Bearer)),
        );

        // API Key in header
        components.add_security_scheme(
            "api_key",
            SecurityScheme::ApiKey(ApiKey::Header(ApiKeyValue::new("X-API-Key"))),
        );

        // API Key in query
        components.add_security_scheme(
            "api_key_query",
            SecurityScheme::ApiKey(ApiKey::Query(ApiKeyValue::new("api_key"))),
        );

        // OAuth2
        components.add_security_scheme(
            "oauth2",
            SecurityScheme::OAuth2(OAuth2::new([
                Flow::AuthorizationCode(AuthorizationCode::new(
                    "https://auth.example.com/authorize",
                    "https://auth.example.com/token",
                    Scopes::from_iter([
                        ("read:users", "Read users"),
                        ("write:users", "Create/update users"),
                    ]),
                )),
            ])),
        );
    }
}
```

## ToResponse Derive

```rust
use utoipa::ToResponse;

#[derive(ToResponse)]
#[response(description = "User not found")]
pub struct NotFound {
    pub message: String,
}

#[derive(ToResponse)]
#[response(
    description = "Validation error",
    content_type = "application/json",
    headers(
        ("X-Request-Id" = String, description = "Request ID")
    )
)]
pub struct ValidationError {
    pub errors: Vec<FieldError>,
}

// Use in responses
#[utoipa::path(
    responses(
        (status = 404, response = NotFound)
    )
)]
```

## IntoResponses Derive

```rust
use utoipa::IntoResponses;

#[derive(IntoResponses)]
pub enum UserResponses {
    #[response(status = 200, description = "Success")]
    Ok(UserResponse),

    #[response(status = 404, description = "Not found")]
    NotFound(ErrorResponse),

    #[response(status = 500, description = "Server error")]
    Error(ErrorResponse),
}

#[utoipa::path(
    responses(UserResponses)
)]
```
