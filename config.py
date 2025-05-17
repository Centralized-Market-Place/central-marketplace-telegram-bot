import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
    TEST_TELEGRAM_BOT_TOKEN: str = os.getenv("TEST_TELEGRAM_BOT_TOKEN")
    BOT_TOKEN: str = TELEGRAM_BOT_TOKEN or TEST_TELEGRAM_BOT_TOKEN

    TELEGRAM_BOT_USERNAME: str = os.getenv("TELEGRAM_BOT_USERNAME")
    TEST_TELEGRAM_BOT_USERNAME: str = os.getenv("TEST_TELEGRAM_BOT_USERNAME")
    BOT_USERNAME: str = TELEGRAM_BOT_USERNAME or TEST_TELEGRAM_BOT_USERNAME

    API_URL: str = os.getenv("API_URL", "http://localhost:8000/api/v1")

settings = Settings()