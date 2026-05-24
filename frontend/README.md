# Frontend Workbench (React + TypeScript)

Каталог `frontend` мигрирован на `React + TypeScript + Vite` в слайсе `V2.1.S3a`.

## Что реализовано

1. App-v3-подобный каркас интерфейса (левый nav, центральный workbench, правый intervention rail).
2. Реальный C1 поток `Workspace & Projects` через backend endpoints:
   - `GET/POST /api/workspaces`
   - `GET/POST /api/workspaces/{workspace_id}/projects`
   - `GET /api/projects/{project_id}`
3. Capability-каталог со статусами `enabled/planned`.
4. Экспорт C1 snapshot payload из UI в JSON.

## Локальная разработка фронтенда

Установка зависимостей:

```powershell
cd .\frontend
npm install
```

Запуск Vite dev server:

```powershell
npm run dev
```

Открыть:

```text
http://127.0.0.1:5173/
```

Важно для раздельного запуска:

1. Vite dev server (`5173`) проксирует `/api/*` на Python backend `http://127.0.0.1:4173`.
2. Vite также проксирует `/design_system/*` на Python backend, чтобы фронт видел токены и ассеты дизайн-системы.
3. Прокси настроен в [vite.config.ts](/c:/Users/solovev.v/Documents/ALT_PRJs/AutoAgent%20Optimizer/frontend/vite.config.ts).

### Раздельный запуск (2 терминала)

Терминал 1 (backend):

```powershell
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

Терминал 2 (frontend):

```powershell
cd .\frontend
npm run dev
```

Открыть фронт:

```text
http://127.0.0.1:5173/
```

## Сборка для Python dev server

Собрать фронтенд:

```powershell
cd .\frontend
npm run build
```

Собранные файлы появятся в `frontend/dist`.

После сборки запуск общего демо-пути:

```powershell
cd ..
python -m optimizer.frontend.dev_server --host 127.0.0.1 --port 4173
```

Открыть:

```text
http://127.0.0.1:4173/
```

## Frontend тесты

Для раннего обнаружения UI-регрессий (пропавшие кандидаты, сломанный фокус, проблемы сворачивания JSON-панели) добавлены компонентные тесты на `Vitest + React Testing Library`.

Запуск всех frontend unit/component тестов:

```powershell
cd .\frontend
npm run test
```

Запуск в watch-режиме:

```powershell
cd .\frontend
npm run test:watch
```

Текущий тест-кейс `src/__tests__/app.workspace.test.tsx` проверяет:

1. Рендер и интерактив кандидатов в battle workspace.
2. Сворачивание/разворачивание блока `Runtime snapshot` (JSON) без потери списка кандидатов.

## Design System

Frontend строго следует:

1. `design_system/colors_and_type.css`.
2. `design_system/ui_kits/app/*`.
3. UX North Star: `design_system/screenshots/app-v3.png`.
