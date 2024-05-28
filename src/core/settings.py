from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """
    API_ID: int
    API_HASH: str
    SESSION_DIRECTORY: str = "./sessions"

    MIN_AVAILABLE_ENERGY: int = 250
    SEND_TAPS_COOLDOWN: list[int] = [15, 25]
    SEND_TAPS_WAIT: list[int] = [30, 60]
    SEND_TAPS_COUNT: list[int] = [150, 250]

    MAX_LEVEL_BOOST: int = 5
    APPLY_DAILY_ENERGY: bool = True
    AUTO_UPGRADE: bool = False
    MAX_LEVEL_UPGRADE: int = 15

    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


settings = Settings()
