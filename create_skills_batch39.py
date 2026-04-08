
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Programming paradigms and niche languages
    ('haskell-advanced', 'Haskell advanced - typeclasses, monads, GADTs, type families, Template Haskell, STM, profiling'),
    ('ocaml-advanced', 'OCaml advanced - modules, functors, effects, Dune, ppx, Lwt, Eio, native compilation'),
    ('erlang-advanced', 'Erlang advanced - OTP, gen_server, supervisors, distribution, mnesia, NIFs, releases, tracing'),
    ('elixir-advanced', 'Elixir advanced - macros, protocols, behaviours, GenServer, Phoenix, Nerves, distributed, debugging'),
    ('clojure-advanced', 'Clojure advanced - macros, transducers, core.async, specs, ClojureScript, reducers, REPL'),
    ('f-sharp-advanced', 'F# advanced - computation expressions, type providers, discriminated unions, actor model, FSLAB'),
    ('scala-advanced', 'Scala advanced - cats, ZIO, Akka, implicit, type classes, macros, Scala Native, Spark'),
    ('kotlin-advanced', 'Kotlin advanced - coroutines, delegates, DSL construction, multiplatform, Arrow, compiler plugins'),
    ('swift-advanced', 'Swift advanced - actors, sendable, result builders, property wrappers, macros, Swift NIO, concurrency'),
    ('nim-programming', 'Nim programming - macros, templates, concepts, async, FFI, compiletime, pragmas, nimble'),
    ('crystal-lang', 'Crystal language - fibers, channels, macros, LLVM, C bindings, specs, shards, performance'),
    ('julia-advanced', 'Julia advanced - multiple dispatch, metaprogramming, parallel, GPU, differential equations, Turing'),
    ('d-language', 'D programming language - templates, mixins, CTFE, ranges, GC, nothrow, betterC, Phobos'),
    ('v-lang', 'V language - memory safety without GC, C interop, compile-time, web framework, native GUI'),
    ('zig-advanced', 'Zig advanced - comptime, allocators, build system, C interop, error unions, async, WASM'),
    ('odin-lang', 'Odin language - procedures, bit fields, context system, vendor libraries, demo projects'),
    ('factor-lang', 'Factor concatenative language - stack effects, words, quotations, vocabs, UI, REPL, deploy'),
    ('forth-lang', 'Forth programming - stack, words, compilation, embedded, Gforth, ANSI Forth, retro computing'),
    ('j-language', 'J array programming language - verbs, adverbs, conjunctions, trains, rank, boxes, tacit'),
    ('apl-advanced', 'APL advanced - array operations, dfns, tacit programming, Dyalog APL, namespace, parallel'),
    ('racket-advanced', 'Racket advanced - macros, #lang, continuations, contracts, Typed Racket, web server'),
    ('common-lisp', 'Common Lisp - CLOS, macros, conditions, packages, SBCL, CFFI, bordeaux-threads, quicklisp'),
    ('prolog-advanced', 'Prolog advanced - constraint logic, DCG, meta-predicates, modules, tabling, SWI-Prolog'),
    ('mercury-lang', 'Mercury logic programming - determinism, modes, types, purity, foreign language interface'),
    ('idris-lang', 'Idris 2 - dependent types, linear types, effects, interactive editing, proofs, tactics'),
    ('agda-lang', 'Agda - dependent types, propositions as types, proofs, modules, records, universes, cubical'),
    ('coq-theorem', 'Coq theorem prover - tactics, ltac, Gallina, extraction, SSReflect, libraries, Coq-of-Rust'),
    ('lean4-advanced', 'Lean 4 advanced - tactics, metaprogramming, Mathlib, macros, type classes, lake, FFI'),
    ('isabelle-hol', 'Isabelle/HOL - proof method, Isar, sledgehammer, code export, HOLCF, corec, datatypes'),
    ('tla-plus', 'TLA+ - specs, PlusCal, model checking, TLC, temporal logic, TLAPS, specifications'),
    ('alloy-modeling', 'Alloy modeling language - relational logic, Alloy Analyzer, instances, checking, visualization'),
    ('k-framework', 'K Framework - syntax, semantics, rewriting, proof, symbolic execution, language definition'),
    ('spin-model', 'SPIN model checker - Promela, never claims, LTL, pan, partial order reduction, abstraction'),
    # Web assembly and edge
    ('webassembly-advanced', 'WebAssembly advanced - WASI, components, interface types, GC, threads, SIMD, toolchain'),
    ('wasm-runtimes', 'WASM runtimes - Wasmtime, Wasmer, WasmEdge, Wasm3, runtime embedding, capabilities'),
    ('cloudflare-workers', 'Cloudflare Workers advanced - D1, R2, KV, Queues, Durable Objects, AI Gateway, bindings'),
    ('deno-advanced', 'Deno advanced - permissions, Deno KV, Deno Deploy, FFI, JSR, workspaces, fresh, Deno 2'),
    ('bun-advanced', 'Bun advanced - bundler, test runner, package manager, SQLite, hot reload, Bun.serve, FFI'),
    ('edge-functions', 'Edge functions - Vercel Edge, Netlify Edge, fastly compute, Fly.io, global distribution'),
    # Systems programming advanced
    ('linux-kernel-dev', 'Linux kernel development - modules, device drivers, system calls, memory, scheduler, BPF, kprobes'),
    ('linux-internals', 'Linux internals - process management, virtual memory, VFS, networking stack, namespaces, cgroups'),
    ('windows-internals', 'Windows internals - processes, threads, memory manager, object manager, I/O, registry, Hyper-V'),
    ('macos-internals', 'macOS internals - Mach, BSD, IOKit, XPC, code signing, SIP, TCC, sandbox, Rosetta'),
    ('device-driver-dev', 'Device driver development - Linux, Windows, USB, PCIe, DMA, interrupt, testing, debugging'),
    ('operating-systems-dev', 'OS development - bootloader, x86 real/protected mode, virtual memory, process scheduling'),
    ('hypervisor-development', 'Hypervisor development - KVM, Xen, VT-x, EPT, VMCS, VirtIO, vhost, IOMMU'),
    ('compiler-development', 'Compiler development - lexing, parsing, AST, IR, codegen, LLVM, register allocation, SSA'),
    ('llvm-advanced', 'LLVM advanced - passes, transformations, backend, MC layer, LTO, PGO, sanitizers, TableGen'),
    ('language-runtime-dev', 'Language runtime development - GC, JIT, bytecode, interpretation, optimization, profiling'),
    # Functional and reactive programming
    ('rxjs-advanced', 'RxJS advanced - higher-order observables, schedulers, subjects, custom operators, marble testing'),
    ('cyclejs', 'Cycle.js - drivers, circular dependencies, isolation, onionify, time travel, testing'),
    ('fp-ts-advanced', 'fp-ts advanced - ADTs, IO, Task, Either, Option, Reader, Writer, optics, Eq, Ord'),
    ('effect-ts', 'Effect-TS - fiber, context, scope, layer, schema, stream, STM, HTTP platform, services'),
    ('fsharp-functional', 'F# functional patterns - railway oriented, applicatives, computation expressions, state monad'),
]

for name, desc in skills:
    d = os.path.join(base, name)
    os.makedirs(d, exist_ok=True)
    title = name.replace('-', ' ').title()
    content = f'''---
name: {name}
description: {desc}
---

# {title} - MAARS Reference

## Overview
{desc}

## Core Framework
Use structured approach: define goal, identify audience, create hypothesis, execute, measure.

## Key Prompts
- "For [project], implement {title.lower()} for [use case]. Requirements: [X]. Provide working code examples."
- "Analyze [existing implementation] and suggest 3 improvements prioritized by impact."
- "Write a {title.lower()} template for a [type] project with [specific requirements]."

## Best Practices
1. Read official documentation before implementation
2. Test in isolation before full integration
3. Handle errors and edge cases explicitly
4. Document configuration and requirements
5. Monitor and alert on key metrics

## Common Patterns
- Setup and initialization
- Core operations
- Error handling and retries
- Authentication and security
- Performance and scaling

## Models to Use
- Architecture: claude-opus-4-6
- Implementation: claude-sonnet-4-6
- Quick lookups: claude-haiku-4-5-20251001
'''
    with open(os.path.join(d, 'SKILL.md'), 'w') as f:
        f.write(content)

print('Done:', len(skills), 'skills')
