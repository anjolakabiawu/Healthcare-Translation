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
    # Default to the lightest Whisper model in prod to keep hosting RAM/cost
    # down. Override per-deploy by setting the WHISPER_MODEL_SIZE env var.
    WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "tiny")


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
