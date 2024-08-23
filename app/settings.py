from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """App settings."""

    app_host: str = "0.0.0.0"
    app_port: int = 8001
    app_public_url: str = "embedding-service"

    # core
    pdfs_data_dir: str = "/data/tmp/pdfs"
    pgvector_dbdir: str = "/data/pgvector/data"

    # chunker
    chunk_size: int = 1500
    chunk_overlap: int = 200
    separators: list = [
        "\n\n",
        "\n",
        "(?<=\. )",
        " ",
        "",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
    ]

    # postgres
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_db: str = "postgres"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    # dramatiq
    dramatiq_name_space: str = "embedding-dramatiq"
    dramatiq_task_time_limit_ms: int = 30 * 60000  # 30 minutes
    dramatiq_task_max_retries: int = 2
    dramatiq_task_max_age_ms: int = 3 * 60 * 60 * 1000  # 3 hour
    redis_host: str = "redis"
    redis_port: int = 6379
    dramatiq_redis_db: int = 0
    embeddings_redis_db: int = 1

    class Config(object):
        """Config for pydantic base settings."""
        env_prefix = "EMB_"


settings = Settings()
