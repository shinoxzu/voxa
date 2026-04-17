# Voxa

Приложение для автоматического анализа онлайн-встреч: транскрипция с разделением спикеров, суммаризация и создание задач в трекере.

## Стек

- **Frontend**: Vue 3, TypeScript, PrimeVue, Pinia
- **Backend**: FastAPI, SQLAlchemy, WhisperX, pyannote, pydantic-ai
- **Инфра**: PostgreSQL, Docker

## Запуск

```bash
cp backend/.env.example backend/.env
# заполнить backend/.env (HF_TOKEN, LLM_MODEL, ...)

docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- Swagger: http://localhost:8000/docs

## Разработка

Frontend:
```bash
cd frontend
bun install
bun run dev
```

Backend:
```bash
cd backend
uv sync
docker compose up db   # поднять только PostgreSQL
uv run uvicorn app.main:app --reload
```

## Структура

```
voxa/
├── frontend/    — Vue 3 SPA
├── backend/     — FastAPI API
└── docker-compose.yaml
```
