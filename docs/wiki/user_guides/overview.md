# User Guide Overview

## Реальные скриншоты интерфейса

### Battles Hub

![Battles Hub](../assets/screenshots/real-battles-hub.png)

### Battle Workspace (C2)

![Battle Workspace C2](../assets/screenshots/real-workspace-c2.png)

### Battle Workspace (C3)

![Battle Workspace C3](../assets/screenshots/real-workspace-c3.png)

## Базовый пользовательский поток

1. Создайте или откройте battle в Battles Hub.
2. В Battle Workspace опишите задачу в чате.
3. Получите список кандидатов архитектур.
4. При необходимости выберите паттерны в C3 (галочки) и сохраните кнопкой `Save`.
5. Подготовьте тестовые кейсы в C4 Dataset Studio, отметьте нужные датасеты и сохраните их назначение на арену.
6. В C4 настройте профиль оценки (метрики, evaluators, budget) и проверьте его через `Validate profile`.
7. Выберите кандидатов для тестов в C2 (чекбоксами) и выполните `Select for tests`.
8. В C5 сохраните optimizer setup, выполните `Validate` (preflight guardrails) и нажмите `Launch`.
9. Анализируйте очередь запусков и переходите к run-monitor этапу.

## Что считается внутренним процессом

1. Валидация и компиляция кандидатов.
2. Внутренние попытки автоисправления подготовительных ошибок.

Пользователь видит только итог: кандидат готов к тесту или требуется ручное внимание.

