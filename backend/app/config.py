from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://voxa:voxa@localhost:5432/voxa"
    audio_dir: str = "./data/audio"

    whisper_model: str = "large-v3"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    diarizer_device: str = "cpu"

    hf_token: str = ""

    openrouter_llm_model: str = ""
    openrouter_token: str = ""

    yandex_tracker_token: str = ""
    yandex_tracker_org_id: str = ""
    yandex_tracker_cloud_org: bool = False

    model_config = {"env_prefix": "VOXA_", "env_file": ".env"}
