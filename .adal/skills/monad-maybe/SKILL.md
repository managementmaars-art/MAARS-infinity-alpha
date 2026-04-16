---
name: monad-maybe
description: Use when writing or reviewing code that returns Maybe<T>.
argument-hint: "Paste the code snippet or use case and ask: 'normalize Maybe handling'"
---

# Maybe Monad

Use this skill to keep `Maybe<T>` usage simple and predictable.

## Core Rules
- Wrap optional value with `Maybe.maybe(value)`.
- Build explicit presence with `Maybe.some(value)`.
- Build explicit absence with `Maybe.none()`.
- Check state with `isSome()` / `isNone()`.
- Provide fallback with `else(() => defaultValue)`.
- Convert to `Result` when needed with `toResult()`.

## Common Mistakes To Avoid
- Do not treat `Maybe` like `Result`.
- Do not use `isFailure` on `Maybe`.
- Do not access `.data` without checking `isSome()` first.

## Procedure
1. Identify nullable or optional source values.
2. Convert early to `Maybe` (`Maybe.maybe(value)`).
3. Use one handling style consistently:
   - Branching: `if (m.isNone()) ... else m.data`
   - Functional: `map`, `flatMap`, `filter`, `fold`
   - Fallback: `m.else(() => defaultValue)`
4. If caller expects `Result<T, E>`, convert once with `toResult()` and continue in Result flow.

## Quick Patterns
```ts
const maybeEmail = Maybe.maybe(input.email);
if (maybeEmail.isNone()) return Result.err(new Error("Missing email"));

return Result.ok(maybeEmail.data.trim());
```

```ts
const displayName = Maybe.maybe(user.nickname)
	.filter((v) => v.length > 0)
	.else(() => user.nome)
	.data;
```