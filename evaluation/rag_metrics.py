"""Judges whether the system's actual generated answer matches the ground
truth, independent of which article got cited. A 'missed' article doesn't necessarily mean a wrong
answer.
"""

from openai import OpenAI

from pipeline import config

GAPGPT_BASE_URL = "https://api.gapgpt.app/v1"
JUDGE_MODEL = "gpt-4o"

_JUDGE_SYSTEM_PROMPT = """شما ارزیاب بی‌طرف پاسخ‌های یک سیستم پرسش و پاسخ دانشگاهی هستید.
پاسخ سیستم را با پاسخ صحیح مقایسه کن، مهم فقط محتوای واقعی است، نه عبارت‌بندی، نه طول پاسخ، و نه اینکه کدام ماده ذکر شده باشد.

مهم: اگر پاسخ سیستم نکته اصلیِ پاسخ صحیح را دقیق بیان کرده باشد، وجود جزئیات یا مواد قانونی اضافیِ درست و بدون تناقض را نقطه‌ضعف حساب نکن. طولانی بودن یا کامل‌تر بودن پاسخ، به‌تنهایی دلیلی برای PARTIAL نیست.

CORRECT: نکته اصلی پاسخ صحیح در پاسخ سیستم آمده، حتی اگر جزئیات درست دیگری هم اضافه شده باشد.
PARTIAL: نکته اصلی پاسخ صحیح ناقص است، فقط بخشی از آن آمده، یا در میان جزئیات دیگر گم و غیرقابل‌تشخیص شده است.
INCORRECT: پاسخ با پاسخ صحیح در تناقض است یا نکته اصلی را اشتباه بیان می‌کند.

خط اول را دقیقاً یکی از این سه کلمه بنویس: CORRECT یا PARTIAL یا INCORRECT
خط دوم را با دلیل، در حداکثر یک جمله کوتاه، بنویس.
"""


def judge_answer(question, ground_truth, generated_answer, model=JUDGE_MODEL, max_tokens=100):
    client = OpenAI(api_key=config.GAPGPT_API_KEY, base_url=GAPGPT_BASE_URL)
    user_message = (
        f"سؤال: {question}\n"
        f"پاسخ صحیح: {ground_truth}\n"
        f"پاسخ سیستم: {generated_answer}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
    )

    text = response.choices[0].message.content.strip()
    first_line, _, rest = text.partition("\n")
    first_line = first_line.upper()

    if "INCORRECT" in first_line:
        verdict = "incorrect"
    elif "PARTIAL" in first_line:
        verdict = "partial"
    elif "CORRECT" in first_line:
        verdict = "correct"
    else:
        verdict = "unparseable"

    return {"verdict": verdict, "reasoning": rest.strip(), "raw": text}


def evaluate_answers(questions, k=5, search_fn=None, save_path=None):
    """Runs the full pipeline (retrieval + generation) and judges each answer.
    Also reports whether the labeled article number was actually retrieved, so
    a 'missed' article that still got a correct answer (or vice versa) is visible.

    search_fn: same as evaluate_retrieval, defaults to dense.
    save_path: if given, saves after every question (not just at the end) so a
    mid-run failure doesn't lose rows that already cost real API calls."""
    from backend import rag

    from . import results as eval_results
    from . import retrieval_metrics as rm

    rows = []
    for i, item in enumerate(questions, start=1):
        try:
            result = rag.answer_question(item["question"], k=k, search_fn=search_fn)
            target = rm.parse_article_number(item["source"])

            retrieved_articles = set()
            for s in result["sources"]:
                arts = s.get("article_numbers", "")
                if arts and arts != "unknown":
                    retrieved_articles.update(arts.split(","))
            article_hit = (target in retrieved_articles) if target else None

            judged = judge_answer(item["question"], item["ground_truth"], result["answer"])

            rows.append({
                "id": item["id"],
                "question": item["question"],
                "ground_truth": item["ground_truth"],
                "generated_answer": result["answer"],
                "question_type": item["question_type"],
                "difficulty": item.get("difficulty"),
                "target_article": target,
                "article_hit": article_hit,
                "was_refused": len(result["sources"]) == 0,
                "verdict": judged["verdict"],
                "reasoning": judged["reasoning"],
                "k": k,
                "relevance_threshold": rag.RELEVANCE_THRESHOLD,
            })
            print(f"    {i}/{len(questions)} done (id={item['id']}, verdict={judged['verdict']})")

            if save_path:
                eval_results.save_results(rows, save_path, label="in_progress")

        except Exception as e:
            print(f"    STOPPED at {i}/{len(questions)} (id={item['id']}), {len(rows)} row(s) preserved")
            print(f"    error: {e}")
            break

    return rows