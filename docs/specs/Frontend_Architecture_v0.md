# Frontend Architecture v0

## Purpose

Р—Р°С„РёРєСЃРёСЂРѕРІР°С‚СЊ С†РµР»РµРІСѓСЋ Р°СЂС…РёС‚РµРєС‚СѓСЂСѓ С„СЂРѕРЅС‚РµРЅРґР° AutoAgent Optimizer РІ С„РѕСЂРјР°С‚Рµ `React + TypeScript`, С‡С‚РѕР±С‹:

1. РЅРµ РїРµСЂРµРґРµР»С‹РІР°С‚СЊ UI РЅР° РєР°Р¶РґРѕРј СЃР»Р°Р№СЃРµ;
2. СЂР°Р·РІРёРІР°С‚СЊ С„СѓРЅРєС†РёРѕРЅР°Р» РёС‚РµСЂР°С†РёРѕРЅРЅРѕ С‡РµСЂРµР· "СЂР°Р·Р±Р»РѕРєРёСЂРѕРІРєСѓ" capability;
3. РґРµСЂР¶Р°С‚СЊ СЃРёРЅС…СЂРѕРЅРЅРѕСЃС‚СЊ `Backend + Frontend + Demo + QA`.

Р”РѕРєСѓРјРµРЅС‚ Р·Р°РґР°РµС‚ РєР°СЂРєР°СЃ СЂР°Р±РѕС‡РµРіРѕ РїСЂРёР»РѕР¶РµРЅРёСЏ (Р° РЅРµ РІСЂРµРјРµРЅРЅРѕР№ Р·Р°РіР»СѓС€РєРё), РіРґРµ РЅРµРґРѕСЃС‚СѓРїРЅС‹Рµ С„СѓРЅРєС†РёРё РІРёРґРёРјС‹, РЅРѕ РїРѕРјРµС‡РµРЅС‹ РєР°Рє `planned/locked` РґРѕ РіРѕС‚РѕРІРЅРѕСЃС‚Рё backend-РєРѕРЅС‚СЂР°РєС‚РѕРІ.

## Scope v0

Р’С…РѕРґРёС‚ РІ v0:

1. Р°СЂС…РёС‚РµРєС‚СѓСЂРЅС‹Р№ РєР°СЂРєР°СЃ SPA РЅР° `React + TypeScript`;
2. СЃС‚Р°Р±РёР»СЊРЅС‹Рµ UI-РєРѕРЅС‚СЂР°РєС‚С‹ capability C1..C6;
3. СЃС‚СЂР°С‚РµРіРёСЏ СЃРѕСЃС‚РѕСЏРЅРёСЏ, СЂРѕСѓС‚РёРЅРіР° Рё РёСЃРїРѕР»РЅРµРЅРёСЏ run;
4. РёРЅС‚РµРіСЂР°С†РёСЏ СЃ РґРёР·Р°Р№РЅ-СЃРёСЃС‚РµРјРѕР№ РєР°Рє РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Р№ СЃС‚Р°РЅРґР°СЂС‚;
5. РїСЂР°РІРёР»Р° С‚РµСЃС‚РёСЂРѕРІР°РЅРёСЏ С„СЂРѕРЅС‚РµРЅРґР° Рё demo-acceptance.

РќРµ РІС…РѕРґРёС‚ РІ v0:

1. РїРѕР»РЅС‹Р№ production-СѓСЂРѕРІРµРЅСЊ auth/tenant model;
2. С„РёРЅР°Р»СЊРЅС‹Р№ real-time transport (SSE/WebSocket) РґР»СЏ РІСЃРµС… СЃС†РµРЅР°СЂРёРµРІ;
3. exhaustive UI-РїРѕРєСЂС‹С‚РёРµ РІСЃРµС… Р±СѓРґСѓС‰РёС… advanced-С„СѓРЅРєС†РёР№.

## Design Principles

