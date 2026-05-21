# ADR-0023: Native Runtime Compatibility Preflight v0

- Status: Accepted
- Date: 2026-05-19
- Slice: I5.S2a

## Context

РџРѕСЃР»Рµ `I5.S1` РІС‹СЏСЃРЅРёР»РѕСЃСЊ, С‡С‚Рѕ `run_profile --target native_runtime` РјРѕР¶РµС‚ РїР°РґР°С‚СЊ РІ РїСЂРѕС†РµСЃСЃРµ Р·Р°РїСѓСЃРєР°,
РµСЃР»Рё СЃСЂРµРґРё participants РµСЃС‚СЊ РЅРµРїРѕРґРґРµСЂР¶Р°РЅРЅС‹Рµ node kinds (РЅР°РїСЂРёРјРµСЂ `hitl_gate`).

РџСЂРѕР±Р»РµРјР°:

1. РѕС€РёР±РєР° РІРѕР·РЅРёРєР°РµС‚ РїРѕР·РґРЅРѕ (РІ СЂР°РЅС‚Р°Р№РјРµ СЌРєСЃРїРѕСЂС‚Р°/Р·Р°РїСѓСЃРєР°),
2. РїСЂРёС‡РёРЅР° РЅРµ Р°РіСЂРµРіРёСЂСѓРµС‚СЃСЏ РїРѕ РІСЃРµРј participants,
3. РЅРµС‚ СЃС‚СЂСѓРєС‚СѓСЂРёСЂРѕРІР°РЅРЅРѕРіРѕ preflight РѕС‚С‡РµС‚Р° РґР»СЏ CI/Р°РІС‚РѕРјР°С‚РёР·Р°С†РёРё.

## Decision

РџСЂРёРЅСЏС‚Рѕ РІРІРµСЃС‚Рё РѕР±СЏР·Р°С‚РµР»СЊРЅС‹Р№ preflight РґР»СЏ `native_runtime` РІ СЂРµР¶РёРјРµ `strict_preflight_v0`:

1. РїРµСЂРµРґ native Р·Р°РїСѓСЃРєРѕРј СЃС‚СЂРѕРёС‚СЃСЏ compatibility report РїРѕ РєР°Р¶РґРѕРјСѓ participant;
2. РµСЃР»Рё РµСЃС‚СЊ РЅРµСЃРѕРІРјРµСЃС‚РёРјС‹Рµ participants, native Р·Р°РїСѓСЃРє Р±Р»РѕРєРёСЂСѓРµС‚СЃСЏ;
3. CLI РІРѕР·РІСЂР°С‰Р°РµС‚ structured error payload:
   - `error_type=native_compatibility_preflight_failed`,
   - `preflight` report СЃ РґРµС‚Р°Р»СЏРјРё incompatibility.

## Consequences

РџР»СЋСЃС‹:

1. РѕС€РёР±РєРё native target СЃС‚Р°РЅРѕРІСЏС‚СЃСЏ РїСЂРµРґСЃРєР°Р·СѓРµРјС‹РјРё Рё explainable;
2. CI РјРѕР¶РµС‚ РјР°С€РёРЅРЅРѕ С‡РёС‚Р°С‚СЊ РїСЂРёС‡РёРЅСѓ Р±Р»РѕРєРёСЂРѕРІРєРё;
3. РґРµРјРѕ РЅРµ вЂњРїР°РґР°РµС‚ РІ СЃРµСЂРµРґРёРЅРµвЂќ, Р° РґР°РµС‚ РєРѕСЂСЂРµРєС‚РЅС‹Р№ fail-fast РѕС‚С‡РµС‚.

РњРёРЅСѓСЃС‹:

1. РїРѕРєР° РёСЃРїРѕР»СЊР·СѓРµС‚СЃСЏ С‚РѕР»СЊРєРѕ strict-РїРѕРІРµРґРµРЅРёРµ (Р±РµР· С‡Р°СЃС‚РёС‡РЅРѕРіРѕ РІС‹РїРѕР»РЅРµРЅРёСЏ).

## Follow-up

Следующий шаг — не degradation policy, а устранение несовместимости:

1. `I4.S6a`: canonical DSL->native parity для stylizer профиля (включая `hitl_gate` семантику) — выполнено;
2. `I4.S6`: native tool binding layer — выполнено;
3. `I4.S7`: DSL-vs-native parity harness + CI gate — выполнено;
4. далее `I4.S8`: native-first champion bundle default switch.
