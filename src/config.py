"""
Central configuration for Life Brain.
Reads settings from environment variables (.env file), never hardcodes secrets.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# --- LLM settings (Google Gemini) ---
# The free tier at aistudio.google.com covers this app comfortably: one
# question is one request, and the whole life profile rides along as context.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Offered in the rail so a question that deserves more thought can have it
# without editing .env. Flash first because it is what the free tier is
# generous with; pro is slower and burns the daily quota faster.
MODEL_CHOICES = {
    "gemini-2.5-flash": "Flash — fast, best for the free tier",
    "gemini-2.5-pro": "Pro — slower, better at long reasoning",
    "gemini-2.5-flash-lite": "Flash Lite — fastest, shortest answers",
}

# --- Uploads ---
# Must match `server.maxUploadSize` in .streamlit/config.toml, which is stated
# in megabytes. Streamlit enforces its own number first and refuses the file
# with a generic message of its own, so a larger figure here is not a more
# generous limit -- it is a limit the app promises and cannot keep, and the
# friendly message below would never be reached.
MAX_UPLOAD_MB = 10
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# Extensions we can pull text out of. Anything else is refused by name rather
# than being sent as bytes and coming back as noise.
TEXT_SUFFIXES = {".md", ".txt", ".markdown", ".rst", ".csv", ".json", ".log",
                 ".yaml", ".yml", ".html", ".htm"}
PDF_SUFFIXES = {".pdf"}
DOCX_SUFFIXES = {".docx"}
SUPPORTED_SUFFIXES = TEXT_SUFFIXES | PDF_SUFFIXES | DOCX_SUFFIXES

# --- Limits ---
# There is no retrieval step here: the whole profile is sent as context on
# every question. Gemini's window is large enough that this is simpler and more
# reliable than chunking -- nothing can be "missed" by a search that went wrong.
# The cap is what stops one enormous upload from making every question fail.
MAX_PROFILE_CHARS = 400_000
MAX_QUESTION_CHARS = 4_000
MAX_OUTPUT_TOKENS = 2_000

# How many past turns travel with each question, so follow-ups make sense.
HISTORY_TURNS = 8

# The opening screen has no history to show, so it shows these instead. They are
# phrased as the kind of thing a person actually wants back from their own
# documents -- not "summarise the profile", which any model will do badly.
STARTERS = (
    "Give me a timeline of my life from these documents.",
    "What am I good at, with the evidence for each one?",
    "What have I said I want to change about my life?",
    "What is missing from this profile that I should add?",
)

# --- Storage ---
# Nothing is written to disk. The uploaded life profile lives in the browser
# session and is gone when the tab closes -- which is the only honest way to
# hold a document like this one.
STORE_ON_DISK = False

SYSTEM_PROMPT = """You are Life Brain, a private assistant that answers questions \
about ONE person, using only the life profile documents provided below.

Rules:
- Answer ONLY from the profile. Do not use outside knowledge and do not guess.
- If the profile does not cover something, say plainly that it isn't in there,
  and suggest what the person could add. Never invent a date, name, number or
  event.
- Quote or point to the part of the profile you used, so the person can check it.
- This is the person's own private material. Be direct and factual about it.
- If the profile contains something sensitive (health, finances, relationships),
  answer normally -- it is their own data -- but never suggest sharing it.
- Be concise. Answer the question that was asked."""