1. `Product-shaped shell first`: СЃСЂР°Р·Сѓ СЃС‚СЂРѕРёРј СЃС‚СЂСѓРєС‚СѓСЂСѓ РєРѕРЅРµС‡РЅРѕРіРѕ РїСЂРёР»РѕР¶РµРЅРёСЏ.
2. `Capability unlock model`: UI СЌРєСЂР°РЅС‹ РµСЃС‚СЊ Р·Р°СЂР°РЅРµРµ, РЅРѕ Р°РєС‚РёРІРёСЂСѓСЋС‚СЃСЏ РїРѕ РјРµСЂРµ РіРѕС‚РѕРІРЅРѕСЃС‚Рё backend.
3. `Stable contracts first`: С‚РёРїС‹ Р·Р°РїСЂРѕСЃРѕРІ/РѕС‚РІРµС‚РѕРІ С„РёРєСЃРёСЂСѓСЋС‚СЃСЏ РґРѕ СЂР°СЃС€РёСЂРµРЅРёСЏ С„СѓРЅРєС†РёРѕРЅР°Р»Р°.
4. `Observable by default`: РєР°Р¶РґС‹Р№ run Рё С€Р°Рі РѕС‚РѕР±СЂР°Р¶Р°СЋС‚СЃСЏ РІ trace/diagnostics.
5. `Design-system only`: UI СЃС‚СЂРѕРёС‚СЃСЏ СЃС‚СЂРѕРіРѕ РїРѕ `design_system`.
6. `UX North Star first`: РІРёР·СѓР°Р»СЊРЅР°СЏ Рё РїРѕРІРµРґРµРЅС‡РµСЃРєР°СЏ РєРѕРјРїРѕР·РёС†РёСЏ СЃС‚СЂРѕРёС‚СЃСЏ РїРѕ СЂРµС„РµСЂРµРЅСЃСѓ `design_system/screenshots/app-v3.png`.

## UX North Star (app-v3)

Р‘Р°Р·РѕРІС‹Р№ UX-СЂРµС„РµСЂРµРЅСЃ РґР»СЏ workbench-РёРЅС‚РµСЂС„РµР№СЃР°:

1. [app-v3.png](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/design_system/screenshots/app-v3.png)

РћР±СЏР·Р°С‚РµР»СЊРЅС‹Рµ РїСЂРёРЅС†РёРїС‹ РєРѕРјРїРѕР·РёС†РёРё:

1. Р”Р»СЏ `Battle Workspace` СЃРѕС…СЂР°РЅСЏРµС‚СЃСЏ app-v3 РєРѕРјРїРѕР·РёС†РёСЏ РєР°Рє North Star.
2. Р”Р»СЏ `Battles Hub` РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ СѓРїСЂРѕС‰РµРЅРЅР°СЏ РєРѕРјРїРѕР·РёС†РёСЏ Р±РµР· РїСЂР°РІРѕРіРѕ rail.
3. run-centric header, KPI Рё intervention rail РѕС‚РЅРѕСЃСЏС‚СЃСЏ С‚РѕР»СЊРєРѕ Рє `Battle Workspace`.
4. Р’Р°Р¶РЅС‹Рµ РґРµР№СЃС‚РІРёСЏ РїСЂРѕРµРєС‚Р° (`compare`, `promote champion`, `apply intervention`, `export`) Р¶РёРІСѓС‚ РІ `Battle Workspace`.
5. РќРѕРІС‹Рµ capability РІСЃС‚СЂР°РёРІР°СЋС‚СЃСЏ РІ РєРѕРјРїРѕР·РёС†РёСЋ `Battle Workspace`, Р° РЅРµ РІ `Battles Hub`.

Р­С‚Рѕ РЅРµ "РїРёРєСЃРµР»СЊ-РїРµСЂС„РµРєС‚ РєРѕРїРёСЏ", Р° РѕР±СЏР·Р°С‚РµР»СЊРЅР°СЏ РїСЂРѕРґСѓРєС‚РѕРІР°СЏ СЂР°РјРєР° UX-СЃС‚СЂСѓРєС‚СѓСЂС‹.

## Tech Stack

1. `React 19+` (functional components, hooks).
2. `TypeScript` (strict mode).
3. `Vite` РєР°Рє dev/build toolchain.
4. `React Router` РґР»СЏ app routing.
5. `TanStack Query` РґР»СЏ server state Рё polling.
6. `Zustand` (РёР»Рё СЌРєРІРёРІР°Р»РµРЅС‚РЅС‹Р№ lightweight store) РґР»СЏ Р»РѕРєР°Р»СЊРЅРѕРіРѕ app state.
7. `Vitest + Testing Library + Playwright` РґР»СЏ unit/integration/e2e.

## High-Level Topology

```text
Browser (React/TS SPA)
  -> Frontend API Client (typed)
  -> Backend API (optimizer services / BFF)
  -> Execution Runtime (DSL run / Native run / Evaluation runners)
  -> Artifacts (reports, traces, evidence packs)
```

## Application Information Architecture

РљР»СЋС‡РµРІР°СЏ SaaS-РѕРіРѕРІРѕСЂРєР°:

1. Р’ РїРѕР»СЊР·РѕРІР°С‚РµР»СЊСЃРєРѕРј UX `Workspace = Project`.
2. РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ СЃРЅР°С‡Р°Р»Р° РїРѕРїР°РґР°РµС‚ РЅР° РѕС‚РґРµР»СЊРЅС‹Р№ СЃРїРёСЃРѕРє СЃРІРѕРёС… РїСЂРѕРµРєС‚РѕРІ.
3. Р’РЅСѓС‚СЂРё РєРѕРЅРєСЂРµС‚РЅРѕРіРѕ РїСЂРѕРµРєС‚Р° РѕС‚РєСЂС‹РІР°РµС‚СЃСЏ РѕС‚РґРµР»СЊРЅС‹Р№ СЂР°Р±РѕС‡РёР№ СЌРєСЂР°РЅ РїСЂРѕРµРєС‚Р°.

