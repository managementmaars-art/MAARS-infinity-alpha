# FrankenTUI UX Architecture

Status: active
Scope: TUI runtime behavior introduced by the FrankenTUI (ftui) migration

This document describes the runtime UX architecture that replaced the original ratatui
rendering layer. It covers the responsive layout system, command palette, inspector
cockpit, resize coalescer, and style degradation cascade. Future contributors should
be able to reason about any UX behavior from this document and the test suites it
references.

---

## Elm Architecture (Model-Update-View)

The TUI follows the Elm architecture pattern implemented by ftui:

```
Event -> CassMsg -> CassApp::update() -> Cmd<CassMsg> -> CassApp::view() -> Frame
```

`CassApp` (`src/ui/app.rs`) is the single Model. `update()` is a pure state transition
that returns `Cmd` values for side effects (async I/O, persistence, subprocess). `view()`
reads the model and emits rendering instructions. No ad-hoc mutation happens during
rendering.

**Why this matters**: Any new feature should follow the same cycle. State changes happen
in `update()`, rendering reads state in `view()`. Side effects are expressed as `Cmd`
values, never as direct calls inside `update()`.

**Key file**: `src/ui/app.rs` (~31k lines)
**Adapter layer**: `src/ui/ftui_adapter.rs` centralizes high-frequency ftui imports so
internal framework changes don't require touching every call site.

---

## Responsive Layout System

### Breakpoints

Terminal width drives a `LayoutBreakpoint` enum with four tiers:

| Breakpoint     | Width (cols) | Behavior |
|----------------|-------------|----------|
| `Narrow`       | <80         | Single pane with tab switching; compact density forced |
| `MediumNarrow` | 80-119      | Dual pane, tight detail column |
| `Medium`       | 120-159     | Balanced dual pane |
| `Wide`         | >=160       | Spacious dual pane |

Breakpoints resolve per-frame. Rendering code consults topology contracts instead
of making ad-hoc width decisions.

### Topology Contracts

Each breakpoint maps to two topology structs:

**SearchTopology**: Controls pane widths, split handle visibility, and dual-pane toggle.
- Narrow: single pane, no split handle
- MediumNarrow: 35-col results, 25-col detail, split handle visible
- Medium: 45/32 split
- Wide: 50/34 split

**AnalyticsTopology**: Controls tab bar, filter summary, header rows, footer hints.
- Narrow: no tab bar, no filter summary, zero footer hint slots
- MediumNarrow: no tab bar, filter summary shown, 2 footer slots (22 chars)
- Medium/Wide: full tab bar, filter summary, 4 footer slots (52 chars)

**VisibilityPolicy**: Controls optional decorations.
- Theme name in title bar: hidden on Narrow, shown on MediumNarrow+
- Saved-view path truncation: 20/40/60/80 chars by tier

### Ultra-Narrow Fallback

Terminals smaller than 30 cols or 6 rows display a "terminal too small" message
instead of attempting to render a broken layout. This prevents panics and unreadable
content at degenerate sizes.

### Density Modes

Three density modes: Compact, Cozy, Spacious. On terminals <90 cols, the mode
auto-downgrades to Compact regardless of user preference via `DensityMode::effective()`.

**Key code**: `src/ui/app.rs` lines 908-1231 (topology), lines 1291-1298 (density)
**Tests**: responsive SIZE_MATRIX suite (16 entries) in `src/ui/app.rs`

---

## Command Palette

### Overview

Ctrl+P / Alt+P opens a keyboard-first action dispatch overlay. The palette provides
fuzzy search over ~28 action variants organized into 7 groups:

| Group      | Actions |
|------------|---------|
| Chrome     | Theme toggle, density, help strip, update check |
| Filter     | Agent, workspace, time-range filters |
| View       | Saved views, bulk actions, reload |
| Analytics  | 8 sub-views (Dashboard, Explorer, Heatmap, Breakdowns, Tools, Cost, Plans, Coverage) |
| Export     | Screenshot formats (HTML, SVG, Text) |
| Recording  | Macro recording toggle |
| Sources    | Sources management |

### Match Modes

