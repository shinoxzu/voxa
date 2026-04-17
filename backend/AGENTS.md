# Voxa Backend

FastAPI-сервис обработки аудиозаписей встреч.

## Команды

```bash
uv sync                                          # установка
uv run uvicorn app.main:app --reload             # dev-сервер (db поднять отдельно: docker compose up db)
uv run alembic revision --autogenerate -m "..."  # новая миграция
uv run alembic upgrade head                      # применить миграции
uv run ruff check . && uv run ruff format .      # линт/формат
uv run ty check                                  # тайпчек
```

Зависимости через **uv**, не pip. Python 3.10–3.12.

## Архитектура

- `app/main.py` — сборка FastAPI + dishka-контейнера, CORS, подключение роутеров.
- `app/config.py` — `Settings` через pydantic-settings, префикс env `VOXA_`.
- `app/dependencies.py` — провайдеры dishka (`AppProvider` — синглтоны, `RequestProvider` — per-request). Все сервисы инжектятся отсюда; новые регистрировать тут.
- `app/models.py` — SQLAlchemy ORM-модели (Meeting, MeetingStatus).
- `app/dto.py` — pydantic-модели для API.
- `app/routes/` — HTTP-эндпоинты.
- `app/services/`:
  - `transcriber.py` — WhisperX (ASR). Абстракция `Transcriber`, реализация `WhisperXTranscriber`.
  - `diarizer.py` — pyannote через whisperx. Абстракция `Diarizer`.
  - `analyzer.py` — pydantic-ai поверх OpenRouter, достаёт summary + action items.
  - `tracker.py` — Yandex Tracker client.
  - `processor.py` — оркестратор пайплайна: `transcription → diarization → merge → analysis`. Запускается фоново после upload.

Пайплайн синхронных ML-вызовов оборачивается `asyncio.to_thread` — не блокировать event loop.

## Конвенции

- Каждый сервис = абстрактный класс + конкретная реализация. Это нужно для DI и подмены реализаций.
- Ошибки в `processor.py` ловятся в `_run`, пишутся в `meeting.error_message`, статус → `error`.
- Новые переменные окружения → в `Settings` + `.env.example`.
- Аудио кладётся в `settings.audio_dir` (по умолчанию `./data/audio`), путь сохраняется в `Meeting.audio_path`.
- Миграции обязательны при изменении `models.py`.

## Внешние сервисы

- **Hugging Face** — нужен `VOXA_HF_TOKEN` и принятые user-conditions на `pyannote/speaker-diarization-3.1` + `pyannote/segmentation-3.0`, иначе диаризация молча ломается.
- **OpenRouter** — `VOXA_OPENROUTER_TOKEN`, модель в `VOXA_OPENROUTER_LLM_MODEL`.
- **Yandex Tracker** — OAuth-токен + org id (cloud или обычная организация — флаг `yandex_tracker_cloud_org`).
