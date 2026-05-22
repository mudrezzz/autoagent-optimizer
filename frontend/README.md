# Frontend Capability Workbench (V2.1.S2)

Этот каталог содержит вертикальный frontend-слайс `V2.1.S2` с каркасом `app-v3` и реальным C1-потоком.

## Что реализовано

1. App-v3-подобный layout: левый workspace/capability nav, центральный workbench, правый intervention rail.
2. Реальный C1 backend flow: `POST /api/c1/validate-compile` с отображением compile summary, issues и полного payload.
3. Capability-модель статусов: `c1=enabled`, `c2..c6=planned` через `/api/capabilities`.
4. Export compile payload из UI в JSON для ручного анализа.
5. Smoke/e2e-совместимый сценарий запуска.

## Запуск

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

Открыть:

```text
http://127.0.0.1:4173/
```

## Что проверять в демо

1. В sidebar видно C1 как `live`, остальные capability как `planned`.
2. В форме C1 есть путь к DSL, кнопка `Validate + compile` активна только для C1.
3. После запуска обновляются KPI: validation, nodes, edges, issues.
4. В блоке `Compile report` появляются summary, issues и JSON payload.
5. В правом rail обновляются bottleneck и intervention hints.

## Design System

Workbench обязан использовать:

1. `design_system/colors_and_type.css` (tokens).
2. `design_system/assets/*` (бренд-ассеты).
3. `design_system/ui_kits/app/*` как baseline-композицию.
4. North Star референс: `design_system/screenshots/app-v3.png`.
