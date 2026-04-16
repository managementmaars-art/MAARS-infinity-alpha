---
name: web-wasm
cluster: web-dev
description: "WebAssembly: Rust/Go/C to WASM, wasm-bindgen, Emscripten, WASM Component Model"
tags: ["wasm","webassembly","rust","performance","web"]
dependencies: []
composes: []
similar_to: []
called_by: []
authorization_required: false
scope: general
model_hint: claude-sonnet
embedding_hint: "webassembly wasm rust go compile browser performance emscripten"
---

# web-wasm

## Purpose
This skill enables the AI to compile and integrate code from Rust, Go, or C into WebAssembly (WASM) for high-performance web applications, using tools like wasm-bindgen, Emscripten, and the WASM Component Model.

## When to Use
Use this skill for browser-based tasks requiring speed, such as running simulations, processing large datasets, or porting legacy C/C++ code to the web. Apply it when JavaScript performance is insufficient, or when working with languages like Rust for safe, concurrent code in the browser.

## Key Capabilities
- Compile Rust to WASM with wasm-pack, including generating JavaScript bindings via wasm-bindgen.
- Convert C/C++ to WASM using Emscripten, with options for HTML output and memory management.
- Support Go to WASM via TinyGo, enabling lightweight modules.
- Handle WASM Component Model for composing modules, using tools like wasm-tools for interface definitions.
- Optimize for performance with flags like Emscripten's `-s ALLOW_MEMORY_GROWTH=1` for dynamic memory.

## Usage Patterns
To compile Rust to WASM, first ensure dependencies: install Rust via rustup and wasm-pack via `cargo install wasm-pack`. In your project directory, add wasm-bindgen to Cargo.toml, write annotated code, then run `wasm-pack build --target web --release`. For C/C++, install Emscripten SDK, set up with `emsdk install latest && emsdk activate latest`, then compile files with `emcc`. Always verify outputs in a browser by loading the generated JS and WASM files.

## Common Commands/API
- Rust to WASM: Use `wasm-pack build --target web --no-pack --release` to generate .wasm and .js files. Example: In Cargo.toml, add `[lib] crate-type = ["cdylib"]`. Snippet:
  ```rust
  use wasm_bindgen::prelude::*;
  #[wasm_bindgen]
  pub fn multiply(a: f64, b: f64) -> f64 { a * b }
  ```
- C/C++ with Emscripten: Command: `emcc input.c -s WASM=1 -o output.js -s EXPORTED_FUNCTIONS='["_main"]'`. Config format: Use .emscripten file for settings like `MEMORY64: 1`. Snippet:
  ```c
  #include <emscripten/emscripten.h>
  EMSCRIPTEN_KEEPALIVE int add(int a, int b) { return a + b; }
  ```
- Go to WASM: Use TinyGo with `tinygo build -o output.wasm -target wasm`. API: For WASM Component Model, define interfaces in WIT format, e.g., `package mypkg: interface { func add(a: s32) s32; }`.
- Authentication: If using cloud WASM services (e.g., for optimization APIs), set env vars like `export WASM_API_KEY=$SERVICE_API_KEY` and pass via flags, e.g., `wasm-pack build --header "Authorization: Bearer $WASM_API_KEY"`.

## Integration Notes
Integrate WASM modules into web projects by including generated files in HTML: `<script src="output.js"></script>` and ensure the WASM file is fetched. For Rust, link with JavaScript using `import * as wasm from './mywasm.js'; console.log(wasm.add(1, 2));`. Config formats: Use package.json for npm integration, e.g., `"scripts": { "build:wasm": "wasm-pack build" }`. For Emscripten, set `$EMSCRIPTEN` env var to the SDK path. If combining with other skills, chain outputs: e.g., after building WASM, use a web-http skill to serve files via an API endpoint like `/api/wasm-output`.

## Error Handling
Handle compilation errors by checking logs: For wasm-pack, look for "error: linking with `link` failed" and resolve with `rustup update`. Emscripten errors often involve missing exports; use `emcc --help` and add flags like `-s ASSERTIONS=1` for detailed runtime errors. Debug in-browser with Chrome DevTools: Inspect console for WASM traps, e.g., "WebAssembly: Out of bounds memory access". Common patterns: Wrap code in try-catch, e.g., in JS: `try { wasm.add(1, 'string'); } catch (e) { console.error(e.message); }`. For Go, check TinyGo logs for "undefined symbol" and ensure imports are correct.

## Concrete Usage Examples
1. Rust function for matrix multiplication: Create a new Rust lib with `cargo new --lib matrix-wasm`. Add to Cargo.toml: `[dependencies] wasm-bindgen = "0.2"`. In src/lib.rs:
   ```rust
   use wasm_bindgen::prelude::*;
   #[wasm_bindgen]
   pub fn multiply_matrices(a: &[f64], b: &[f64]) -> Vec<f64> { /* implementation */ }
   ```
   Build with `wasm-pack build --target web --release`. Integrate in HTML: `<script>import * as mod from './matrix_wasm.js'; console.log(mod.multiply_matrices([1,2], [3,4]));</script>`.

2. C code for image processing: Write hello.c: 
   ```c
   #include <emscripten/emscripten.h>
   EMSCRIPTEN_KEEPALIVE void process_image(int* data, int size) { /* process array */ }
   ```
   Compile with `emcc hello.c -s WASM=1 -o hello.js -s EXPORTED_FUNCTIONS='["_process_image"]'`. Load in browser: `<script src="hello.js"></script><script>Module.process_image(new Int32Array([1,2,3]), 3);</script>`.

## Graph Relationships
- Cluster: web-dev (directly related to skills like web-http for serving WASM files, and web-frontend for UI integration).
- Tags: wasm (connects to performance skills for optimization), webassembly (links to browser-related skills like web-dom), rust (associated with rust-dev for ecosystem tools), go (ties to go-backend for server-side compilation), web (overlaps with web-security for safe WASM execution).
