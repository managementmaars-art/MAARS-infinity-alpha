---
name: cocos-ui-schema-generator  
description: Generate Cocos Creator 2.4 WebUI schema and supporting TypeScript files from screenshots, HTML, mockups, or textual UI descriptions. Use when building UI in projects that want to reuse the bundled WebUI runtime, when converting a design into `WebUINodeSchema`, when preparing AI-generated UI code for Cocos, or when a target project does not yet contain the required WebUI runtime files and they must be copied in first.
---

# cocos-ui-schema-generator

Generate UI as `WebUINodeSchema`-based TypeScript for the bundled Cocos WebUI runtime.

This skill includes a reusable runtime in `assets/webui-runtime/`. If the target Cocos project does not already contain these runtime files, copy them into the target project before generating schema or controller code.

## Bundled assets

The bundled runtime lives here:

- `assets/webui-runtime/types.ts`
- `assets/webui-runtime/style.ts`
- `assets/webui-runtime/layout.ts`
- `assets/webui-runtime/WebUIBackground.ts`
- `assets/webui-runtime/WebUIRenderer.ts`
- `assets/webui-runtime/WebUIExample.ts`
- `assets/webui-runtime/uiMeta.ts`
- `assets/webui-runtime/examples/withdrawExample.ts`
- `assets/webui-runtime/examples/withdrawExample1.ts`

Use these files as the source of truth when bootstrapping a new project.

The skill also includes helper scripts:

- `scripts/install-runtime.ps1`
- `scripts/validate-webui-schema.js`

## Core workflow

1. Inspect the target repository.
2. Check whether a compatible WebUI runtime already exists.
3. If missing, copy the bundled runtime into the target project first.
4. Generate a schema as a `.ts` file exporting `WebUINodeSchema` data.
5. If requested, generate a business-facing controller component that uses `WebUIRenderer`.
6. Keep generated output within the capabilities of the bundled runtime.

## Runtime bootstrap rule

Before generating new UI files, verify whether the target project already contains equivalent runtime files such as `WebUIRenderer.ts`, `layout.ts`, `style.ts`, and `types.ts`.

If they do not exist, prefer using `scripts/install-runtime.ps1` from this skill to copy the bundled runtime into a suitable location in the target Cocos project. Typical target location:

- `assets/scripts/webui/`
- or the repository's existing UI runtime directory

Prefer preserving the bundled file contents exactly unless the target project clearly requires path or naming adjustments.

PowerShell example:

- `powershell -ExecutionPolicy Bypass -File <skill>/scripts/install-runtime.ps1 -TargetProjectRoot <projectRoot>`

## File layout and import path rules

Prefer the following project layout when bootstrapping a plain Cocos Creator project:

- runtime: `assets/scripts/webui/`
- generated page files: `assets/scripts/`

If runtime is installed under `assets/scripts/webui/` and generated page files are placed under `assets/scripts/`, use these relative imports:

- schema -> `import { WebUINodeSchema } from './webui/types';`
- meta -> `import { WebUIMeta } from './webui/uiMeta';`
- controller -> `import WebUIRenderer from './webui/WebUIRenderer';`

Do not guess import paths blindly. Compute imports from the actual generated file location relative to the runtime location.

If the target project uses a different directory layout, adjust imports accordingly, but keep runtime imports consistent within the generated files.

## Output format rules

Generate TypeScript, not raw JSON, unless the user explicitly asks for JSON.

Preferred output shape:

- one schema file, e.g. `WithdrawPanel.schema.ts`
- export a typed constant, e.g. `export const withdrawPanelSchema: WebUINodeSchema = { ... }`
- one meta object, e.g. `export const withdrawPanelMeta: WebUIMeta = { ... }`

If a controller is requested, generate a separate component file, e.g. `WithdrawPanel.ts`, that:

- extends `cc.Component`
- gets or adds `WebUIRenderer`
- renders the schema
- optionally stores references to key nodes after render
- may use `renderer.getNodeById(id)` or `renderer.getNodesByIds(ids)` when the bundled runtime is present

Do not treat `WebUIExample.ts` as a required business base class. It is only an example reference.

## Allowed node types

Only generate these node types unless the runtime has been explicitly extended:

- `view`
- `text`
- `image`

Do not invent unsupported nodes such as:

- `button`
- `input`
- `scroll`
- `richText`
- `svg`
- `video`

Represent buttons and clickable areas as `view` or `text` nodes with stable ids that business code can bind events to later.

## Allowed style rules

Only use style fields supported by the bundled runtime:

- `display`
- `position`
- `flexDirection`
- `justifyContent`
- `alignItems`
- `alignSelf`
- `flexWrap`
- `flexGrow`
- `flexShrink`
- `flexBasis`
- `gap`
- `width`
- `height`
- `minWidth`
- `minHeight`
- `maxWidth`
- `maxHeight`
- `padding`
- `margin`
- `paddingTop`
- `paddingRight`
- `paddingBottom`
- `paddingLeft`
- `marginTop`
- `marginRight`
- `marginBottom`
- `marginLeft`
- `left`
- `right`
- `top`
- `bottom`
- `zIndex`
- `backgroundColor`
- `opacity`
- `borderRadius`
- `fontSize`
- `fontWeight`
- `color`
- `lineHeight`
- `textAlign`
- `whiteSpace`
- `overflow`
- `objectFit`

Do not generate unsupported CSS-like fields such as `border`, `boxShadow`, `transform`, `grid`, `filter`, `letterSpacing`, or `lineClamp` unless the user explicitly asks to extend the runtime too.

## Unsupported style fallback rules

When the source design contains unsupported CSS-like effects, do not simply copy those fields into schema. Use the following fallback strategy.

