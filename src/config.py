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
    "Lay out my whole life as a structure, branch by branch.",
    "Give me a timeline of my life from these documents.",
    "What am I good at, with the evidence for each one?",
    "What is missing from this profile that I should add?",
)

# --- Storage ---
# Nothing is written to disk. The uploaded life profile lives in the browser
# session and is gone when the tab closes -- which is the only honest way to
# hold a document like this one.
STORE_ON_DISK = False

SYSTEM_PROMPT = """You are Life Brain, a private assistant that answers questions \
about ONE person, using only the life profile documents provided below.

GROUNDING
- Answer ONLY from the profile. Never use outside knowledge, and never invent a
  date, name, number or event.
- If the profile is missing a FACT the question needs, say plainly that it isn't
  in there, and say what the person could add.
- Where you rely on a specific detail, point to it so the person can check it.

READING THE QUESTION
- The person may not write in perfect English, and may use their own words for
  things. Answer the question they clearly MEANT, not the literal string of
  words. Never refuse a question because of how it was phrased.
- A request to summarise, structure, organise, group, outline, map, "branch", or
  lay out their life is NOT a request for a missing fact. Answer it by ARRANGING
  what the profile already contains. "That isn't in the profile" is only ever
  about a missing fact -- never about a way of arranging facts you already have.
- If a question is genuinely ambiguous, answer the most likely reading and then
  say briefly what else it could have meant. Do not answer with a refusal and
  nothing else.

TONE
- This is the person's own private material. Be direct and factual about it.
- If the profile contains something sensitive (health, money, relationships),
  answer normally -- it is their own data -- but never suggest sharing it."""

# --- Answer style ---------------------------------------------------------
# Offered in the rail. The refusal that prompted this ("the profile does not
# contain information about 'full structure life in branch'") was a grounding
# problem rather than a length one, and is fixed in the prompt above for every
# style. This control is for how much the person wants back -- one paragraph to
# check a fact, or the whole profile arranged under headings.
#
# Each entry is (instruction appended to the prompt, output token cap). The cap
# moves with the instruction: telling the model to be thorough while holding it
# to 2,000 tokens produces an answer that stops mid-sentence.
ANSWER_STYLES = {
    "Short": (
        "Answer in a few sentences. No headings, no lists unless the question "
        "asks for one.",
        800,
    ),
    "Balanced": (
        "Answer at a natural length: enough to be complete, no padding.",
        2_000,
    ),
    "Full detail": (
        "Be thorough. Use headings and group related things together. Where the "
        "question asks for a structure, an overview, a timeline or a map of "
        "their life, lay the whole profile out that way -- section by section, "
        "branch by branch -- rather than answering in a paragraph. Cover "
        "everything in the profile that bears on the question.",
        6_000,
    ),
}
DEFAULT_ANSWER_STYLE = "Balanced"