РћСЃРЅРѕРІРЅС‹Рµ СЌРєСЂР°РЅС‹:

1. `Battles Hub` (С‚РѕР»СЊРєРѕ СЃРїРёСЃРѕРє РїСЂРѕРµРєС‚РѕРІ РєР»РёРµРЅС‚Р° + СЃРѕР·РґР°РЅРёРµ РїСЂРѕРµРєС‚Р°).
2. `Battle Workspace` (С‡Р°С‚, РєР°РЅРґРёРґР°С‚С‹, РґР°С‚Р°СЃРµС‚С‹, РјРµС‚СЂРёРєРё, СЂР°РЅС‹, РѕС‚С‡РµС‚С‹, champion).
3. `Settings`.

Р Р°Р·РґРµР»С‹ РІРЅСѓС‚СЂРё `Battle Workspace`:

1. `Battle Chat`
2. `Candidates`
3. `Datasets`
4. `Metrics & Evaluators`
5. `Optimizer Runs`
6. `Reports`
7. `Champion`

РљР°Р¶РґС‹Р№ СЂР°Р·РґРµР» РёРјРµРµС‚:

1. `enabled` (С„СѓРЅРєС†РёСЏ РґРѕСЃС‚СѓРїРЅР°);
2. `planned` (С„СѓРЅРєС†РёСЏ РІРёРґРЅР°, РЅРѕ РµС‰Рµ Р·Р°РєСЂС‹С‚Р°);
3. `beta` (С„СѓРЅРєС†РёСЏ РґРѕСЃС‚СѓРїРЅР° СЃ РїРѕРјРµС‚РєРѕР№ РѕРіСЂР°РЅРёС‡РµРЅРёР№).

## Core User Flow (v0 target)

Р¦РµРЅС‚СЂР°Р»СЊРЅС‹Р№ flow РґР»СЏ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ:

1. РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РѕС‚РєСЂС‹РІР°РµС‚ `Battles Hub` Рё РІРёРґРёС‚ С‚РѕР»СЊРєРѕ СЃРІРѕРё РїСЂРѕРµРєС‚С‹.
2. РЎРѕР·РґР°РµС‚ РЅРѕРІС‹Р№ РїСЂРѕРµРєС‚ (workspace) РёР»Рё РѕС‚РєСЂС‹РІР°РµС‚ СЃСѓС‰РµСЃС‚РІСѓСЋС‰РёР№.
3. РџРµСЂРµС…РѕРґРёС‚ РІ РѕС‚РґРµР»СЊРЅС‹Р№ `Battle Workspace`.
4. Р’ `Battle Chat` С„РѕСЂРјСѓР»РёСЂСѓРµС‚ Р·Р°РґР°С‡Сѓ РµСЃС‚РµСЃС‚РІРµРЅРЅС‹Рј СЏР·С‹РєРѕРј.
5. РР РїСЂРµРґР»Р°РіР°РµС‚ РєР°РЅРґРёРґР°С‚РѕРІ РЅР° Р±Р°Р·Рµ pattern library + РѕРіСЂР°РЅРёС‡РµРЅРёР№ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ.
6. РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РїРѕРґС‚РІРµСЂР¶РґР°РµС‚/РёСЃРєР»СЋС‡Р°РµС‚ РїР°С‚С‚РµСЂРЅС‹, РїРѕР»СѓС‡Р°РµС‚ РЅР°Р±РѕСЂ candidate-Р°РіРµРЅС‚РѕРІ.
7. РЎРёСЃС‚РµРјР° РІРЅСѓС‚СЂРµРЅРЅРµ РІР°Р»РёРґРёСЂСѓРµС‚/РєРѕРјРїРёР»РёСЂСѓРµС‚ РєР°РЅРґРёРґР°С‚РѕРІ (Р±РµР· СЂСѓС‡РЅРѕР№ DSL-СЂР°Р±РѕС‚С‹).
8. РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ С„РѕСЂРјРёСЂСѓРµС‚ dataset (СЂСѓС‡РЅРѕР№ РІРІРѕРґ/Р·Р°РіСЂСѓР·РєР°/РР-СЃРёРЅС‚РµР·/РѕС‡РёСЃС‚РєР°).
9. РџРѕР»СЊР·РѕРІР°С‚РµР»СЊ РЅР°СЃС‚СЂР°РёРІР°РµС‚ РјРµС‚СЂРёРєРё/evaluators Рё optimizer policy.
10. Р—Р°РїСѓСЃРєР°РµС‚ РѕРїС‚РёРјРёР·Р°С†РёСЋ, РЅР°Р±Р»СЋРґР°РµС‚ РїСЂРѕРіСЂРµСЃСЃ/Р»РѕРіРё/РјРµС‚СЂРёРєРё РІ РіР»СѓР±РёРЅСѓ.
11. РџРѕР»СѓС‡Р°РµС‚ Р°РЅР°Р»РёС‚РёС‡РµСЃРєРёР№ РѕС‚С‡РµС‚, РІС‹Р±РёСЂР°РµС‚ winner.
12. Р­РєСЃРїРѕСЂС‚РёСЂСѓРµС‚ champion РІ native.
13. РћРїС†РёРѕРЅР°Р»СЊРЅРѕ РёРјРїРѕСЂС‚РёСЂСѓРµС‚ РёР·РјРµРЅРµРЅРЅС‹Р№ native agent РѕР±СЂР°С‚РЅРѕ Рё РїРѕРІС‚РѕСЂСЏРµС‚ С†РёРєР» РѕС†РµРЅРєРё.

