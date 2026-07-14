"""Calls the generation model with the retrieved chunks and the user's
question, grounded strictly in what was retrieved, refusing per the brief's
required wording when nothing relevant was found."""

from huggingface_hub import InferenceClient
from openai import OpenAI

from pipeline import config

NOT_FOUND_MESSAGE = "پاسخ این سؤال در اسناد موجود یافت نشد."

GAPGPT_BASE_URL = "https://api.gapgpt.app/v1"
GENERATION_MODEL = "gapgpt-qwen-3.6"
# GENERATION_MODEL = "Qwen/Qwen2.5-7B-Instruct"


_SYSTEM_PROMPT = f"""شما دستیار پاسخ‌گویی به سؤالات دانشگاهی بر اساس آیین‌نامه‌ها هستید.
فقط بر اساس متن‌های ارائه‌شده در بخش «اسناد» پاسخ بده، از دانش خودت استفاده نکن.
در پاسخ به شماره ماده و صفحه سند مرتبط اشاره کن.
اگر پاسخ سؤال در اسناد ارائه‌شده وجود ندارد، دقیقاً همین جمله را برگردان و چیز دیگری ننویس:
"{NOT_FOUND_MESSAGE}"
اگر می توانی برداشت خودت را از متون بنویس حتما نباید تماما جمله را برگردانی میتوانی خودت هم ویرایش و درونیابی بکنی.
"""


def _format_context(chunks):
    parts = []
    for i, c in enumerate(chunks, start=1):
        meta = c["metadata"]
        articles = meta.get("article_numbers", "")
        tag = f"ماده {articles}" if articles and articles != "unknown" else ""
        parts.append(f"[سند {i} | صفحه {meta.get('page')} {tag}]\n{c['text']}")
    return "\n\n".join(parts)


def generate_answer(query, chunks, max_tokens=500):
    client = OpenAI(api_key=config.GAPGPT_API_KEY, base_url=GAPGPT_BASE_URL)
    
    user_message = f"اسناد:\n{_format_context(chunks)}\n\nسؤال: {query}"

    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        model=GENERATION_MODEL,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content