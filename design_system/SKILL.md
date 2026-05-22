---
name: autoagent-optimizer-design
description: Use this skill to generate well-branded interfaces and assets for AutoAgent Optimizer (AAO) — an OSS-first platform for designing and measuring compound AI systems. Direction is clean modern SaaS (Stripe-soft + Vercel-clean): white surfaces, friendly indigo accent, soft shadows, medium-rounded corners, Geist typography. Contains design tokens, logos, and full UI kits for the workbench app and marketing landing.
user-invocable: true
---

# AutoAgent Optimizer — Design Skill

The brand voice is **friendly + technological** — the way Stripe and Vercel talk. Direct, plain-English, no marketing slop, no AI mysticism, no emoji.

The visuals are **clean modern SaaS**: white surfaces, generous whitespace, one indigo accent, soft shadows, medium-rounded corners (8–10 px), Geist typography throughout.

## How to use this skill

1. **Read `README.md`** first. It contains the full brand foundations:
   - Content fundamentals (voice, vocabulary, examples)
   - Visual foundations (surfaces, color, typography, layout, motion)
   - Iconography (Lucide)
2. **Read `colors_and_type.css`** for every design token: colors, type scale, spacing, radii, shadows, motion timings.
3. **Read `ui_kits/app/` and `ui_kits/landing/`** for high-fidelity component recreations to copy: sidebars, top bars, metric strips, architecture lists, trace viewers, command palette, hero, features, philosophy, proof matrix, CTA, footer.
4. **Use `assets/`** for logos and the favicon. Never recreate the mark by hand.

## When making artifacts

- Pull `<link rel="stylesheet" href="path/to/colors_and_type.css">` so all tokens are available.
- Copy actual logo SVGs out of `assets/`.
- Use Lucide for icons (`<script src="https://unpkg.com/lucide@latest/dist/umd/lucide.min.js">`) — stroke-only, inherits `currentColor`.
- For decks, marketing visuals, prototypes: copy assets locally and produce static HTML.
- For production code: read the rules and apply tokens via CSS variables.

## When the user invokes the skill alone

Ask what they want to build, ask a few targeted questions about audience and depth, then act as an expert designer in this brand — output HTML artifacts or production code as needed.

## Core rules to never break

- **No emoji.** Anywhere.
- **No bluish-purple gradients.** Solid indigo only.
- **No glassmorphism, no AI glow art, no stock photography.**
- **One indigo accent per view.** Reserved for primary action / champion / focus.
- **Sentence case.** Headlines, buttons, labels — always.
- **Numbers carry the message.** Lead with `+4.2 f1, −38 % cost`. Metric names in monospace.
- **Cards have hairlines + soft shadows.** Not heavy borders, not floating heavy drop shadows.
- **Pills (999 px radius) are reserved for status badges only.**
- **Geist for body + headlines, Geist Mono for code/metrics.** Both free on Google Fonts.

## Voice cheat-sheet

> ✓ "Design many architectures. Ship the one that proves itself."
> ✗ "Unleash the power of AI to revolutionize your workflow!"
>
> ✓ "No runs yet. Start your first run to bracket the design space."
> ✗ "✨ Welcome! Let's get started on your AI journey."
>
> ✓ "Champion → arch_b4f · +4.2 f1, −38 % cost · Evidence exported."
> ✗ "Congratulations! Your AI is now optimized 🎉"