## Layout Rules (SaaS)

РћР±СЏР·Р°С‚РµР»СЊРЅС‹Рµ РїСЂР°РІРёР»Р° РєРѕРјРїРѕРЅРѕРІРєРё:

1. РќР° `Battles Hub` РЅРµС‚ РїСЂР°РІРѕРіРѕ operational rail.
2. Р›РµРІС‹Р№ РєР°СЂРєР°СЃ (navigation/settings zone) РЅРµ СѓРµР·Р¶Р°РµС‚ РїСЂРё РїСЂРѕРєСЂСѓС‚РєРµ.
3. РќРёР¶РЅРёР№ Р±Р»РѕРє РїСЂРѕС„РёР»СЏ/РЅР°СЃС‚СЂРѕРµРє РІСЃРµРіРґР° РїСЂРёР±РёС‚ Рє РЅРёР·Сѓ viewport.
4. РџСЂРѕРєСЂСѓС‚РєР° РґРѕР»Р¶РЅР° РїСЂРѕРёСЃС…РѕРґРёС‚СЊ РІ РєРѕРЅС‚РµРЅС‚РЅРѕР№ РѕР±Р»Р°СЃС‚Рё, Р° РЅРµ РІРѕ РІСЃРµРј app-shell.
5. Capability-РјРµРЅСЋ C2..C6 РЅРµ РїРѕРєР°Р·С‹РІР°РµС‚СЃСЏ РЅР° `Battles Hub`; РѕРЅРѕ Р¶РёРІРµС‚ РІ `Battle Workspace`.

## Multi-User and Tenant Scope

Frontend РёР·РЅР°С‡Р°Р»СЊРЅРѕ РїСЂРѕРµРєС‚РёСЂСѓРµС‚СЃСЏ РєР°Рє multi-tenant SaaS:

1. Р›СЋР±РѕР№ СЃРїРёСЃРѕРє РїСЂРѕРµРєС‚РѕРІ РѕС‚РѕР±СЂР°Р¶Р°РµС‚ С‚РѕР»СЊРєРѕ tenant-scoped РґР°РЅРЅС‹Рµ РїРѕР»СЊР·РѕРІР°С‚РµР»СЏ.
2. РђРєС‚РёРІРЅС‹Р№ РєРѕРЅС‚РµРєСЃС‚ РІ UI: `tenant -> project`.
3. Р”РѕСЃС‚СѓРї Рє РїСЂРѕРµРєС‚Сѓ РїРѕ id РІСЃРµРіРґР° РїРѕРґС‚РІРµСЂР¶РґР°РµС‚СЃСЏ backend (РЅРµР»СЊР·СЏ РґРѕРІРµСЂСЏС‚СЊ С‚РѕР»СЊРєРѕ frontend state).

## Capability Contract Model

`/api/capabilities` РІРѕР·РІСЂР°С‰Р°РµС‚ РєР°С‚Р°Р»РѕРі С„СѓРЅРєС†РёР№, РєРѕС‚РѕСЂС‹Рј СѓРїСЂР°РІР»СЏРµС‚СЃСЏ РґРѕСЃС‚СѓРїРЅРѕСЃС‚СЊ UI:

1. `id`;
2. `title`;
3. `status` (`enabled|planned|beta|disabled`);
4. `routes`;
5. `required_backends`;
6. `notes`.

Product capability map (РЅРѕРІР°СЏ С†РµР»РµРІР°СЏ РјРѕРґРµР»СЊ):

