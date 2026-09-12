import os

from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
CALLE_API_KEY = os.environ.get("CALLE_API_KEY", "")
MOCK = os.environ.get("SUPPORT_MOCK", "0") == "1"

TEXT_MODEL = "gemini-flash-latest"
