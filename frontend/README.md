# Frontend Capability Shell (V2.1.S1)

Этот каталог содержит первый вертикальный frontend shell для capability `C1..C6`.

## Что реализовано

1. Sidebar + topbar + capability-панель (C1..C6) в стиле `design_system`.
2. Состояния `idle/loading/success/error` для всех capability.
3. Реальный backend вызов для `C1` (`/api/c1/validate-compile`).
4. Stub-endpoints для `C2..C6`.

## Запуск

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

Открыть:

```text
http://127.0.0.1:4173/
```

## Design System

Frontend shell обязан использовать:

1. `design_system/colors_and_type.css` (токены).
2. `design_system/assets/*` (бренд-ассеты).
3. `design_system/ui_kits/app/*` как baseline-композиции.
4. Lucide stroke-only и sentence-case copy правила.

