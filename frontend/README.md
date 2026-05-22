# Frontend Workbench (React + TypeScript)

Каталог `frontend` мигрирован на `React + TypeScript + Vite` в слайсе `V2.1.S3a`.

## Что реализовано

1. App-v3-подобный каркас интерфейса (левый nav, центральный workbench, правый intervention rail).
2. Реальный C1 поток `validate + compile` через backend endpoint `/api/c1/validate-compile`.
3. Capability-каталог со статусами `enabled/planned`.
4. Экспорт compile payload из UI в JSON.

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

## Design System

Frontend строго следует:

1. `design_system/colors_and_type.css`.
2. `design_system/ui_kits/app/*`.
3. UX North Star: `design_system/screenshots/app-v3.png`.