F9 cycles through match modes: All -> Exact -> Prefix -> WordStart -> Substring -> Fuzzy.
Each mode trades recall for precision. The default (All) uses Bayesian scoring which adds
~50us per keystroke but produces better ranking than substring matching.

Alt+B toggles a micro-bench overlay showing queries/second throughput and a latency
indicator (OK <200us, WARN <1000us, SLOW >=1000us).

### Architecture

The palette is side-effect free: `PaletteState` produces a `PaletteResult` which the
parent `update()` dispatches to the appropriate `CassMsg`. This means palette code never
directly mutates application state.

**Key file**: `src/ui/components/palette.rs` (1507 lines, 59 unit tests)
**Integration tests**: 12 regression tests in `src/ui/app.rs` covering dispatch for all
28 action variants

---

## Inspector / Explainability Cockpit

### Opening

Ctrl+Shift+I opens the inspector overlay with 7 tabs:
Timing, Layout, HitRegions, Resize, Diff, Budget, Timeline.

### Cockpit Panels

The cockpit surfaces causal explanations for adaptive runtime decisions through
4 panel types:

| Panel | What it explains |
|-------|-----------------|
| `DiffStrategy` | Full vs partial redraw decisions, dirty-row counts, reason strings |
| `ResizeRegime` | Steady vs Burst regime classification, BOCPD probability, event history |
| `BudgetHealth` | Frame budget vs actual time, degradation level, PID controller state |
| `Timeline` | Chronological feed of decision events with severity markers |

### Data Flow

Inspector data comes from ftui's per-tick evidence telemetry. The cockpit does not
parse logs at render time. Instead, ftui emits typed snapshots (`DiffStrategySnapshot`,
`ResizeDecisionSnapshot`, `BudgetSnapshot`) which the model stores in ring buffers.

### Cockpit Topology

The cockpit adapts to terminal size through `LayoutBreakpoint x CockpitMode` topology
contracts:

- Narrow overlay: 42x10 max, single-char tab labels (T L H R D B G)
- Narrow expanded: 42x16 max
- MediumNarrow: 56x12 overlay / 56x22 expanded, full labels
- Medium/Wide overlay: 66x16, full labels
- Medium/Wide expanded: 72x30, up to 18 timeline events

The cockpit auto-disables when the terminal is smaller than 20x6.

**Key code**: `src/ui/data.rs` lines 370-724 (data contracts), `src/ui/app.rs` lines 1235-1244 (topology)
**Tests**: cockpit topology tests in `src/ui/app.rs`

---

## Resize Coalescer (BOCPD)

The TUI uses Bayesian Online Changepoint Detection to classify resize event streams
into Steady and Burst regimes. This prevents the "thundering herd" problem where
rapid terminal resizing (e.g., dragging a window edge) triggers dozens of redundant
relayouts.

### How It Works

1. Each resize event records its inter-arrival time
2. BOCPD computes the probability that the resize rate has changed regime
3. In Burst regime, the coalescer delays relayout until the rate stabilizes
4. In Steady regime, resizes apply immediately

The "responsive" preset (`BocpdConfig::responsive()`) uses lower thresholds for
faster changepoint detection.

### Evidence Capture

The resize regime and BOCPD probability are surfaced in the inspector's Resize
panel via `ResizeRegimeContract` fields: regime label, burst probability, recommended
delay, event rate, and last action taken (apply/defer/coalesce).

**Key code**: `src/ui/app.rs` lines 1718-1830 (resize handling), `src/ui/data.rs` lines 507-553 (contract)

---

## Style & Degradation System

### Degradation Cascade

Six degradation levels, from full fidelity to frame skipping:

| Level | What renders |
|-------|-------------|
| `Full` | All styling, rounded borders, icons, gradients |
| `SimpleBorders` | Plain box-drawing (no rounded corners) |
| `NoStyling` | Square borders, no fg/bg colors |
| `EssentialOnly` | No borders, no icons, minimal content |
| `Skeleton` | Bare structure only |
| `SkipFrame` | Skip rendering entirely |

Degradation is driven by ftui's frame budget PID controller. When frame times exceed
the budget, the degradation level increases. When headroom returns, it decreases.

### DecorativePolicy

