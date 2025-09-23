from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "task-scheduler"
    environment: str = "dev"

    # Database
    postgres_host: str = "db"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "tasks"

    # Redis / Broker
    redis_host: str = "redis"
    redis_port: int = 6379

    # Celery
    celery_result_backend_db: int = 1
    celery_task_default_queue: str = "tasks"

    # Scheduling
    recurrence_scan_interval_seconds: int = 10  # Reduced to 10 seconds for better demo responsiveness

    # Logging and Monitoring
    log_level: str = "INFO"
    structured_logging: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"

    @property
    def celery_result_backend(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.celery_result_backend_db}"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
