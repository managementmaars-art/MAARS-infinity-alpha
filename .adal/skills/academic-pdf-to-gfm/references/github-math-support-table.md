# GitHub GFM Math Support Table

Complete reference for LaTeX commands supported/unsupported on GitHub's GFM renderer (powered by MathJax with KaTeX-compatible subset).

Last verified: 2026-03 (López de Prado 2026 paper conversion, 82 equations)

## Official Open Bug Reports

| Issue                                                                              | What it documents                                                 |
| ---------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| [Community #17143](https://github.com/orgs/community/discussions/17143)            | `\,` `\:` `\;` `\!` stripped by markdown pre-processor (open bug) |
| [Community #121416](https://github.com/orgs/community/discussions/121416)          | `\\` double-backslash stripped in `$$` display blocks (open bug)  |
| [Nico Schlömer analysis](https://nschloe.github.io/2022/05/20/math-on-github.html) | Comprehensive catalog of GitHub math rendering bugs               |

**Gap**: No existing FOSS tool detects the pre-processor stripping issues. They all run AFTER the markdown layer. `validate-math.mjs` in this skill is the only validator that simulates this layer statically.

---

## Environments

| Environment                           | Status           | Notes                                    |
| ------------------------------------- | ---------------- | ---------------------------------------- |
| `\begin{aligned}...\end{aligned}`     | ✅ Supported     | Use inside ` ```math ``` ` if multi-line |
| `\begin{align}...\end{align}`         | ❌ NOT supported | Replace with `aligned`                   |
| `\begin{align*}...\end{align*}`       | ❌ NOT supported | Replace with `aligned`                   |
| `\begin{equation}...\end{equation}`   | ❌ NOT supported | Use `$$` or ` ```math ``` ` block        |
| `\begin{equation*}...\end{equation*}` | ❌ NOT supported | Same                                     |
| `\begin{gather}...\end{gather}`       | ❌ NOT supported | Use multiple `$$` blocks                 |
| `\begin{pmatrix}...\end{pmatrix}`     | ✅ Supported     | Needs ` ```math ``` ` if contains `\\`   |
| `\begin{bmatrix}...\end{bmatrix}`     | ✅ Supported     | Needs ` ```math ``` ` if contains `\\`   |
| `\begin{vmatrix}...\end{vmatrix}`     | ✅ Supported     | Needs ` ```math ``` ` if contains `\\`   |
| `\begin{cases}...\end{cases}`         | ✅ Supported     | Needs ` ```math ``` ` if multi-row       |
| `\begin{array}...\end{array}`         | ✅ Supported     | Needs ` ```math ``` ` if multi-row       |

---

## Display Math Delimiters

| Delimiter                   | Status           | Notes                                         |
| --------------------------- | ---------------- | --------------------------------------------- |
| `$$...$$` (block, own line) | ✅ Supported     | Must have blank line before and after         |
| ` ```math...``` ` (fenced)  | ✅ Supported     | Pre-processor safe — use for any `\\` content |
| `$...$` (inline)            | ✅ Supported     | Single line only                              |
| `\(...\)` (inline)          | ❌ Not supported | Use `$...$`                                   |
| `\[...\]` (display)         | ❌ Not supported | Use `$$` or ` ```math ``` `                   |

---

## Common Math Commands

### Fractions, Roots, Sums

| Command                 | Status | Notes                 |
| ----------------------- | ------ | --------------------- |
| `\frac{}{}`             | ✅     |                       |
| `\dfrac{}{}`            | ✅     | Display-size fraction |
| `\sqrt{}`               | ✅     |                       |
| `\sqrt[n]{}`            | ✅     | nth root              |
| `\sum`, `\prod`, `\int` | ✅     |                       |
| `\sum_{i=1}^{n}`        | ✅     | With limits           |

### Operators and Functions

| Command                        | Status               | Notes                                              |
| ------------------------------ | -------------------- | -------------------------------------------------- |
| `\log`, `\ln`, `\exp`          | ✅                   |                                                    |
| `\sin`, `\cos`, `\tan`         | ✅                   |                                                    |
| `\max`, `\min`, `\sup`, `\inf` | ✅                   |                                                    |
| `\text{}`                      | ✅                   | Text in math                                       |
| `\mathrm{}`                    | ✅                   | Roman text in math                                 |
| `\mathbf{}`                    | ✅                   | Bold math                                          |
| `\mathbb{}`                    | ✅                   | Blackboard bold (ℝ, ℤ, etc.)                       |
| `\operatorname{}`              | ⚠️ Active GitHub bug | Inconsistent; use `\text{}` or `\mathrm{}` instead |

### Accents and Decorators

| Command             | Status | Notes |
| ------------------- | ------ | ----- |
| `\hat{}`            | ✅     |       |
| `\widehat{}`        | ✅     |       |
| `\bar{}`            | ✅     |       |
| `\overline{}`       | ✅     |       |
| `\tilde{}`          | ✅     |       |
| `\vec{}`            | ✅     |       |
| `\dot{}`, `\ddot{}` | ✅     |       |

### Greek Letters

| Command                                                                                   | Status |
| ----------------------------------------------------------------------------------------- | ------ |
| `\alpha`, `\beta`, `\gamma`, `\delta`, `\epsilon`, `\varepsilon`                          | ✅     |
| `\zeta`, `\eta`, `\theta`, `\iota`, `\kappa`, `\lambda`                                   | ✅     |
| `\mu`, `\nu`, `\xi`, `\pi`, `\rho`, `\sigma`                                              | ✅     |
| `\tau`, `\upsilon`, `\phi`, `\varphi`, `\chi`, `\psi`, `\omega`                           | ✅     |
| `\Gamma`, `\Delta`, `\Theta`, `\Lambda`, `\Xi`, `\Pi`, `\Sigma`, `\Phi`, `\Psi`, `\Omega` | ✅     |

### Arrows and Relations

| Command                                        | Status |
| ---------------------------------------------- | ------ |
| `\to`, `\rightarrow`, `\leftarrow`             | ✅     |
| `\Rightarrow`, `\Leftarrow`, `\Leftrightarrow` | ✅     |
| `\leq`, `\geq`, `\neq`, `\approx`, `\equiv`    | ✅     |
| `\in`, `\notin`, `\subset`, `\supset`          | ✅     |
| `\sim`, `\propto`                              | ✅     |

### Delimiters

| Command                         | Status        | Notes                                                  |
| ------------------------------- | ------------- | ------------------------------------------------------ |
| `\left(`, `\right)`             | ✅            |                                                        |
| `\left[`, `\right]`             | ✅            |                                                        |
| `\left\{`, `\right\}`           | ⚠️ GFM-UNSAFE | CommonMark strips `\{`→`{`; use `\left\lbrace` instead |
| `\left\lbrace`, `\right\rbrace` | ✅ GFM-safe   | Letter-based; immune to CommonMark pre-processor       |
| `\left\|`, `\right\|` (double)  | ✅            |                                                        |

---

## Commands to Avoid

| Command                | Problem                                                                                    | Replacement                           |
| ---------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------- |
| `\left\{`, `\right\}`  | ⚠️ CommonMark strips `\{`→`{` so `\left\{`→`\left{` = "Missing or unrecognized delimiter"  | `\left\lbrace`, `\right\rbrace`       |
| `\{...\}` set notation | ⚠️ CommonMark strips `\{`→`{` making `\{x\}` render as invisible group (no visible braces) | `\lbrace...\rbrace`                   |
| `\boxed{}`             | ⚠️ Can cause raw LaTeX passthrough in some GitHub parsing contexts                         | Bold text `**formula**` or blockquote |
| `\operatorname{}`      | ⚠️ Active GitHub bug — renders raw in some contexts                                        | `\text{}` or `\mathrm{}`              |
| `\begin{align}`        | ❌ Not supported at all                                                                    | `\begin{aligned}`                     |
| `\newcommand{}`        | ❌ Was briefly available, then removed by GitHub                                           | Expand macros inline                  |
| `\DeclareMathOperator` | ❌ Never supported                                                                         | `\mathrm{}` per-use                   |
| `\\[8pt]` spacing      | Vertical spacing modifiers stripped by pre-processor                                       | Remove or use ` ```math ``` `         |
| `x^_y`                 | "Missing open brace for superscript"                                                       | `x^{*}_{y}` or brace the superscript  |

---

## The `$$` vs ` ```math ``` ` Decision Tree

````
Does the equation contain any of:
  - \\ (line breaks)
  - \begin{aligned} with multiple rows
  - \begin{pmatrix}, \begin{bmatrix} (matrices)
  - \begin{cases} with multiple cases
  - \\[8pt] or other vertical spacing
?
├── Yes → Use ```math ... ```
└── No  → Use $$ ... $$
````

**When in doubt, use ` ```math ``` `** — it is always safe. The only reason to prefer `$$` is that it renders slightly faster and is more universally supported in non-GitHub renderers (VS Code, Jupyter, etc.).

---

## Display Block Formatting Rules

```markdown
# REQUIRED: blank line before and after each $$ block

$$
E = mc^2
$$

# REQUIRED: blank line between consecutive $$ blocks

$$
a + b = c
$$

$$
d + e = f
$$

# WRONG: consecutive blocks without blank lines

$$
a + b = c
$$

$$
d + e = f   ← GitHub collapses this into the first block
$$
```

---

## KaTeX vs GitHub Rendering Differences

KaTeX validation (`node validate-math.mjs`) catches **parse errors** but NOT GitHub pre-processor issues.

After KaTeX passes, also check:

1. All multi-line blocks (`\\` present) use ` ```math ``` ` not `$$`
2. All `$$` blocks have blank lines before and after
3. No `\boxed{}` usage
4. No `\operatorname{}` usage — use `\text{}` instead
5. No `\begin{align}` — use `\begin{aligned}`
