import re
from difflib import SequenceMatcher


def _clean_text(value):
    return re.sub(r"\s+", "", (value or "").strip().lower())


def _char_coverage(answer, reference):
    chars = set(reference)
    chars.discard(" ")
    if not chars:
        return 0
    return len(chars.intersection(set(answer))) / len(chars)


def score_subjective_answer(answer, question):
    """Local heuristic scorer for subjective answers.

    It behaves like a lightweight AI scorer without requiring network access:
    compare the answer with the question's template and analysis, then map the
    similarity to the configured question score.
    """
    max_score = int(getattr(question, "score", 0) or 0)
    if max_score <= 0:
        return 0

    cleaned_answer = _clean_text(answer)
    if not cleaned_answer:
        return 0

    reference = _clean_text(
        "{}{}".format(
            getattr(question, "answer_template", "") or "",
            getattr(question, "analysis", "") or "",
        )
    )
    if not reference:
        reference = _clean_text(getattr(question, "question", "") or "")

    if not reference:
        length_score = min(len(cleaned_answer) / 120, 1)
        return int(round(max_score * length_score))

    similarity = SequenceMatcher(None, cleaned_answer, reference).ratio()
    coverage = _char_coverage(cleaned_answer, reference)
    length_balance = min(len(cleaned_answer) / max(len(reference), 1), 1)
    weighted = similarity * 0.55 + coverage * 0.35 + length_balance * 0.10

    return max(0, min(max_score, int(round(max_score * weighted))))


def suggest_subjective_score(answer, question):
    score = score_subjective_answer(answer, question)
    max_score = int(getattr(question, "score", 0) or 0)
    lower = max(0, score - max(1, round(max_score * 0.15)))
    upper = min(max_score, score + max(1, round(max_score * 0.15)))

    if not (answer or "").strip():
        reason = "学生未作答，建议给 0 分。"
    else:
        reason = "系统根据答案与参考模板、解析中的关键词覆盖率和文本相似度生成建议区间，最终得分仍由教师确认。"

    return {
        "score_min": lower,
        "score_max": upper,
        "reason": reason,
    }
