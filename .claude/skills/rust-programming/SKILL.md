---
name: rust-programming
description: Rust expert patterns — ownership, lifetimes, async/tokio, error handling, traits, macros, WebAssembly, systems programming for MAARS Rust agents
---

# Rust Programming — MAARS Reference

## Ownership & Borrowing
```rust
// Move semantics
let s1 = String::from("hello");
let s2 = s1;  // s1 moved, cannot use s1
// let s3 = s1;  // ERROR: use of moved value

// Clone when you need both
let s1 = String::from("hello");
let s2 = s1.clone();  // s1 still valid

// Borrow
fn print_len(s: &String) -> usize {
    s.len()  // borrows, doesn't take ownership
}

// Mutable borrow — only ONE at a time
fn append(s: &mut String) {
    s.push_str(", world");
}

// Slice — reference to contiguous sequence
fn first_word(s: &str) -> &str {
    let bytes = s.as_bytes();
    for (i, &byte) in bytes.iter().enumerate() {
        if byte == b' ' { return &s[0..i]; }
    }
    &s[..]
}
```

## Error Handling
```rust
use std::fmt;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AppError {
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
    
    #[error("Not found: {0}")]
    NotFound(String),
    
    #[error("Validation failed: {field} - {message}")]
    Validation { field: String, message: String },
    
    #[error("Unauthorized")]
    Unauthorized,
}

// Result type alias
type AppResult<T> = Result<T, AppError>;

// The ? operator
async fn get_user(id: i64) -> AppResult<User> {
    let user = db::find_user(id).await?;  // propagates DbError
    user.ok_or(AppError::NotFound(format!("User {id}")))
}

// anyhow for application code
use anyhow::{Context, Result};
fn read_config(path: &str) -> Result<Config> {
    let content = std::fs::read_to_string(path)
        .with_context(|| format!("Failed to read {path}"))?;
    serde_json::from_str(&content).context("Invalid config JSON")
}
```

## Traits & Generics
```rust
use std::fmt::Display;

trait Summary {
    fn summarize(&self) -> String;
    fn preview(&self) -> String {  // default implementation
        format!("{}...", &self.summarize()[..50])
    }
}

// Trait bounds
fn notify<T: Summary + Display>(item: &T) {
    println!("{}: {}", item, item.summarize());
}

// Where clause (cleaner for complex bounds)
fn compare<T>(a: &T, b: &T) -> bool
where
    T: PartialEq + Debug,
{
    if a == b { println!("Equal: {:?}", a); }
    a == b
}

// Return trait objects
fn make_summarizable(is_article: bool) -> Box<dyn Summary> {
    if is_article { Box::new(Article::new()) }
    else { Box::new(Tweet::new()) }
}

// Blanket implementations
impl<T: Display> ToString for T {
    fn to_string(&self) -> String { format!("{}", self) }
}
```

## Async with Tokio
```rust
use tokio::{time, sync::{Mutex, RwLock}};
use std::sync::Arc;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Spawn tasks
    let handle = tokio::spawn(async {
        expensive_computation().await
    });
    
    // Timeout
    let result = tokio::time::timeout(
        std::time::Duration::from_secs(5),
        fetch_data()
    ).await??;
    
    // Select — race multiple futures
    tokio::select! {
        result = task_a() => println!("A finished: {:?}", result),
        result = task_b() => println!("B finished: {:?}", result),
        _ = tokio::signal::ctrl_c() => println!("Shutdown"),
    }
    
    Ok(())
}

// Shared state with Arc<Mutex>
type SharedState = Arc<Mutex<HashMap<String, String>>>;

async fn update_state(state: SharedState, key: String, value: String) {
    let mut map = state.lock().await;
    map.insert(key, value);
}
```

## Common Data Structures
```rust
use std::collections::{HashMap, HashSet, BTreeMap, VecDeque};

// HashMap patterns
let mut scores: HashMap<String, Vec<i32>> = HashMap::new();
scores.entry("Alice".to_string()).or_insert_with(Vec::new).push(95);

// Iterate
for (name, score_list) in &scores {
    let avg: f64 = score_list.iter().sum::<i32>() as f64 / score_list.len() as f64;
    println!("{}: {:.1}", name, avg);
}

// Vec operations
let mut v = vec![3, 1, 4, 1, 5, 9, 2, 6];
v.sort();
v.dedup();
let evens: Vec<_> = v.iter().filter(|&&x| x % 2 == 0).collect();
let doubled: Vec<_> = v.iter().map(|&x| x * 2).collect();
let sum: i32 = v.iter().sum();
```

## Serde (Serialization)
```rust
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Debug, Clone)]
#[serde(rename_all = "camelCase")]
pub struct User {
    pub id: i64,
    pub email: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub avatar_url: Option<String>,
    #[serde(default)]
    pub is_admin: bool,
    #[serde(rename = "created_at")]
    pub created_at: chrono::DateTime<chrono::Utc>,
}

// JSON
let json = serde_json::to_string(&user)?;
let user: User = serde_json::from_str(&json)?;

// With custom deserializer
#[serde(deserialize_with = "deserialize_from_str")]
pub amount: Decimal,
```

## Axum Web Framework
```rust
use axum::{extract::{Path, State, Json}, Router, routing::*};
use tower_http::cors::CorsLayer;

#[derive(Clone)]
struct AppState { db: sqlx::PgPool }

async fn get_user(
    State(state): State<AppState>,
    Path(id): Path<i64>,
) -> Result<Json<User>, AppError> {
    let user = sqlx::query_as!(User, "SELECT * FROM users WHERE id = $1", id)
        .fetch_optional(&state.db).await?
        .ok_or(AppError::NotFound(format!("User {id}")))?;
    Ok(Json(user))
}

let app = Router::new()
    .route("/users/:id", get(get_user))
    .route("/users", post(create_user))
    .with_state(AppState { db })
    .layer(CorsLayer::permissive());
```

## Models to Use
- **Rust code generation**: `claude-opus-4-6` (best for Rust's complex type system)
- **Lifetime fixes**: `claude-opus-4-6`
- **Performance optimization**: `claude-opus-4-6`
- **FFI / unsafe code review**: `claude-opus-4-6`
