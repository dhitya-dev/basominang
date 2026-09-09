import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Config:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "terjemahan")
    MODEL_TTS_INDO_PATH = Path(
        os.getenv("MODEL_TTS_INDO_PATH", BASE_DIR / "TTS_Indo")
    )
    MINANG_TTS_MODEL_PATH = Path(
        os.getenv(
            "MINANG_TTS_MODEL_PATH", BASE_DIR / "TTS_Minang" / "best_model.pth"
        )
    )
    MINANG_TTS_CONFIG_PATH = Path(
        os.getenv(
            "MINANG_TTS_CONFIG_PATH", BASE_DIR / "TTS_Minang" / "config_Agam.json"
        )
    )
    AUDIO_OUTPUT_PATH = BASE_DIR / "static" / "generated" / "output.wav"
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "1000"))