1. `C1` Battle Registry
2. `C2` Task Chat + Candidate Generation
3. `C3` Pattern Library + RAG Retrieval
4. `C4` Dataset & Metrics Studio
5. `C5` Optimizer Run Monitor
6. `C6` Report + Champion Export/Import

Frontend РЅРµ "СѓРіР°РґС‹РІР°РµС‚" РіРѕС‚РѕРІРЅРѕСЃС‚СЊ, Р° С‡РёС‚Р°РµС‚ capability-РјР°РЅРёС„РµСЃС‚ РѕС‚ backend.

## Frontend Module Boundaries

1. `app/`
2. `pages/`
3. `widgets/`
4. `features/`
5. `entities/`
6. `shared/`
7. `processes/`

Р РµРєРѕРјРµРЅРґСѓРµРјР°СЏ РѕС‚РІРµС‚СЃС‚РІРµРЅРЅРѕСЃС‚СЊ:

1. `app`: bootstrapping, providers, router.
2. `pages`: route-level composition.
3. `widgets`: РєСЂСѓРїРЅС‹Рµ UI-Р±Р»РѕРєРё СЌРєСЂР°РЅРѕРІ.
4. `features`: user actions/use-cases (run arena, export champion).
5. `entities`: РґРѕРјРµРЅРЅС‹Рµ РјРѕРґРµР»Рё (profile, run, candidate, metric).
6. `shared`: UI-kit wrappers, utils, api client.
7. `processes`: РґР»РёРЅРЅС‹Рµ Р±РёР·РЅРµСЃ-РїРѕС‚РѕРєРё (benchmark loop, post-export loop).

## State Model

Р Р°Р·РґРµР»РµРЅРёРµ СЃРѕСЃС‚РѕСЏРЅРёСЏ:

1. `Server state`: TanStack Query (`workspaces`, `projects`, `candidates`, `datasets`, `runs`, `reports`, `capabilities`).
2. `Session/UI state`: РІС‹Р±СЂР°РЅРЅС‹Р№ battle/arena, Р°РєС‚РёРІРЅС‹Рµ РїР°РЅРµР»Рё, С„РёР»СЊС‚СЂС‹, layout.
3. `Project state machine`: `draft -> candidate_design -> candidate_ready -> dataset_ready -> run_ready -> running -> analyzed -> champion_selected`.

РљР»СЋС‡РµРІС‹Рµ СЃСѓС‰РЅРѕСЃС‚Рё UI:

1. `WorkspaceEnvelope`
2. `ProjectEnvelope`
3. `CandidateSetEnvelope`
4. `RunEnvelope`

`RunEnvelope` РјРёРЅРёРјСѓРј СЃРѕРґРµСЂР¶РёС‚:

1. `run_id`;
2. `project_id`;
3. `versions_manifest` (agents/datasets/metrics/evaluators/prompts/tools/settings);
4. `status`;
5. `comparative_metrics`;
6. `diagnostic_signals`;
7. `artifacts`.

## API Contract Strategy

РџСЂР°РІРёР»Рѕ: UI СЂР°Р±РѕС‚Р°РµС‚ С‚РѕР»СЊРєРѕ СЃ С‚РёРїРёР·РёСЂРѕРІР°РЅРЅС‹РјРё DTO Рё runtime-validation РЅР° РіСЂР°РЅРёС†Рµ (zod/io-ts СЌРєРІРёРІР°Р»РµРЅС‚).

РњРёРЅРёРјР°Р»СЊРЅС‹Рµ РєРѕРЅС‚СЂР°РєС‚С‹:

1. health/capabilities;
2. tenant-scoped projects CRUD/list;
3. chat task brief + candidate generation session;
4. pattern library retrieval & selection/exclusion;
5. internal candidate validate/compile readiness;
6. dataset/metrics/evaluator configuration;
7. optimizer run orchestration & monitoring;
8. evidence/champion artifacts metadata;
9. native import/export + compatibility/preflight results.

Р›СЋР±РѕРµ РёР·РјРµРЅРµРЅРёРµ backend-С„РѕСЂРјР°С‚Р°:

1. СЃРЅР°С‡Р°Р»Р° С„РёРєСЃРёСЂСѓРµС‚СЃСЏ РІ spec/ADR;
2. Р·Р°С‚РµРј РѕР±РЅРѕРІР»СЏСЋС‚СЃСЏ TS-С‚РёРїС‹ Рё РєРѕРЅС‚СЂР°РєС‚РЅС‹Рµ С‚РµСЃС‚С‹;
3. С‚РѕР»СЊРєРѕ РїРѕСЃР»Рµ СЌС‚РѕРіРѕ СЂР°СЃС€РёСЂСЏРµС‚СЃСЏ UI.

## Comparative Metrics vs Diagnostic Signals in UI

