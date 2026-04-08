
import os
base = 'c:/Users/mirza/MAARS-Command/.claude/skills'
skills = [
    # More programming languages and paradigms
    ('gleam-advanced', 'Gleam advanced - type system, BEAM VM, OTP, interop with Erlang/Elixir, packages, testing'),
    ('grain-lang-advanced', 'Grain language advanced - linear types, memory management, WASM compilation, stdlib'),
    ('roc-lang-advanced', 'Roc language advanced - record syntax, abilities, tasks, REPL, platform building, performance'),
    ('purescript-advanced', 'PureScript advanced - type classes, MTL, Halogen, Effect, Aff, Purs, FFI, Spago'),
    ('elm-advanced', 'Elm advanced - architecture, custom types, ports, WebGL, interop, testing, optimization'),
    ('reasonml-advanced', 'ReasonML advanced - OCaml interop, bindings, BuckleScript, ReScript, JSX, variants'),
    ('clojurescript-advanced', 'ClojureScript advanced - React integration, shadow-cljs, macros, async, state management'),
    ('fable-fsharp', 'Fable F# - F# to JS compilation, Elmish, Feliz, React interop, testing, deployment'),
    ('mojo-advanced', 'Mojo advanced - MLIR, ownership, parameters, inout, auto-parallelism, SIMD, GPU'),
    ('carbon-lang-advanced', 'Carbon language advanced - interoperability with C++, safety model, toolchain, migration'),
    ('beef-lang-advanced', 'Beef language - real-time debugging, performance, hot code reloading, game development'),
    ('vale-lang', 'Vale language - regions, borrowing, generational references, speed, FFI, safety guarantees'),
    ('lobster-lang', 'Lobster language - strongly typed scripting, coroutines, visual programming, game logic'),
    ('pony-lang', 'Pony language - actors, capabilities, reference capabilities, lock-free, performance, type system'),
    ('red-lang', 'Red programming language - dialects, reactive, Parse dialect, VID GUI, scripting, REBOL heritage'),
    ('rebol-lang', 'REBOL language - dialects, meta-programming, homoiconicity, internet protocols, parse, GUI'),
    ('chapel-parallel', 'Chapel parallel programming - domains, arrays, parallel loops, communication, HPC, GPU'),
    ('x10-parallel', 'X10 parallel programming - places, activities, async/finish, distributed, PGAS model'),
    ('coarray-fortran', 'Coarray Fortran - PGAS, images, codimension, sync, distributed memory, scientific computing'),
    ('hack-lang', 'Hack language - type system, async, XHP, collections, shape, type refinement, generics'),
    ('lfe-lisp', 'LFE (Lisp Flavored Erlang) - macros, OTP, BEAM VM, metaprogramming, patterns, interop'),
    ('jolie-microservices', 'Jolie microservices - service-oriented, behavior, workflow, orchestration, aggregation'),
    ('whiley-lang', 'Whiley language - postconditions, invariants, verification, runtime checks, subtyping'),
    ('dafny-verification', 'Dafny verification - specifications, proofs, invariants, modular reasoning, verification'),
    ('verifast-verification', 'VeriFast verification - separation logic, C/Java, proof annotations, fractional permissions'),
    ('liquid-haskell', 'LiquidHaskell - refinement types, SMT verification, measures, termination, safety'),
    ('fstar-verification', 'F* verification - dependent types, effects, Z3, proofs, Low*, C interop, cryptography'),
    # More data formats and standards
    ('json-ld-advanced', 'JSON-LD advanced - context, framing, compaction, expansion, RDF conversion, linked data'),
    ('rdf-sparql', 'RDF and SPARQL - triples, ontologies, reasoning, SPARQL queries, federated, update, inference'),
    ('owl-ontology', 'OWL ontology - description logics, TBox, ABox, reasoners, Protégé, SHACL, validation'),
    ('graphql-federation-advanced', 'GraphQL federation advanced - subgraph, supergraph, router, composition, defer, stream'),
    ('openapi-31-advanced', 'OpenAPI 3.1 advanced - webhooks, path templating, discriminator, callbacks, security schemes'),
    ('asyncapi-advanced', 'AsyncAPI advanced - channels, bindings, traits, message correlations, code generation'),
    ('cloudevents-advanced', 'CloudEvents advanced - bindings, extensions, versioning, delivery guarantees, SDK usage'),
    ('odata-protocol', 'OData protocol - entity model, query options, batch, expand, filtering, EDM, metadata'),
    ('graphql-subscriptions-advanced', 'GraphQL subscriptions advanced - WebSocket, SSE, filtering, multiplexing, authorization'),
    ('jsonapi-spec', 'JSON:API spec - resource objects, relationships, links, sparse fieldsets, pagination, errors'),
    ('hal-hypermedia', 'HAL hypermedia - links, embedded, curies, resource, browser, CURIE, hypermedia design'),
    ('siren-hypermedia', 'Siren hypermedia - entities, actions, links, fields, class, sub-entities, navigation'),
    ('problem-details-rfc', 'Problem Details RFC 7807 - status, type, title, detail, instance, extensions, content-type'),
    ('cbor-encoding', 'CBOR encoding - Concise Binary Object Representation, COSE, CWT, CBOR-LD, diagnostic'),
    ('bson-format', 'BSON format - binary JSON, MongoDB wire protocol, types, encoding, indexing, aggregation'),
    ('smile-format', 'Smile binary format - binary JSON variant, headers, types, back references, Jackson integration'),
    ('ion-format', 'Amazon Ion format - data model, types, text/binary, shared symbol tables, readers/writers'),
    ('serf-msgpack', 'Serf/MessagePack encoding - efficient binary, schema-free, streaming, extension types'),
    ('bencode-format', 'Bencode format - BitTorrent encoding, integers, strings, lists, dictionaries, metainfo files'),
    ('ndjson-format', 'NDJSON/JSONL format - newline-delimited JSON, streaming, log processing, bulk imports'),
    # More security patterns
    ('supply-chain-security-advanced', 'Supply chain security advanced - SBOM, SLSA, sigstore, in-toto, attestation, VEX'),
    ('threat-modeling-tmthreat', 'Threat modeling Microsoft TMT - DFDs, STRIDE automation, mitigations, reports'),
    ('attack-surface-management', 'Attack surface management - discovery, inventory, monitoring, risk prioritization, ASM'),
    ('vulnerability-management-advanced', 'Vulnerability management advanced - CVSS v4, EPSS, prioritization, SLA, remediation'),
    ('devsecops-advanced', 'DevSecOps advanced - shift-left, ASPM, policy as code, security champions, metrics'),
    ('container-security-advanced', 'Container security advanced - image signing, SBOM, admission, runtime, least privilege'),
    ('cloud-native-security-advanced', 'Cloud-native security advanced - CNAPP, CSPM, CWPP, CIEM, agentless, shift-left'),
    ('api-security-advanced', 'API security advanced - OWASP API Top 10, spec validation, fuzzing, JWT attacks, BOLA'),
    ('mobile-security-advanced', 'Mobile security advanced - OWASP MASVS, reverse engineering, certificate pinning, frida'),
    ('hardware-security', 'Hardware security - TPM, secure enclave, HSM, side-channel attacks, firmware analysis'),
    ('cryptography-engineering', 'Cryptography engineering - key management, TLS 1.3, PKCS, certificate lifecycle, HSM'),
    ('privacy-engineering', 'Privacy engineering - PETs, differential privacy, SMPC, k-anonymity, data minimization'),
    ('red-team-infrastructure', 'Red team infrastructure - C2 setup, redirectors, domain fronting, OPSEC, COVERT comms'),
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
