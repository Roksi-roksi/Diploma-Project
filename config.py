import os
from dotenv import load_dotenv

load_dotenv()

API_URL: str = os.getenv("API_URL", "https://ru.yougile.com/api-v2")
BASE_URL: str = os.getenv("BASE_URL", "https://yougile.com")

LOGIN: str = os.getenv("LOGIN", "")
PASSWORD: str = os.getenv("PASSWORD", "")
COMPANY_ID: str = os.getenv("COMPANY_ID", "")

TOKEN: str = os.getenv("TOKEN", "")
USER_TOKEN: str = os.getenv("TOKEN", "")