### Border and divider fallback

- `borderTop`, `borderBottom`, or similar single-edge border:
  - replace with a dedicated thin `view` node, usually height `1`, width `'100%'`, and a suitable `backgroundColor`
- full `border` around a block:
  - prefer a nested two-layer structure:
    - outer `view` uses the border color and border radius
    - inner `view` uses the content background color and inner padding or margin to simulate the border thickness
- radio or outlined circle:
  - prefer nested circular `view`s rather than unsupported border fields

### Shadow fallback

- `boxShadow`:
  - omit by default
  - if the shadow is visually important, approximate it with a softer background block or a larger outer wrapper with a subtle background color
  - never generate `boxShadow` directly unless runtime support is explicitly added

### Gradient fallback

- `linear-gradient` or other gradient backgrounds:
  - replace with a single dominant solid color
  - if the gradient is central to the design, tell the user that the runtime must be extended for accurate rendering

### Transform fallback

- `transform`, `scale`, `rotate`, `translate`:
  - avoid generating them
  - simplify the structure or use normal layout and positioning instead

### Rounded clipping fallback

- rounded image clipping or `overflow: hidden` for card masking:
  - do not assume generic clipping is fully supported
  - if accuracy depends on clipping, either simplify the design or explicitly note the runtime limitation

Always prefer a visually close, runtime-compatible structure over copying unsupported fields.

## Layout generation rules

Prefer flex layout over absolute positioning.

Use `position: 'absolute'` only for clear overlay cases such as:

- floating close buttons
- top-left back icons over a title area
- badges or corner marks
- decorative overlays

For normal structure, prefer:

- semantic container `view`s
- `flexDirection`
- `gap`
- `padding`
- `margin`

Avoid unnecessary nesting. Keep hierarchy shallow while preserving meaningful groups such as header, content, footer, card, row, and action area.

## Id and naming rules

Assign stable ids to all business-relevant nodes.

Ids are required for:

- clickable nodes
- dynamic text nodes
- dynamic image nodes
- nodes that may be shown or hidden
- container nodes that business code may access later

Use lower camel case and semantic prefixes when useful:

- `btnSubmit`
- `btnBack`
- `txtAmount`
- `txtTitle`
- `imgAvatar`
- `panelMain`
- `listRewards`

Do not rename existing ids during edits unless the user explicitly requests it.

## UI meta rules

Generate a lightweight `WebUIMeta` object alongside the schema for business-facing pages.

Import source:

- `assets/webui-runtime/uiMeta.ts`

Current supported fields:

- `interactiveIds`
- `dynamicTextIds`
- `dynamicImageIds`
- `containerIds`

Use `interactiveIds` for clickable nodes such as back, close, submit, invite, tab, and card entry areas.

Use `dynamicTextIds` for text nodes whose content may change later, such as title, amount, username, countdown, status text, and button label.

Use `dynamicImageIds` for images that business code may replace later, such as avatar, banner, product, and reward art.

Use `containerIds` for nodes that business code may access to inject, replace, or toggle content, such as main panel, content panel, empty panel, loading panel, and list container.

Keep `WebUIMeta` lightweight. Do not try to encode full business logic into it.

## Controller generation rules

If asked to generate a controller component, prefer this structure:

- `onLoad()` or `start()` ensures a `WebUIRenderer` exists
- render the schema once
- `cacheNodes()` optionally stores important node references after render
- `bindEvents()` attaches click handlers for interactive ids
- business update methods such as `updateAmount()`, `updateTitle()`, or `setLoadingVisible()` modify UI using ids or cached refs

Additional rules:

- render the schema via `WebUIRenderer`
- avoid embedding large schema objects directly inside the controller if a separate schema file is feasible
- import and use the generated `WebUIMeta` when present
- use ids to find nodes after render
- prefer `renderer.getNodeById('someId')` when using the bundled runtime
- keep event binding in the controller, not in the schema
- keep business logic separate from runtime files
- if `claimToBagMeta.interactiveIds` or similar meta fields exist, keep controller logic aligned with those ids rather than inventing unrelated names

## Editing existing generated UI

When revising an existing schema:

- preserve existing ids whenever possible
- avoid restructuring unrelated branches
- make the smallest requested change
- keep compatibility with the bundled runtime

## Practical constraints of the bundled runtime

The bundled runtime is suitable for prototype and moderate business UI, but not full browser compatibility.

Important limitations to respect while generating:

- only `view`, `text`, `image` are supported
- `flexWrap` is typed but not fully implemented for production usage
- `flexShrink` support is incomplete
- image measuring is basic; prefer explicit image width and height
- `overflow: hidden` is not fully implemented as a generic container clipping system
- border, gradient, and shadow are not implemented

When the design depends on unsupported features, simplify the UI or explicitly tell the user that the runtime must be extended.

## Preferred generation strategy

For screenshot-to-UI or mockup-to-UI tasks:

1. Infer a semantic container structure.
2. Convert the structure into a `WebUINodeSchema` tree.
3. Add stable ids to business-critical nodes.
4. Keep text nodes coarse-grained unless style differences require splitting.
5. Give explicit width and height to images.
6. Generate a controller only if the user needs interaction wiring or dynamic updates.

## Validation rule

When schema or meta is available in machine-readable JSON form for checking, validate it with `scripts/validate-webui-schema.js` when practical. The validator checks:

- node type validity
- supported style keys
- duplicate ids
- required `props.text` for text
- required `props.src` for image
- meta ids that do not exist in schema

## Important behavior

If the current repository does not contain the WebUI runtime, do not stop at schema generation. First copy the bundled runtime assets from this skill into the target project, then generate the schema, meta, and any requested controller files.
