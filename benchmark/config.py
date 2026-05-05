import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

MODEL = "gemini-3.1-flash-lite-preview"
# LiteLLM format for CrewAI
CREWAI_MODEL = f"gemini/{MODEL}"

# Normalise API key: both env names accepted
_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
os.environ["GOOGLE_API_KEY"] = _key
os.environ["GEMINI_API_KEY"] = _key
GOOGLE_API_KEY = _key

PROJECT_ROOT = Path(__file__).parent.parent
OAUTH_CREDS_PATH = str(PROJECT_ROOT / "oauth_gmail.json")

# Shared token: first we try delfhos cache, then write here on first OAuth run
BENCHMARK_TOKEN_PATH = str(PROJECT_ROOT / "benchmark" / "gmail_token.json")
DELFHOS_TOKEN_PATH = str(Path.home() / ".config" / "oauth_gmail.json")

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

NUM_RUNS = 3  # Runs per task per library

# Cost per 1M tokens (from delfhos pricing.json)
COST_INPUT_PER_M = 0.10
COST_OUTPUT_PER_M = 0.40
