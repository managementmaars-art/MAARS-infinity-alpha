# H5P Content Type Authoring

## Minimum moving parts
- A runtime JavaScript library that renders into a container via an `attach` method.
- `semantics.json` that defines the editor schema and validates the data structure.
- `library.json` metadata, including preloaded JS/CSS assets.

## Authoring flow
1. Define editor fields in `semantics.json` (labels, types, defaults, validation).
2. Implement runtime logic in `src/scripts/h5p-<slug>.js` to read params and render in `attach`.
3. Register built assets in `library.json` under `preloadedJs` and `preloadedCss`.

## Scaffold mapping
- `src/scripts/h5p-<slug>.js`: runtime entry point (`attach`).
- `src/styles/h5p-<slug>.css`: styles.
- `semantics.json`: editor schema and validation.
- `library.json`: metadata and preloaded assets.

## References
- https://h5p.org/library-development
- https://h5p.org/semantics
