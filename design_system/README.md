# AutoAgent Optimizer — Design System

> **Compound AI systems, designed and measured with evidence.**

This design system covers the visual + verbal language of **AutoAgent Optimizer (AAO)** — an OSS-first platform for discovering, generating, diagnosing and optimizing **compound AI systems**. Engineers use AAO to design many candidate architectures, measure them as white boxes, and ship a deployable *champion* with an evidence base.

The visual direction is **clean, modern SaaS** — Stripe-soft + Vercel-clean. White surfaces, generous whitespace, friendly indigo accent, soft shadows, medium-rounded corners. Friendly and technological.

---

## Sources

Bootstrapped from a written brief only. No codebase, Figma, or prior brand assets attached. All marks, palettes, typography, and components are original to this system.

---

## What's in here

| Path | Purpose |
| --- | --- |
| `README.md` | This file — brand foundations, content rules, visual rules |
| `SKILL.md` | Agent-Skills-compatible loader for use in Claude Code |
| `colors_and_type.css` | All design tokens (colors, type, radii, shadow, spacing) as CSS variables |
| `assets/` | Logos, glyphs, favicon |
| `preview/` | Standalone HTML cards that populate the Design System tab |
| `ui_kits/app/` | Workbench app — runs, architecture comparison, white-box trace, interventions |
| `ui_kits/landing/` | Marketing landing — hero, features, philosophy, proof matrix, CTA |

---

## Content fundamentals

The voice is **friendly + technological**. Clear, confident, low-jargon — the way Stripe and Vercel talk in their product UI. Address the reader directly when it helps; stay impersonal when copying tools or instruments.

### Tone characteristics

| Lean toward | Avoid |
| --- | --- |
| Direct, plain-English engineering terms | "Empower", "unleash", "supercharge" |
| Sentence case, friendly verbs | TITLE CASE MARKETING SHOUTS |
| Concrete measurements (numbers, deltas) | Vague magic ("intelligent", "AI-powered") |
| Honest tradeoffs | Hype |

### Rules

- **Sentence case everywhere.** Headlines, buttons, nav labels, table headers. Title Case is reserved for proper nouns (AutoAgent, GitHub).
- **Second person allowed.** "Start your first run" is fine. Mix freely with imperative ("Compare baselines").
- **No emoji.** Anywhere in product, marketing, docs. Status is communicated by color + label, not faces.
- **Code, identifiers, metric names: monospace.** `f1@k`, `p95_latency_ms`, `arch_b4f.compound`.
- **Numbers carry the message.** Lead with the measurement: `+4.2 f1, −38 % cost. Promoted.`
- **Deltas always carry sign.** `+4.2`, `−1.7`. En-dash minus, space before `%`.

### Vocabulary

**Use:** baseline, candidate, champion, architecture, compound system, white-box trace, middle-metric, bottleneck, targeted intervention, HITL gate, budget, regression, evidence, deployable, deterministic, tool call, retrieval, judgement, runtime constraint.

**Avoid:** "magic", "wizard", "smart", "AI assistant", "co-pilot", "powered by AI", "LLM-first".

### Example copy

> **Hero:**
> Design many architectures. Ship the one that proves itself.
>
> **Sub-hero:**
> AutoAgent Optimizer generates architecturally distinct baselines for the same task, measures them as white boxes, and returns a deployable champion — with the trace, the budget, and the regression matrix to back it up.
>
> **Empty state:**
> No runs yet. Start your first run to bracket the design space.
>
> **Toast (champion promoted):**
> Champion → `arch_b4f.compound` · +4.2 f1, −38 % cost · Evidence exported.

---

## Visual foundations

### Surfaces

- **Default page background:** white (`#FFFFFF`) for the app; warm-white (`#FAFAFA`) for landing sections.
- **Cards** sit on either of those, with a hairline border (`1 px var(--border-muted)`) and a soft drop shadow.
- **Dark surfaces** appear only for the CTA section and the optional dark theme — never as default.
- **No grids, no graph paper, no schematic textures.** Plenty of generous whitespace does the structural work.

### Color usage

