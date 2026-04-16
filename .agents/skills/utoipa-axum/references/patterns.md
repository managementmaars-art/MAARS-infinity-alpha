# utoipa + Axum Patterns

Common patterns for building OpenAPI-documented Axum APIs.

## Project Structure

```
src/
├── main.rs
├── lib.rs
├── openapi.rs          # ApiDoc definition
├── state.rs            # AppState
├── handlers/
│   ├── mod.rs
│   ├── users.rs
│   ├── posts.rs
│   └── health.rs
├── models/
│   ├── mod.rs
│   ├── user.rs
│   └── error.rs
└── middleware/
    ├── mod.rs
    └── auth.rs
```

## Error Response Pattern

```rust
use axum::{http::StatusCode, response::IntoResponse, Json};
use serde::Serialize;
use utoipa::ToSchema;

#[derive(Debug, Serialize, ToSchema)]
pub struct ApiError {
    pub error: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub code: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub details: Option<serde_json::Value>,
}

impl ApiError {
    pub fn new(error: impl Into<String>) -> Self {
        Self {
            error: error.into(),
            code: None,
            details: None,
        }
    }

    pub fn with_code(mut self, code: impl Into<String>) -> Self {
        self.code = Some(code.into());
        self
    }
}

// Tuple response type for handlers
pub type ApiResult<T> = Result<Json<T>, (StatusCode, Json<ApiError>)>;

// Or with status code for creation
pub type ApiResultCreated<T> = Result<(StatusCode, Json<T>), (StatusCode, Json<ApiError>)>;

// Helper functions
pub fn ok<T: Serialize>(data: T) -> ApiResult<T> {
    Ok(Json(data))
}

pub fn created<T: Serialize>(data: T) -> ApiResultCreated<T> {
    Ok((StatusCode::CREATED, Json(data)))
}

pub fn bad_request(msg: impl Into<String>) -> (StatusCode, Json<ApiError>) {
    (StatusCode::BAD_REQUEST, Json(ApiError::new(msg)))
}

pub fn not_found(msg: impl Into<String>) -> (StatusCode, Json<ApiError>) {
    (StatusCode::NOT_FOUND, Json(ApiError::new(msg)))
}

pub fn internal_error() -> (StatusCode, Json<ApiError>) {
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(ApiError::new("Internal server error")),
    )
}
```

## Handler with Full Documentation

```rust
use axum::{extract::{Path, Query, State}, http::StatusCode, Json};
use uuid::Uuid;

#[derive(Debug, Deserialize, IntoParams)]
pub struct ListUsersQuery {
    #[param(minimum = 1, default = 1)]
    pub page: Option<u32>,
    #[param(minimum = 1, maximum = 100, default = 20)]
    pub limit: Option<u32>,
    pub status: Option<UserStatus>,
    pub search: Option<String>,
}

#[derive(Debug, Serialize, ToSchema)]
pub struct ListUsersResponse {
    pub users: Vec<UserResponse>,
    pub total: u64,
    pub page: u32,
    pub limit: u32,
}

/// List users with pagination and filters
#[utoipa::path(
    get,
    path = "/api/users",
    tag = "users",
    params(ListUsersQuery),
    responses(
        (status = 200, description = "Users list", body = ListUsersResponse),
        (status = 401, description = "Unauthorized", body = ApiError),
        (status = 500, description = "Server error", body = ApiError)
    ),
    security(("bearer" = []))
)]
pub async fn list_users(
    State(state): State<AppState>,
    Query(params): Query<ListUsersQuery>,
) -> ApiResult<ListUsersResponse> {
    let page = params.page.unwrap_or(1);
    let limit = params.limit.unwrap_or(20);
    
    // ... fetch from database
    
    ok(ListUsersResponse {
        users: vec![],
        total: 0,
        page,
        limit,
    })
}
```

## Authentication Extractor

