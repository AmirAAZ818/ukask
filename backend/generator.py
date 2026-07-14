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

# system prompt, added a conciseness instruction (this is the real fix)
_SYSTEM_PROMPT = f"""شما دستیار پاسخ‌گویی به سؤالات دانشگاهی بر اساس آیین‌نامه‌ها هستید.
فقط بر اساس متن‌های ارائه‌شده در بخش «اسناد» پاسخ بده، اما میتوانی تنها کمی درونیابی برای بالابردن کیفیت و عقلانی بودنش انجام بدی.
پاسخ را با طول متوسط بنویس، نه خیلی مختصر و نه خیلی توضیحی، معمولاً یک تا شش جمله کافی است، مگر در صورتی که در سوال، کاربر درخواست توضیح کامل بکند و یا مگر اینکه سؤال واقعاً نیاز به توضیح بیشتر داشته باشد.
در پاسخ به شماره ماده و صفحه سند مرتبط اشاره کن، بدون مقدمه یا توضیح اضافی.
اگر پاسخ سؤال در اسناد ارائه‌شده وجود ندارد، دقیقاً همین جمله را برگردان و چیز دیگری ننویس:
"{NOT_FOUND_MESSAGE}"
اگر مشکلات نوشتاری در متن دیدی حتما نباید تماما جمله را به همون شکل برگردانی میتوانی خودت هم ویرایش و درونیابی بکنی.
"""

# _SYSTEM_PROMPT = f"""شما دستیار پاسخ‌گویی به سؤالات دانشگاهی بر اساس آیین‌نامه‌ها هستید.
# فقط بر اساس متن‌های ارائه‌شده در بخش «اسناد» پاسخ بده، از دانش خودت استفاده نکن.
# در پاسخ به شماره ماده و صفحه سند مرتبط اشاره کن.
# اگر پاسخ سؤال در اسناد ارائه‌شده وجود ندارد، دقیقاً همین جمله را برگردان و چیز دیگری ننویس:
# "{NOT_FOUND_MESSAGE}"
# """


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
    choice = response.choices[0]
    if choice.finish_reason == "length":
        print(f"    warning, answer got cut off at max_tokens={max_tokens}, consider raising it")
    return choice.message.content