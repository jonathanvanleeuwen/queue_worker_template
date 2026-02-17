import base64
import json
from functools import lru_cache

from lib_auth.utils.auth_utils import hash_api_key
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    app_name: str = "{{cookiecutter.project_name}}"
    description: str = "{{cookiecutter.app_description}}"

    # Logger settings
    log_level_console: str = "INFO"
    log_level_file: str = "DEBUG"

    cors_allow_origins: tuple = ("http://localhost:3000", "http://127.0.0.1:3000", "*")

    # API Keys (base64 encoded JSON: {"key": {"username": "name", "roles": ["admin", "user"]}})
    api_keys: dict[str, dict] | str = (
        "eyJ0ZXN0Ijp7InVzZXJuYW1lIjoiSm9uYXRoYW4iLCJyb2xlcyI6WyJhZG1pbiIsInVzZXIiXX0sInRlc3QyIjp7InVzZXJuYW1lIjoiYm9iIiwicm9sZXMiOlsidXNlciJdfX0="
    )

    # OAuth settings
    oauth_provider: str = "github"
    oauth_secret_key: str = "your-secret-key-min-32-chars-change-in-production"
    oauth_client_id: str = ""
    oauth_client_secret: str = ""
    oauth_access_token_expire_minutes: int = 1440  # 1 day

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str | None = None

    # Queue worker settings
    worker_count: int = 2
    result_ttl: int = 3600  # Time to live for job results in seconds (1 hour)
    default_queue: str = "default"
    queue_names: str = "default,high,low"  # Comma-separated list
    job_timeout: int = 600  # Default job timeout in seconds (10 minutes)

    @model_validator(mode="after")
    def process_api_keys(self) -> "Settings":
        if isinstance(self.api_keys, str):
            decoded = base64.b64decode(self.api_keys).decode()
            self.api_keys = json.loads(decoded)

        api_key_list = list(self.api_keys.keys())
        if len(api_key_list) != len(set(api_key_list)):
            raise ValueError("All Keys in 'api_keys' must be unique")

        hashed_keys = {}
        for key, value in self.api_keys.items():
            hashed_key = hash_api_key(key)
            hashed_keys[hashed_key] = value

        self.api_keys = hashed_keys
        return self

    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_queue_list(self) -> list[str]:
        """Get list of queue names."""
        return [q.strip() for q in self.queue_names.split(",") if q.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
