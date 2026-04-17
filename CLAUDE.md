# Voxa

Анализатор онлайн-встреч: транскрипция с диаризацией, суммаризация LLM, автосоздание задач в Yandex Tracker.

## Стек

- **Backend** (`backend/`): FastAPI + SQLAlchemy async, WhisperX + pyannote, pydantic-ai, dishka для DI, Alembic, PostgreSQL
- **Frontend** (`frontend/`): Vue 3 + TS, PrimeVue, Pinia, Vite
- **Инфра**: Docker Compose

Подробности и команды — в `backend/CLAUDE.md` и `frontend/CLAUDE.md`.

## Локальный запуск

```bash
cp backend/.env.example backend/.env   # прописать VOXA_HF_TOKEN и LLM-ключи
docker compose up
```

- Frontend: http://localhost:5173
- API: http://localhost:8000/api, docs: http://localhost:8000/docs

## Общие правила

- Ответы на русском; технические идентификаторы — как есть.
- Не коммитить без явной просьбы.
- Секреты (`.env`, токены HF/OpenRouter/Yandex) никогда не попадают в репозиторий.
- Поток обработки митинга: upload → transcription → diarization → merge → LLM analysis (см. `backend/app/services/processor.py`).