UI РѕС‚РѕР±СЂР°Р¶Р°РµС‚ РґРІР° СЂР°Р·РЅС‹С… СЃР»РѕСЏ:

1. `Comparative Metrics`:
2. `Diagnostic Signals`:

`Comparative Metrics`:
1. РёСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ РґР»СЏ ranking Рё РІС‹Р±РѕСЂР° winner;
2. РЅРѕСЂРјР°Р»РёР·СѓСЋС‚СЃСЏ РґР»СЏ СЃСЂР°РІРЅРµРЅРёСЏ СЂР°Р·РЅС‹С… РєР°РЅРґРёРґР°С‚РѕРІ;
3. РїРѕРєР°Р·С‹РІР°СЋС‚СЃСЏ РєР°Рє scoreboard/leaderboard.

`Diagnostic Signals`:
1. РЅРµ СѓС‡Р°СЃС‚РІСѓСЋС‚ РЅР°РїСЂСЏРјСѓСЋ РІ С„РёРЅР°Р»СЊРЅРѕРј СЂР°РЅР¶РёСЂРѕРІР°РЅРёРё (РµСЃР»Рё РЅРµ Р·Р°РґР°РЅРѕ РёРЅРѕРµ РїСЂРѕС„РёР»РµРј);
2. РїРѕРєР°Р·С‹РІР°СЋС‚ "РіРґРµ РёРјРµРЅРЅРѕ Р»РѕРјР°РµС‚СЃСЏ РїР°Р№РїР»Р°Р№РЅ" РїРѕ С€Р°РіР°Рј;
3. РёСЃРїРѕР»СЊР·СѓСЋС‚СЃСЏ РґР»СЏ С‚РѕС‡РµС‡РЅРѕРіРѕ СѓР»СѓС‡С€РµРЅРёСЏ Р°СЂС…РёС‚РµРєС‚СѓСЂС‹.

Р”Р»СЏ СЂР°Р·РЅРѕС‚РёРїРЅС‹С… Р·Р°РґР°С‡ СЃРѕСЃС‚Р°РІ РѕР±РѕРёС… СЃР»РѕРµРІ Р·Р°РґР°РµС‚СЃСЏ РїСЂРѕС„РёР»РµРј РѕС†РµРЅРєРё, Р° РЅРµ С…Р°СЂРґРєРѕРґРѕРј РІ UI.

## Budget and Cost UX

UI РґРѕР»Р¶РµРЅ СЏРІРЅРѕ РїРѕРєР°Р·С‹РІР°С‚СЊ:

1. Р±СЋРґР¶РµС‚ РїСЂРѕС„РёР»СЏ (`max_cases`, `max_llm_calls`, `max_cost_usd`, `timebox`);
2. С„Р°РєС‚РёС‡РµСЃРєРѕРµ РїРѕС‚СЂРµР±Р»РµРЅРёРµ;
3. РїСЂРёС‡РёРЅСѓ РѕСЃС‚Р°РЅРѕРІРєРё (`budget_exceeded`, `manual_stop`, `completed`).

Р•РґРёРЅРёС†С‹ РёР·РјРµСЂРµРЅРёСЏ:

1. `llm_calls_total` (С€С‚.);
2. `cost_usd_total` (USD);
3. `latency_ms_p50/p95` (РјСЃ).

## Design System Compliance

РћР±СЏР·Р°С‚РµР»СЊРЅС‹Рµ РїСЂР°РІРёР»Р°:

1. С‚РѕРєРµРЅС‹ С‚РѕР»СЊРєРѕ РёР· `design_system/colors_and_type.css`;
2. РєРѕРјРїРѕР·РёС†РёРё Рё РїР°С‚С‚РµСЂРЅС‹ РёР· `design_system/ui_kits/app/*`;
3. Р±СЂРµРЅРґ-Р°СЃСЃРµС‚С‹ С‚РѕР»СЊРєРѕ РёР· `design_system/assets/*`;
4. voice/copy РїРѕ РїСЂР°РІРёР»Р°Рј `design_system/README.md`.

РќР°СЂСѓС€РµРЅРёРµ СЌС‚РёС… РїСЂР°РІРёР» Р±Р»РѕРєРёСЂСѓРµС‚ РїСЂРёРµРјРєСѓ frontend-СЃР»Р°Р№СЃР°.

## Testing Strategy (Frontend)

РўРµСЃС‚РѕРІР°СЏ РїРёСЂР°РјРёРґР°:

1. unit: hooks, formatters, state reducers, DTO-mappers;
2. integration: page + API mock contracts;
3. e2e: РєР»СЋС‡РµРІС‹Рµ user flows РІ Р±СЂР°СѓР·РµСЂРµ РЅР° Р»РѕРєР°Р»СЊРЅРѕРј СЃС‚РµРЅРґРµ.