The function `DecorativePolicy::resolve()` maps
(StyleOptions, DegradationLevel, LayoutBreakpoint, fancy_borders) to a concrete
rendering policy with fields: `border_tier`, `show_icons`, `use_styling`,
`use_gradients`, `render_content`. Rendering code checks this policy instead of
making independent decisions about what to draw.

### Color Profile Detection

Precedence rules for color profile selection:

1. `CASS_NO_COLOR=1` -> Mono profile, no_color mode
2. `CASS_RESPECT_NO_COLOR=1` + `NO_COLOR` set -> Mono profile
3. `CASS_COLOR_PROFILE=<value>` -> use explicit value (mono/ansi16/ansi256/truecolor)
4. Otherwise -> detect from terminal capabilities (COLORTERM, TERM env vars)

### Semantic Tokens

Widgets reference semantic token names (e.g., `STYLE_STATUS_SUCCESS`, `STYLE_ROLE_USER`)
rather than raw colors. Theme preset changes and degradation level changes propagate
automatically through all widgets without per-widget updates.

19 named color slots: primary, secondary, accent, bg, surface, overlay, text,
text_muted, text_subtle, success, warning, error, info, border, border_focused,
selection, scrollbar.

### Theme Customization

Ctrl+Shift+T opens the interactive theme editor with hex input, preset cycling
(Dark, Light, HighContrast, Catppuccin, Dracula, Nord), WCAG contrast warnings,
and export to `~/.config/cass/theme.toml`.

**Key file**: `src/ui/style_system.rs` (4914 lines)
**Key file**: `docs/tui_style_spec.md` (full color/spacing/motion spec)
**Tests**: degradation transition monotonicity tests, capability matrix tests

---

## Modal Priority Stack

Modal interceptors form a priority stack:

```
theme editor > inspector > palette > normal key handling
```

When a modal is open, it captures all input except its own dismiss keybinding.
New modals should insert at the appropriate priority level and follow the same
capture/dismiss pattern.

---

## Accessibility

- `CASS_A11Y=1` enables accessible mode: text role markers, bold/underline accents,
  icon suppression
- `CASS_NO_ICONS=1` disables Unicode icons
- `CASS_NO_GRADIENT=1` disables gradient effects
- NO_COLOR standard is respected (with configurable override via CASS_RESPECT_NO_COLOR)
- Minimum contrast ratio target: 4.5:1 for all text
- 8-color terminal fallback: high-contrast flat palette, no gradients, no alpha

**Full spec**: `docs/ACCESSIBILITY.md`

---

## Test Coverage Pointers

| Area | Location | Count |
|------|----------|-------|
| Palette lifecycle + dispatch | `src/ui/app.rs`, `src/ui/components/palette.rs` | ~71 tests |
| Responsive layout (SIZE_MATRIX) | `src/ui/app.rs` | 16 entries |
| Degradation cascades | `src/ui/style_system.rs` | monotonicity + capability tests |
| Inspector cockpit | `src/ui/app.rs`, `src/ui/data.rs` | topology + contract tests |
| Cross-workstream integration | `tests/cross_workstream_integration.rs` | 74 tests |
| Visual parity | `docs/ftui_visual_parity_rubric.md` | scoring rubric |

---

## Design Decision Log

### Why Elm Architecture?

Separating state transitions (update) from rendering (view) eliminates an entire class
of bugs where rendering code mutates state mid-frame. It also makes the TUI testable:
unit tests can call `update()` with a message and assert on the resulting state without
needing a terminal.

### Why Breakpoint Contracts Instead of Ad-Hoc Width Checks?

Early versions used scattered `if width > N` checks. These were hard to maintain and
produced inconsistent behavior. Topology contracts centralize layout decisions: change
the contract once and all rendering code follows.

### Why BOCPD for Resize?

Simple debounce (fixed delay) either introduces visible latency on single resizes or
fails to coalesce rapid resize bursts. BOCPD adapts: it detects the statistical
boundary where resize rate changes, applying resizes immediately in steady state
and coalescing during bursts.

### Why Semantic Tokens Instead of Direct Colors?

Direct color references create tight coupling between theme presets and widget code.
Semantic tokens provide an indirection layer: themes define token values, widgets
reference tokens, and the degradation system can override token resolution without
touching widget code.
