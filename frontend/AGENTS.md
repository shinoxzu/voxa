# Voxa Frontend

Vue 3 SPA для Voxa: загрузка/запись встречи, просмотр транскрипта, создание задач в трекере.

## Команды

```bash
bun install
bun run dev          # vite dev-сервер (http://localhost:5173)
bun run build        # type-check + сборка
bun run type-check   # vue-tsc
bun run lint         # eslint --fix
bun run format       # prettier
```

Пакетный менеджер — **bun**, не npm/pnpm. TypeScript strict, Vue 3 `<script setup>`.

## Архитектура

- `src/main.ts` — точка входа, регистрация PrimeVue + Pinia + router.
- `src/router.ts` — маршруты (`/`, `/meetings`, `/meetings/:id`).
- `src/App.vue` — layout с верхней навигацией.
- `src/pages/`:
  - `HomePage.vue` — загрузка файла / запись с микрофона.
  - `HistoryPage.vue` — список встреч.
  - `MeetingPage.vue` — детали: транскрипт, summary, action items, создание задач в Tracker.
- `src/services/api.ts` — обёртка над backend API.
- `src/services/recorder/` — захват аудио через MediaRecorder.
- `src/stores/` — Pinia-стора (`meetingStore`, `recorderStore`).

Backend API живёт на том же хосте под `/api` (в проде проксируется nginx, см. `nginx.conf`); для дева vite проксирует на `http://localhost:8000`.

## Конвенции

- Компоненты и страницы — PascalCase `.vue`, `<script setup lang="ts">`.
- Состояние между страницами — через Pinia-стору, а не props-пробрасывание.
- UI-компоненты берутся из PrimeVue, иконки — primeicons.
- Запросы к backend — только через `src/services/api.ts`, не `fetch` россыпью по компонентам.
- Типы DTO держим синхронно с `backend/app/dto.py` — при изменении бэка обновлять тут.

## Запуск вместе с бэком

Бэк должен быть поднят (`docker compose up` или `uv run uvicorn ...`), иначе api-запросы упадут.