```rust
use axum::{
    async_trait,
    extract::FromRequestParts,
    http::{request::Parts, StatusCode},
    Json,
};

#[derive(Debug, Clone)]
pub struct AuthUser {
    pub id: Uuid,
    pub email: String,
}

#[async_trait]
impl<S> FromRequestParts<S> for AuthUser
where
    S: Send + Sync,
{
    type Rejection = (StatusCode, Json<ApiError>);

    async fn from_request_parts(parts: &mut Parts, _state: &S) -> Result<Self, Self::Rejection> {
        let auth_header = parts
            .headers
            .get("Authorization")
            .and_then(|h| h.to_str().ok())
            .ok_or_else(|| {
                (
                    StatusCode::UNAUTHORIZED,
                    Json(ApiError::new("Missing authorization header")),
                )
            })?;

        let token = auth_header
            .strip_prefix("Bearer ")
            .ok_or_else(|| {
                (
                    StatusCode::UNAUTHORIZED,
                    Json(ApiError::new("Invalid authorization header")),
                )
            })?;

        // Validate JWT and extract user
        let user = validate_token(token).map_err(|_| {
            (
                StatusCode::UNAUTHORIZED,
                Json(ApiError::new("Invalid token")),
            )
        })?;

        Ok(user)
    }
}

// Use in handler - automatically requires auth in implementation
// but must document with security() in utoipa::path
#[utoipa::path(
    get,
    path = "/api/me",
    tag = "users",
    responses(
        (status = 200, body = UserResponse),
        (status = 401, body = ApiError)
    ),
    security(("bearer" = []))
)]
pub async fn get_current_user(user: AuthUser) -> ApiResult<UserResponse> {
    ok(UserResponse {
        id: user.id,
        email: user.email,
        name: None,
    })
}
```

## Modular OpenAPI Definition

```rust
// src/handlers/users.rs
pub mod users {
    // ... handlers and types

    // Tags constant for consistency
    pub const TAG: &str = "users";
}

// src/handlers/posts.rs
pub mod posts {
    pub const TAG: &str = "posts";
}

// src/openapi.rs
use utoipa::{Modify, OpenApi};
use utoipa::openapi::security::*;

use crate::handlers::{users, posts, health};
use crate::models::error::ApiError;

#[derive(OpenApi)]
#[openapi(
    info(
        title = "My API",
        version = "1.0.0"
    ),
    tags(
        (name = users::TAG, description = "User operations"),
        (name = posts::TAG, description = "Post operations"),
        (name = "health", description = "Health checks")
    ),
    paths(
        // Health
        health::health_check,
        
        // Users
        users::list_users,
        users::get_user,
        users::create_user,
        users::update_user,
        users::delete_user,
        
        // Posts
        posts::list_posts,
        posts::get_post,
        posts::create_post,
    ),
    components(
        schemas(
            // Common
            ApiError,
            
            // Users
            users::UserResponse,
            users::CreateUserRequest,
            users::UpdateUserRequest,
            users::ListUsersResponse,
            
            // Posts
            posts::PostResponse,
            posts::CreatePostRequest,
        )
    ),
    modifiers(&SecurityAddon)
)]
pub struct ApiDoc;

struct SecurityAddon;

impl Modify for SecurityAddon {
    fn modify(&self, openapi: &mut utoipa::openapi::OpenApi) {
        let components = openapi.components.get_or_insert_with(Default::default);
        components.add_security_scheme(
            "bearer",
            SecurityScheme::Http(Http::new(HttpAuthScheme::Bearer)),
        );
    }
}
```

## Router Setup

```rust
use axum::{routing::{get, post, put, delete}, Router};
use utoipa::OpenApi;
use utoipa_scalar::{Scalar, Servable};

use crate::openapi::ApiDoc;
use crate::handlers::{health, users, posts};
use crate::state::AppState;

pub fn create_router(state: AppState) -> Router {
    Router::new()
        // OpenAPI docs
        .merge(Scalar::with_url("/docs", ApiDoc::openapi()))
        
        // Health
        .route("/health", get(health::health_check))
        
        // Users
        .route("/api/users", get(users::list_users).post(users::create_user))
        .route(
            "/api/users/{id}",
            get(users::get_user)
                .put(users::update_user)
                .delete(users::delete_user),
        )
        
        // Posts
        .route("/api/posts", get(posts::list_posts).post(posts::create_post))
        .route("/api/posts/{id}", get(posts::get_post))
        
        .with_state(state)
}
```

## File Upload

