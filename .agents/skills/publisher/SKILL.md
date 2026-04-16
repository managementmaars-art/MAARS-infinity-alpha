---
name: publisher
description: Use when writing or reviewing Publisher code.
argument-hint: "Paste code and ask: 'normalize Publisher usage'"
---

# Publisher

Use this skill when you need event broadcasting without stored state.

## Quick Rule
- `Publisher`: emit events with `notify(...)` to current subscribers.
- No state: if you need `get/set`, use Observable instead.

## Procedure
1. Create `new PublisherImpl<Args>()` with typed tuple args.
2. Register listeners with `subscribe(...)` and keep the cleanup function.
3. Emit events via `notify(...)` and cleanup with returned unsubscribe or `unsubscribeAll()`.

## Common Mistakes
- Using Publisher as a state container.
- Ignoring returned unsubscribe function.
- Emitting args that do not match the tuple type.

## Tiny Example
```ts
const bus = new PublisherImpl<[string, number]>();
const off = bus.subscribe((event, code) => console.log(event, code));

bus.notify("saved", 200);
off();
```

## Simplified Interface

```ts
type Subscriber<ARGS extends unknown[]> = (...args: ARGS) => void;
type Unsubscribe = () => void;
interface IPublisher<ARGS extends unknown[]> {
    size: number;
    subscribe(s: Subscriber<ARGS>): Unsubscribe;
    unsubscribe(id: number): void;
    notify(...args: ARGS): void;
    unsubscribeAll(): void;
}
```