"""Shared settings for the ingestion pipeline. Edit this file, not the modules, when tuning."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # reads .env in the project root if present

# --- paths ---
ROOT_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT_DIR / "data" / "pdfs"
CHROMA_DIR = ROOT_DIR / "data" / "chroma"
COLLECTION_NAME = "ukask_regulations"

# --- API Providers ---
HF_TOKEN = os.environ.get("HF_TOKEN")
GAPGPT_API_KEY = os.environ.get("GAPGPT_API_KEY")

# --- chunking ---
MIN_CHUNK_TOKENS = 300
MAX_CHUNK_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50  # avoids losing context at chunk edges

INCLUDE_TABLE_CHUNKS = False

# --- embedding ---
EMBEDDING_MODEL = "BAAI/bge-m3"

# --- OCR ---
OCR_LANG = "fas"
OCR_DPI = 300
# a page with fewer real characters than this is treated as a scan, not native text
NATIVE_TEXT_MIN_CHARS = 20

TESSERACT_CMD = r"D:\Tesseract-OCR\tesseract.exe"

FORCE_OCR_FILES = {
    "دستورالعمل بررسی موارد غیبت پزشکی.pdf",
}

# files with the ل+ا (lam-alef) drawing-order bug in their font, see
# pipeline/ligature_fix.py for what this actually does and why it's opt-in
LIGATURE_FIX_FILES = {
    "مجموعه مقررات آموزشی 1402.pdf",
    "راهنمای شرکت در امتحانات پایان ترم.pdf"
}

# --- per-document metadata ---
DOCUMENT_MANIFEST = {
    "ainname karshenasi phd msc 1397.pdf": {
        "title": "آیین‌نامه تمام دوره‌های تحصیلی برای دانشجویان ورودی 1397 و بعد از آن",
        "publication_date": "1397"
    },
    "shivename 1402.pdf": {
        "title": "شیوه‌نامه یکپارچه تمام دوره‌های تحصیلی برای دانشجویان ورودی 1402 و بعد از آن",
        "publication_date": "1402"
    },
    "خلاصه قوانین آموزشی.pdf": {
        "title": "خلاصه قوانین یکپارچه آموزشی ورودی‌های 1402 و بعد از آن",
        "publication_date": "1402"
    },
    "دستورالعمل بررسی موارد غیبت پزشکی.pdf": {
        "title": "دستورالعمل بررسی غیبت پزشکی در امتحانات پایان نیمسال",
        "publication_date": "1402"
    },
    "راهنمای شرکت در امتحانات پایان ترم.pdf": {
        "title": "دستورالعمل شرکت در امتحانات پایان نیمسال تحصیلی",
        "publication_date": "1402"
    },
    "مجموعه مقررات آموزشی 1402.pdf": {
        "title": "مجموعه قوانین و آیین‌نامه‌های آموزشی 1402",
        "publication_date": "1402"
    },
    "مقررات-آموزشی-ابلاغی-1402.pdf": {
        "title": "آیین‌نامه یکپارچه تمام دوره‌های تحصیلی برای دانشجویان ورودی 1402 و بعد از آن",
        "publication_date": "1402"
    },
}