```rust
use axum::extract::Multipart;

#[derive(Debug, Serialize, ToSchema)]
pub struct UploadResponse {
    pub file_id: String,
    pub filename: String,
    pub size: u64,
}

#[utoipa::path(
    post,
    path = "/api/upload",
    tag = "files",
    request_body(
        content = Vec<u8>,
        content_type = "multipart/form-data"
    ),
    responses(
        (status = 200, body = UploadResponse),
        (status = 400, body = ApiError)
    )
)]
pub async fn upload_file(mut multipart: Multipart) -> ApiResult<UploadResponse> {
    while let Some(field) = multipart.next_field().await.map_err(|_| bad_request("Invalid multipart"))? {
        let filename = field.file_name().unwrap_or("unknown").to_string();
        let data = field.bytes().await.map_err(|_| bad_request("Failed to read file"))?;
        
        // Save file...
        
        return ok(UploadResponse {
            file_id: Uuid::new_v4().to_string(),
            filename,
            size: data.len() as u64,
        });
    }
    
    Err(bad_request("No file provided"))
}
```

## Pagination Helper

```rust
#[derive(Debug, Deserialize, IntoParams)]
pub struct PaginationParams {
    #[param(minimum = 1, default = 1)]
    pub page: Option<u32>,
    #[param(minimum = 1, maximum = 100, default = 20)]
    pub per_page: Option<u32>,
}

impl PaginationParams {
    pub fn offset(&self) -> u64 {
        let page = self.page.unwrap_or(1).max(1);
        let per_page = self.per_page.unwrap_or(20);
        ((page - 1) * per_page) as u64
    }

    pub fn limit(&self) -> u64 {
        self.per_page.unwrap_or(20).min(100) as u64
    }
}

#[derive(Debug, Serialize, ToSchema)]
pub struct PaginatedResponse<T: ToSchema> {
    pub items: Vec<T>,
    pub total: u64,
    pub page: u32,
    pub per_page: u32,
    pub total_pages: u32,
}

impl<T: ToSchema> PaginatedResponse<T> {
    pub fn new(items: Vec<T>, total: u64, params: &PaginationParams) -> Self {
        let per_page = params.per_page.unwrap_or(20);
        Self {
            items,
            total,
            page: params.page.unwrap_or(1),
            per_page,
            total_pages: ((total as f64) / (per_page as f64)).ceil() as u32,
        }
    }
}
```

## Versioned API

```rust
// v1/mod.rs
pub mod v1 {
    use utoipa::OpenApi;

    #[derive(OpenApi)]
    #[openapi(
        info(title = "API v1", version = "1.0.0"),
        paths(list_users_v1, get_user_v1),
        components(schemas(UserResponseV1))
    )]
    pub struct ApiDocV1;
}

// v2/mod.rs
pub mod v2 {
    #[derive(OpenApi)]
    #[openapi(
        info(title = "API v2", version = "2.0.0"),
        paths(list_users_v2, get_user_v2),
        components(schemas(UserResponseV2))
    )]
    pub struct ApiDocV2;
}

// Serve both
Router::new()
    .merge(Scalar::with_url("/docs/v1", ApiDocV1::openapi()))
    .merge(Scalar::with_url("/docs/v2", ApiDocV2::openapi()))
    .nest("/api/v1", v1_routes())
    .nest("/api/v2", v2_routes())
```

## Testing

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use axum::{body::Body, http::{Request, StatusCode}};
    use tower::ServiceExt;

    #[tokio::test]
    async fn test_list_users() {
        let app = create_router(test_state());

        let response = app
            .oneshot(
                Request::builder()
                    .uri("/api/users")
                    .header("Authorization", "Bearer test-token")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::OK);
    }

    #[tokio::test]
    async fn test_openapi_spec() {
        use utoipa::OpenApi;
        
        let spec = ApiDoc::openapi();
        let json = spec.to_json().unwrap();
        
        // Validate spec structure
        let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed["openapi"], "3.1.0");
        assert!(parsed["paths"]["/api/users"].is_object());
    }
}
```

## Export OpenAPI Spec at Build Time

```rust
// build.rs
use std::fs;

fn main() {
    // Only run when building for release or explicitly requested
    if std::env::var("EXPORT_OPENAPI").is_ok() {
        use utoipa::OpenApi;
        
        let spec = crate::openapi::ApiDoc::openapi();
        fs::write("openapi.json", spec.to_json().unwrap()).unwrap();
        fs::write("openapi.yaml", spec.to_yaml().unwrap()).unwrap();
    }
}
```

Or as a binary:

```rust
// src/bin/export_openapi.rs
use myapi::openapi::ApiDoc;
use utoipa::OpenApi;

fn main() {
    let spec = ApiDoc::openapi();
    println!("{}", spec.to_json().unwrap());
}
```

Run: `cargo run --bin export_openapi > openapi.json`
