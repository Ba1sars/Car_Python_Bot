import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

LINK_CHECKER = os.getenv('LINK_CHECKER')
BOT_API = os.getenv('BOT_API')
DB_NAME = os.getenv('DB_NAME')
EXCEL_TABLE_NAME = os.getenv('EXCEL_TABLE_NAME')