РњРёРЅРёРјСѓРј РґР»СЏ РєР°Р¶РґРѕРіРѕ frontend-СЃР»Р°Р№СЃР°:

1. unit-С‚РµСЃС‚С‹ РЅРѕРІРѕРіРѕ РґРѕРјРµРЅРЅРѕРіРѕ РєРѕРґР°;
2. integration-С‚РµСЃС‚ СЌРєСЂР°РЅРЅРѕРіРѕ РїРѕРІРµРґРµРЅРёСЏ;
3. e2e smoke РґР»СЏ РѕСЃРЅРѕРІРЅРѕРіРѕ happy-path.

Test gates РґР»СЏ frontend delivery:

1. `Fast gate` (frontend-only): `python -m pytest tests/unit/test_frontend_contracts.py` + `python -m pytest tests/e2e/test_frontend_shell_smoke_script.py`.
2. `Targeted gate` (frontend + API-СЃСЂРµР·): fast gate + `python -m pytest tests/integration/test_frontend_dev_server.py` + РїСЂРѕС„РёР»СЊРЅС‹Рµ backend integration/e2e С‚РµСЃС‚С‹ РїРѕ Р·Р°С‚СЂРѕРЅСѓС‚С‹Рј endpoint.
3. `Full gate` (РєСЂСѓРїРЅС‹Р№ СЃР»Р°Р№СЃ/release): `python -m pytest` + frontend test suite.

РћРїРµСЂР°С†РёРѕРЅРЅРѕРµ РїСЂР°РІРёР»Рѕ: РїРѕСЃР»Рµ РёР·РјРµРЅРµРЅРёСЏ backend API frontend РѕР±СЏР·Р°РЅ СЂР°Р±РѕС‚Р°С‚СЊ РїСЂРѕС‚РёРІ РїРµСЂРµР·Р°РїСѓС‰РµРЅРЅРѕРіРѕ dev server; РёРЅР°С‡Рµ РІРѕР·РјРѕР¶РЅС‹ Р»РѕР¶РЅС‹Рµ `404` РЅР° `/api/*` РёР·-Р·Р° СЃС‚Р°СЂРѕРіРѕ РїСЂРѕС†РµСЃСЃР°.

## Demo Contract (v0)

Р”РµРјРѕ РґРѕР»Р¶РЅРѕ РїРѕРєР°Р·С‹РІР°С‚СЊ РЅРµ "РјРѕРє-СЃС‚СЂР°РЅРёС†Сѓ", Р° СЂР°Р±РѕС‡РёР№ РєРѕРЅС‚СѓСЂ:

1. Р·Р°РіСЂСѓР·РєР° capability-РєР°С‚Р°Р»РѕРіР°;
2. Р·Р°РїСѓСЃРє РјРёРЅРёРјСѓРј РѕРґРЅРѕРіРѕ СЂРµР°Р»СЊРЅРѕРіРѕ backend-СЃС†РµРЅР°СЂРёСЏ;
3. РѕС‚РѕР±СЂР°Р¶РµРЅРёРµ ranking + diagnostics;
4. РїРµСЂРµС…РѕРґ Рє champion/export Р°СЂС‚РµС„Р°РєС‚Р°Рј.

## Delivery Plan Alignment

Frontend СЂР°Р·РІРёРІР°РµС‚СЃСЏ РІРµСЂС‚РёРєР°Р»СЊРЅРѕ, СЃРёРЅС…СЂРѕРЅРЅРѕ СЃ backend:

1. РІ РєР°Р¶РґРѕРј СЃР»Р°Р№СЃРµ С„РёРєСЃРёСЂСѓРµС‚СЃСЏ, РєР°РєРёРµ capability СЃС‚Р°Р»Рё `enabled`;
2. UI РґР»СЏ РѕСЃС‚Р°Р»СЊРЅС‹С… capability РѕСЃС‚Р°РµС‚СЃСЏ РІРёРґРёРјС‹Рј (`planned`);
3. Roadmap РѕР±РЅРѕРІР»СЏРµС‚СЃСЏ РїРѕ РјРѕРґРµР»Рё `BE + FE + Demo + QA` РІ РѕРґРЅРѕРј СЃР»Р°Р№СЃРµ.

## Missing Elements (Gap Analysis)

РљР»СЋС‡РµРІС‹Рµ РїСЂРѕР±РµР»С‹ РѕС‚РЅРѕСЃРёС‚РµР»СЊРЅРѕ С†РµР»РµРІРѕРіРѕ РїСЂРѕРґСѓРєС‚Р°:

1. `FE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РѕСЃРЅРѕРІРЅРѕР№ `Battle Chat` РєР°Рє С‚РѕС‡РєР° РїРѕСЃС‚Р°РЅРѕРІРєРё Р·Р°РґР°С‡Рё.
2. `FE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ Р±РёР±Р»РёРѕС‚РµРєР° РїР°С‚С‚РµСЂРЅРѕРІ СЃ include/exclude UX.
3. `FE` РѕС‚СЃСѓС‚СЃС‚РІСѓСЋС‚ `Dataset Studio` Рё `Metrics Studio`.
4. `FE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РїСЂРѕРґСѓРєС‚РѕРІС‹Р№ run-monitor СЃ РІРµСЂСЃРёСЏРјРё СЃСѓС‰РЅРѕСЃС‚РµР№ Рё СЌРїРѕС…Р°РјРё.
5. `FE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ РїСѓС‚СЊ native `import` (РµСЃС‚СЊ export/read-only Р°СЂС‚РµС„Р°РєС‚С‹).
6. `BE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ chat-orchestrator РґР»СЏ candidate generation.
7. `BE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ pattern library service + RAG index/query API.
8. `BE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ unified version-manifest service РґР»СЏ runs.
9. `BE` РѕС‚СЃСѓС‚СЃС‚РІСѓРµС‚ native import pipeline СЃ compatibility/preflight РїРѕ РєРѕРґСѓ.

РџСЂРёРѕСЂРёС‚РµС‚ Р·Р°РєСЂС‹С‚РёСЏ gap:

1. СЃРЅР°С‡Р°Р»Р° `Workspaces + Battle Chat + Candidate lifecycle`;
2. Р·Р°С‚РµРј `Dataset/Metrics/Optimizer setup`;
3. Р·Р°С‚РµРј `Run monitor/report/champion`;
4. Р·Р°С‚РµРј `native import` РєР°Рє Р·Р°РјС‹РєР°РЅРёРµ РїРѕСЃС‚-СЌРєСЃРїРѕСЂС‚РЅРѕРіРѕ С†РёРєР»Р°.

## Definition of Done for Frontend Slice

РЎР»Р°Р№СЃ СЃС‡РёС‚Р°РµС‚СЃСЏ Р·Р°РІРµСЂС€РµРЅРЅС‹Рј, РµСЃР»Рё:

1. backend-РєРѕРЅС‚СЂР°РєС‚ СЂРµР°Р»РёР·РѕРІР°РЅ Рё Р·Р°РґРѕРєСѓРјРµРЅС‚РёСЂРѕРІР°РЅ;
2. capability РѕС‚СЂР°Р¶РµРЅР° РІ UI c РєРѕСЂСЂРµРєС‚РЅС‹Рј СЃС‚Р°С‚СѓСЃРѕРј;
3. РґРёР·Р°Р№РЅ-СЃРёСЃС‚РµРјР° СЃРѕР±Р»СЋРґРµРЅР°;
4. С‚РµСЃС‚С‹ `unit + integration + e2e` РґРѕР±Р°РІР»РµРЅС‹;
5. demo-СЃС†РµРЅР°СЂРёР№ РѕР±РЅРѕРІР»РµРЅ Рё РІРѕСЃРїСЂРѕРёР·РІРѕРґРёРј РїРѕ README.

## Risks and Mitigations

1. Р РёСЃРє: СЂР°СЃСЃРёРЅС…СЂРѕРЅ frontend/backend РєРѕРЅС‚СЂР°РєС‚РѕРІ.
2. РњРёС‚РёРіРёСЂСѓРµРј: typed client + contract tests + ADR/spec-first.
3. Р РёСЃРє: СЂРѕСЃС‚ СЃР»РѕР¶РЅРѕСЃС‚Рё UI РїСЂРё РґРѕР±Р°РІР»РµРЅРёРё С„СѓРЅРєС†РёР№.
4. РњРёС‚РёРіРёСЂСѓРµРј: capability gating + РјРѕРґСѓР»СЊРЅС‹Рµ РіСЂР°РЅРёС†С‹ + state machine.
5. Р РёСЃРє: РґРµРіСЂР°РґР°С†РёСЏ UX РїСЂРё Р±С‹СЃС‚СЂС‹С… РёС‚РµСЂР°С†РёСЏС….
6. РњРёС‚РёРіРёСЂСѓРµРј: design-system gate Рё demo-acceptance РЅР° РєР°Р¶РґРѕРј СЃР»Р°Р№СЃРµ.

## References

1. [Roadmap.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/Roadmap.md)
2. [System_Architecture_Overview.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/System_Architecture_Overview.md)
3. [Project_Operating_Model.md](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/process/Project_Operating_Model.md)
4. [ADR-0029](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0029-vertical-product-slices-backend-frontend-demo-sync.md)
5. [ADR-0030](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/docs/adr/ADR-0030-design-system-as-mandatory-frontend-standard.md)

