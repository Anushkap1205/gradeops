from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
UPLOADS_DIR = BACKEND_ROOT / "uploads"
OUTPUTS_DIR = BACKEND_ROOT / "outputs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str  # env: DATABASE_URL
    pipeline_module: str = "ml_pipeline"

    @property
    def uploads_dir(self) -> Path:
        return UPLOADS_DIR

    @property
    def outputs_dir(self) -> Path:
        return OUTPUTS_DIR


settings = Settings()
