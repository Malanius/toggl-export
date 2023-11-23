import os

from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL = os.getenv("LOG_LEVEL") or "INFO"
PROJECT_SEPARATOR = os.getenv("PROJECT_SEPARATOR") or " | "
TOKEN = os.getenv("API_TOKEN") or ""
WORKSPACE_ID = os.getenv("WORKSPACE_ID")
