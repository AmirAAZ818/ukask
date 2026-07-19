"""Judges whether the system's actual generated answer matches the ground
truth, independent of which article got cited. A 'missed' article doesn't necessarily mean a wrong
answer.
"""

from openai import OpenAI

from pipeline import config

GAPGPT_BASE_URL = "https://api.gapgpt.app/v1"
JUDGE_MODEL = "gpt-4o"

_JUDGE_SYSTEM_PROMPT = """شما ارزیاب بی‌طرف پاسخ‌های یک سیستم پرسش و پاسخ دانشگاهی هستید.
پاسخ سیستم را با پاسخ صحیح مقایسه کن، مهم فقط محتوای واقعی است، نه عبارت‌بندی و نه اینکه کدام ماده ذکر شده باشد.
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


def evaluate_answers(questions, k=5):
    """Runs the full pipeline (retrieval + generation) and judges each answer.
    Also reports whether the labeled article number was actually retrieved,
    so you can see directly how often a 'missed' article still gave a
    correct answer, and how often a correct article still gave a bad one."""
    from backend import rag

    from . import retrieval_metrics as rm

    rows = []
    for item in questions:
        result = rag.answer_question(item["question"], k=k)
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
            "k": k,  # recorded per row, same pattern as evaluate_retrieval, so save_results can auto-detect it
            "relevance_threshold": rag.RELEVANCE_THRESHOLD,  # read live, reflects whatever this run actually used
        })
    return rows