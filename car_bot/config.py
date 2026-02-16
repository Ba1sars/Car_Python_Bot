import os

from dotenv import load_dotenv
from pathlib import Path
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

BASE_DIR = Path(__file__).resolve().parent

LINK_CHECKER = os.getenv("LINK_CHECKER")
BOT_API = os.getenv("BOT_API")
DB_NAME = os.getenv("DB_NAME")
EXCEL_TABLE_NAME = os.getenv("EXCEL_TABLE_NAME")
PROKLADKA_USERNAME = os.getenv("PROKLADKA_USERNAME")
MONJARO_VIDEO_PATH = BASE_DIR / "models" / "Установка.mp4"
MONJARO_DOC_PATH = BASE_DIR / "models" / "Руководство SkyCam.pdf"
WHATSAPP_LINK = os.getenv("WHATSAPP_LINK")
WHATSAPP_TEL = os.getenv("WHATSAPP_TEL")
TELEGRAMM_TAG = os.getenv("TELEGRAMM_TAG")
TEL_NUMBER = os.getenv("TEL_NUMBER")
EMAIL = os.getenv("EMAIL")
WEB_SITE_LINK = os.getenv("WEB_SITE_LINK")
WEB_SITE_NAME = os.getenv("WEB_SITE_NAME")
