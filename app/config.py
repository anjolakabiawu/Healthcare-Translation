import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-prod")
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
    MAX_AUDIO_SIZE_MB = 10
    SESSION_TYPE = "filesystem"
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", "")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False
    # "small" is markedly more accurate on medical terms than tiny/base and
    # fits comfortably in the Hugging Face Spaces free tier (16 GB RAM).
    # Override per-deploy with the WHISPER_MODEL_SIZE env var
    # (tiny | base | small | medium) — smaller = faster + less memory.
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "small")


class TestingConfig(Config):
    TESTING = True
    WHISPER_MODEL_SIZE = "tiny"
    SECRET_KEY = "test-secret"
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
