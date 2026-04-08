from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 1
    MAIL_FROM: str = ""
    MAIL_PASSWORD: str = ""
    DATABASE_URL: str = "sqlite:///./patrimoine.db"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: set = {"jpg", "jpeg", "png", "gif", "webp"}

    model_config = {"env_file": ".env"}

settings = Settings()