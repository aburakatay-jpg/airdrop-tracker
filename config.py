import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

MIN_AIRDROP_SCORE = int(
    os.getenv("MIN_AIRDROP_SCORE", "45")
)

MIN_FREE_SCORE = int(
    os.getenv("MIN_FREE_SCORE", "80")
)

MAX_CANDIDATES_PER_RUN = int(
    os.getenv("MAX_CANDIDATES_PER_RUN", "60")
)

DATA_DIR = "data"
DOCS_DIR = "docs"

SEEN_FILE = f"{DATA_DIR}/seen.json"
STATE_FILE = f"{DATA_DIR}/projects.json"
WEB_FILE = f"{DOCS_DIR}/airdrops.json"
