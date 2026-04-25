
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # Every major programming language (deep coverage)
    ('lua-programming', 'Lua programming - tables, metatables, coroutines, C API, LuaJIT, LÖVE, scripting, modules'),
    ('perl-programming', 'Perl programming - regexes, CPAN, references, OOP, DBI, CGI, text processing, one-liners'),
    ('objective-c', 'Objective-C - message passing, ARC, categories, protocols, blocks, Foundation, UIKit, runtime'),
    ('groovy-programming', 'Groovy - closures, dynamic typing, DSLs, Gradle scripts, Spock, GDK, metaprogramming'),
    ('scheme-language', 'Scheme - continuations, macros, tail recursion, SICP, Racket, Guile, R7RS, environments'),
    ('racket-language', 'Racket - macros, typed racket, continuations, GUI, DrRacket, package system, web server'),
    ('elm-language', 'Elm - The Elm Architecture, types, effects, decoders, ports, subscriptions, no runtime errors'),
    ('reasonml', 'ReasonML/ReScript - OCaml semantics, JSX, Belt, bindings, pattern matching, modules, React'),
    ('purescript-advanced', 'PureScript - type classes, row polymorphism, Halogen, Effect, Aff, foreign imports'),
    ('f-sharp-advanced', 'F# advanced - computation expressions, type providers, discriminated unions, mailbox, Fable'),
    ('clojurescript', 'ClojureScript - reagent, re-frame, shadow-cljs, interop, macros, transit, core.async'),
    ('common-lisp', 'Common Lisp - CLOS, macros, conditions, packages, ASDF, Quicklisp, SBCL, performance'),
    ('tcl-programming', 'Tcl/Tk - event loop, namespaces, packages, TclOO, expect, Tk widgets, embedded'),
    ('pascal-delphi', 'Pascal/Delphi - classes, interfaces, RTTI, FireMonkey, VCL, database, RAD, FPC'),
    ('d-language', 'D language - templates, mixins, ranges, fibers, GC, betterC, CTFE, DUB, phobos'),
    ('ada-programming', 'Ada - strong typing, tasks, protected objects, contracts, ravenscar, GNAT, embedded'),
    ('cobol-programming', 'COBOL programming - divisions, data types, file handling, CICS, DB2, mainframe migration'),
    ('fortran-programming', 'Fortran programming - arrays, modules, pointers, parallel, intrinsics, numerical, HPC'),
    ('prolog-programming', 'Prolog - unification, backtracking, DCG, meta-predicates, constraint solving, SWI-Prolog'),
    ('matlab-programming', 'MATLAB programming - matrices, toolboxes, Simulink, plotting, optimization, signal processing'),
    ('r-advanced', 'R advanced - environments, R6, Rcpp, tidyeval, parallel, S3/S4/R5, package development'),
    ('julia-advanced', 'Julia advanced - multiple dispatch, metaprogramming, SIMD, parallel, GPU, Pkg, interop'),
    ('swift-ui-advanced', 'SwiftUI advanced - custom layouts, property wrappers, preferences, geometry, matchedGeometry'),
    ('kotlin-dsl', 'Kotlin DSL - type-safe builders, extension functions, operator overloading, delegated properties'),
    ('scala-3-advanced', 'Scala 3 advanced - opaque types, extension methods, union types, given, export, macros'),
    ('haskell-monad-transformers', 'Haskell monad transformers - MTL, ReaderT, StateT, ExceptT, lift, runXxx, transformer stacks'),
    ('ocaml-advanced', 'OCaml advanced - modules, functors, GADTs, effects, ppx, dune, lwt, async, mirage'),
    ('gleam-language', 'Gleam - type-safe BEAM language, pipelines, custom types, interop, OTP, concurrency'),
    ('grain-language', 'Grain - WebAssembly-first, pattern matching, types, modules, memory management'),
    ('roc-language', 'Roc - platforms, tasks, records, tags, modules, abilities, effects, performance'),
    # Systems/Low-level languages
    ('c-advanced', 'C advanced - pointers, memory layout, inline assembly, undefined behavior, POSIX, toolchains'),
    ('cpp-systems', 'C++ systems - allocators, coroutines, concepts, constexpr, SIMD, ABI, toolchains, sanitizers'),
    ('rust-systems-advanced', 'Rust systems - unsafe, raw pointers, FFI, linker scripts, no_std, atomics, intrinsics'),
    ('assembly-advanced', 'Assembly language - x86-64, ARM, calling conventions, SIMD, OS dev, bootloaders, debugging'),
    ('mips-assembly', 'MIPS assembly - instructions, registers, memory, syscalls, floating point, MIPS32/64'),
    ('wasm-advanced', 'WebAssembly advanced - WAT, component model, WASI, memory64, threads, GC, toolchains'),
    # Scripting/Shell
    ('bash-advanced', 'Bash advanced - process substitution, coprocesses, arrays, traps, getopts, signal handling'),
    ('zsh-scripting', 'Zsh - completion system, plugins, themes, functions, hooks, ZLE, zplugin, antibody'),
    ('fish-shell', 'Fish shell - functions, completions, abbr, universal vars, event system, scripting'),
    ('powershell-advanced', 'PowerShell advanced - classes, DSC, remoting, modules, providers, PipelineVariable, jobs'),
    ('python-scripting', 'Python scripting - argparse, pathlib, subprocess, shutil, os, sys, automation, globs'),
    ('ruby-scripting', 'Ruby scripting - one-liners, optparse, fileutils, ERB, Rake, automation, text processing'),
    # Web frontend languages/extensions
    ('coffeescript', 'CoffeeScript - syntactic sugar, classes, comprehensions, arrow functions, existential operator'),
    ('livescript', 'LiveScript - functional, OOP, backcalls, operators, lists, pattern matching, compile to JS'),
    ('typescript-compiler-advanced', 'TypeScript compiler API - AST traversal, transforms, diagnostics, language service, plugins'),
    ('flow-types', 'Flow type checker - type annotations, generics, React, opaque types, library definitions'),
    # Mobile platforms
    ('android-ndk', 'Android NDK - JNI, native code, CMake, Android.mk, ABI, profiling, GLES, Vulkan'),
    ('ios-native-advanced', 'iOS native advanced - Metal, ARKit, Core ML, Core Data, CloudKit, app extensions, Instruments'),
    ('watchos-development', 'watchOS development - complications, health, sensors, connectivity, SwiftUI on watch'),
    ('tvos-development', 'tvOS development - focus engine, TVML, top shelf, remote, media playback, CloudKit'),
    ('visionos-development', 'visionOS development - RealityKit, Reality Composer Pro, windows, volumes, spaces, ARKit'),
    ('android-wear-os', 'Wear OS development - tiles, complications, health services, ambient mode, input, sensors'),
    # Desktop development
    ('electron-advanced', 'Electron advanced - IPC, context isolation, preload, native modules, auto-updater, ASAR'),
    ('tauri-advanced', 'Tauri advanced - commands, events, plugins, system tray, notifications, deep links, updater'),
    ('qt-framework', 'Qt framework - signals/slots, QML, model/view, threading, networking, OpenGL, deployment'),
    ('wxwidgets', 'wxWidgets - cross-platform, event handling, sizers, painting, threads, database, multimedia'),
    ('gtk-programming', 'GTK programming - signals, GObject, GLib, Cairo, Pango, GStreamer, GNOME integration'),
    ('winforms-advanced', 'WinForms advanced - custom controls, data binding, async, P/Invoke, COM interop, printing'),
    ('wpf-advanced', 'WPF advanced - MVVM, dependency properties, routed events, animation, templates, 3D'),
    ('maui-advanced-patterns', 'MAUI advanced patterns - handlers, effects, behaviors, platforms, shell navigation, MVVM'),
    ('flutter-desktop', 'Flutter desktop - Windows, macOS, Linux, platform channels, plugins, FFI, accessibility'),
    # Game-specific
    ('pygame-advanced', 'Pygame advanced - sprites, groups, events, collision, surfaces, sound, tilemaps, particles'),
    ('monogame', 'MonoGame - content pipeline, sprites, input, audio, physics, shaders, cross-platform, Xbox'),
    ('libgdx', 'LibGDX - scenes, actors, shaders, box2d, tweens, assets, networking, cross-platform, Kotlin'),
    ('phaser-advanced', 'Phaser advanced - arcade physics, tilemaps, cameras, tweens, particles, shaders, scale'),
    ('babylon-advanced', 'Babylon.js advanced - PBR materials, physics, XR, shadows, post-processes, GUI, inspector'),
    ('threejs-advanced', 'Three.js advanced - custom shaders, physics, XR, instancing, LOD, skeletal animation'),
    ('pixijs-advanced', 'PixiJS advanced - filters, spine, particle container, render texture, interaction, batching'),
    ('love2d-advanced', 'LÖVE 2D advanced - physics, shaders, threads, sockets, gamepad, transforms, particles'),
    # Scientific/numerical
    ('numpy-advanced', 'NumPy advanced - broadcasting, strides, ufuncs, structured arrays, C extensions, memory'),
    ('scipy-advanced', 'SciPy advanced - sparse matrices, optimization, integration, signal, interpolation, stats'),
    ('pandas-advanced', 'Pandas advanced - internals, extension types, query optimization, groupby, rolling, MultiIndex'),
    ('matplotlib-advanced', 'Matplotlib advanced - artists, axes transforms, animation, custom projections, backends'),
    ('sympy-advanced', 'SymPy advanced - expression manipulation, solvers, calculus, linear algebra, code generation'),
    ('cvxpy-optimization', 'CVXPY optimization - convex problems, disciplined programming, solvers, parametric, MIP'),
    ('networkx-advanced', 'NetworkX advanced - algorithms, generators, drawing, I/O, centrality, community detection'),
    ('statsmodels-advanced', 'statsmodels advanced - GLM, time series, survival, mixed effects, VAR, multivariate'),
    ('pymc-advanced', 'PyMC advanced - NUTS, variational inference, custom distributions, Gaussian processes, PPL'),
    ('scikit-learn-advanced', 'scikit-learn advanced - pipelines, custom estimators, feature union, calibration, inspection'),
    # Web standards & APIs
    ('web-components', 'Web Components - custom elements, shadow DOM, HTML templates, slots, lifecycle, Lit'),
    ('service-workers', 'Service Workers - cache API, push notifications, background sync, workbox, offline first'),
    ('web-crypto-api', 'Web Crypto API - key generation, encryption, signatures, digests, ECDH, AES-GCM'),
    ('webrtc-advanced', 'WebRTC advanced - signaling, ICE, DTLS, SRTP, data channels, statistics, simulcast'),
    ('websockets-advanced', 'WebSockets advanced - framing, extensions, subprotocols, load balancing, scaling'),
    ('web-push', 'Web Push notifications - VAPID, payload encryption, service workers, subscriptions, delivery'),
    ('media-source-extensions', 'Media Source Extensions - adaptive streaming, DASH, HLS.js, buffer management, codecs'),
    ('webgl-advanced', 'WebGL advanced - shaders, buffers, textures, instancing, transform feedback, multisampling'),
    ('webgpu-advanced', 'WebGPU advanced - compute pipelines, storage buffers, bind groups, WGSL, render passes'),
    ('webaudio-api', 'Web Audio API - nodes, routing, analysis, synthesis, spatialization, worklets, streaming'),
    # Compiler/language tools
    ('llvm-ir', 'LLVM IR - types, instructions, passes, optimization, backend, tablegen, MLIR bridge'),
    ('antlr-grammars', 'ANTLR grammars - lexer rules, parser rules, visitors, listeners, error recovery, predicates'),
    ('bison-flex', 'Bison/Flex - grammar rules, actions, symbol types, conflicts, precedence, GLR'),
    ('tree-sitter', 'Tree-sitter - grammar writing, queries, binding, incremental parsing, syntax highlighting'),
    ('cranelift', 'Cranelift code generator - IR, passes, register allocation, JIT, backend, verifier'),
    ('webassembly-toolchain', 'WebAssembly toolchain - clang, wasi-sdk, binaryen, wabt, optimization, linking'),
    # Functional programming tools
    ('arrow-kt', 'Arrow Kt - functional Kotlin, Option, Either, IO, optics, validation, concurrency'),
    ('cats-scala', 'Cats Scala - type classes, functor, monad, applicative, IO, mtl, kernel, effect'),
    ('zio-scala', 'ZIO Scala - fibers, layers, refs, STM, streams, schedule, metrics, test'),
    ('fp-ts-advanced', 'fp-ts advanced - ADTs, pipe/flow, TaskEither, ReaderTaskEither, schema, codecs'),
    ('effect-ts-advanced', 'Effect-ts advanced - fibers, layers, scopes, streams, schedule, concurrency, testing'),
    ('haskell-lens', 'Haskell lens - optics, traversals, prisms, isos, indexed, van Laarhoven, profunctor'),
    # Markup/document
    ('latex-beamer', 'LaTeX Beamer - slides, themes, animations, overlays, handout, bibliography, TikZ'),
    ('asciidoc', 'AsciiDoc - document structure, macros, extensions, Asciidoctor, diagrams, publishing'),
    ('rst-sphinx', 'reStructuredText/Sphinx - directives, roles, autodoc, themes, extensions, readthedocs'),
    ('typst-document', 'Typst - document composition, styling, math, bibliography, templates, packages'),
    ('pandoc-conversion', 'Pandoc - document conversion, filters, templates, citations, Lua filters, formats'),
    # Regular expressions advanced
    ('regex-advanced', 'Regex advanced - lookahead, lookbehind, atomic groups, possessive, PCRE, RE2, matching'),
    # Build systems
    ('make-advanced', 'GNU Make advanced - automatic variables, pattern rules, functions, VPATH, parallel, .PHONY'),
    ('cmake-advanced', 'CMake advanced - targets, generators, toolchains, CPM, FetchContent, packaging, testing'),
    ('meson-build', 'Meson build system - cross compilation, wraps, unity builds, introspection, benchmarks'),
    ('buck2-build', 'Buck2 build - targets, rules, macros, remote execution, query, project graphs'),
    ('scons-build', 'SCons - build environments, scanners, builders, caching, variants, compilation databases'),
    # Package managers
    ('cargo-workspaces', 'Cargo workspaces - member crates, dependency sharing, workspace configs, publishing'),
    ('npm-advanced', 'npm advanced - workspaces, lifecycle scripts, link, publish, audit, overrides, lockfiles'),
    ('pip-advanced', 'pip advanced - constraints, extras, editable installs, index servers, trusted hosts'),
    ('conda-advanced', 'Conda advanced - environments, channels, packages, lock files, micromamba, mamba'),
    ('homebrew-advanced', 'Homebrew advanced - formulae, casks, taps, bottles, services, bundle, audit'),
    # Version control
    ('git-advanced', 'Git advanced - rebase, reflog, bisect, worktrees, submodules, hooks, attributes, internals'),
    ('mercurial-hg', 'Mercurial - branches, bookmarks, phases, extensions, hg flow, largefiles, convert'),
    ('svn-advanced', 'SVN advanced - branching, merging, externals, hooks, dump, load, svnadmin'),
    ('fossil-scm', 'Fossil SCM - tickets, wiki, forum, sync, bisect, stash, configuration, autosync'),
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