- **Indigo is the one accent.** It marks the primary action, the champion, the active row, focus rings, link color. Used as **solid only — never gradients.**
- **Status colors** (green/amber/red/blue) are reserved for status: champion, pending, regression, info. Don't decorate with them.
- **Hierarchy lives in the neutrals.** `gray-900` for primary text, `gray-700` for body, `gray-500` for secondary, `gray-400` for tertiary/captions.

### Typography

**One family does the whole system: Geist** (sans) + **Geist Mono**. No serifs, no display fonts, no editorial drama.

- **Display & headlines:** Geist 600, tracking −0.025 to −0.035em. Sentence case.
- **Body:** Geist 400, 14–15 px, line-height 1.5–1.65, `gray-700` on white.
- **UI:** Geist 500, 13–14 px.
- **Code / metrics / identifiers:** Geist Mono 400–600.

Both fonts loaded from Google Fonts — open-licensed, no substitutions needed.

### Layout

- **12-column grid**, generous gutters (40–80 px on hero surfaces, 20–32 px in app).
- **Max content widths:** 1240 px on marketing, 1440 px on app.
- **Sidebar** in the app is a fixed 264 px; main is fluid; right rail is 340 px.
- **8 px baseline.** All spacing on 4-px multiples, most on 8.

### Borders & radii

- **Radii are medium-soft.** 4 px on chips, 6 px on inputs, 8 px on buttons + small cards, 10 px on cards, 12 px on panels, 16 px on hero containers, 24 px on big feature blocks.
- **Pills (`999 px`) are reserved for status indicators and small badges** like the champion pill.
- **Borders are single solid hairlines** (`1 px var(--border-muted)`). No 2-px bars, no dashed borders.

### Elevation & shadows

Five levels of soft, warm shadows (`--shadow-xs` through `--shadow-xl`). Cards default to `--shadow-sm`; hover lifts to `--shadow-md`. Modals and command palette use `--shadow-xl`. Shadows are always cool-gray, never colored.

### Hover, press, focus

- **Hover** on links and nav rows: shift background to `gray-100` (or stronger if needed). No underline flicker.
- **Hover** on primary buttons: shift to `accent-hover` (slightly darker indigo).
- **Press**: 1 px translateY downward + subtle inset shadow.
- **Focus**: 3 px indigo glow (`--focus-ring`) — always visible on keyboard nav.
- **Disabled**: 45 % opacity, no pointer events.

### Motion

- Default: **220 ms** with `cubic-bezier(0.22, 0.61, 0.36, 1)` (snappy `--ease-out`).
- **Fades and slides — no springs, no bounces.**
- Sparklines and trace bars animate on mount only.
- The champion's lime ring (1 px indigo glow) is the only "celebration" motion — fades in over 320 ms when promoted.

### Imagery

- **No stock photography.** No abstract AI glow art. No bluish-purple gradients.
- Functional diagrams only: sparklines, trace timelines, regression matrices, DAG graphs.
- One subtle radial glow on the hero (indigo at 6 % opacity, ellipse) — that's it for "decoration".

---

## Iconography

**Lucide** (lucide.dev) — chosen for its 1.5–1.7 px stroke, clean geometry, and friendly feel.

> Substitution flagged: No prior icon set provided. If you have proprietary icons, drop SVGs in `assets/icons/`.

### Rules

- **Stroke icons only.** Default 24 px box, 1.6 px stroke.
- **Inherits `currentColor`.** No hardcoded fills.
- **Sizes:** 14 (inline-with-text), 16 (dense rows), 20 (nav), 24 (headers), 40 (empty-state).
- **No emoji.** Anywhere.
- **Common icons:** `git-branch`, `target`, `gauge`, `activity`, `boxes`, `cpu`, `flask-conical`, `route`, `sparkles`, `git-compare`, `coins`, `user-check`.

### Load

```html
<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js"></script>
```
Then `<i data-lucide="git-branch"></i>` and call `lucide.createIcons()`.

### Brand glyphs (in `assets/`)

- `logo-mark.svg` — primary mark (indigo tile + compound network glyph)
- `logo-mark-inverse.svg` — for dark surfaces
- `logo-lockup.svg` — mark + "AutoAgent Optimizer" wordmark
- `logo-lockup-inverse.svg` — lockup on dark
- `favicon.svg` — 32 px favicon
