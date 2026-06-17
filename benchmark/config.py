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

NUM_RUNS = 3  # Runs per task per library

# Cost per 1M tokens (from delfhos pricing.json)
COST_INPUT_PER_M = 0.10
COST_OUTPUT_PER_M = 0.40
