from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)

BASE_DIR = Path(__file__).resolve().parent
CORPUS_DIR = BASE_DIR / "corpus"
QUESTIONS_FILE = BASE_DIR / "questions.json"

TOP_K = 5
