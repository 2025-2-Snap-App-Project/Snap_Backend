from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    google_api_key: str
    google_application_credentials: str
    debug: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
