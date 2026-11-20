"""
interview_coach.py
Builds the LLM prompt and calls the API to evaluate a student's interview answer.
Falls back to keyword-based offline feedback if the API is unavailable.
"""

import os
import re
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def _get_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", None)
    kwargs = {"api_key": api_key}
    if base_url and base_url.strip():
        kwargs["base_url"] = base_url.strip()
    return OpenAI(**kwargs)


def _get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


# ── Offline fallback ───────────────────────────────────────────────────────────

def _offline_feedback(question: str, strong_answer_includes: str,
                      student_answer: str) -> dict:
    """
    Rule-based feedback using keyword matching against strong_answer_includes.
    Works with no API connection.
    """
    answer_lower  = student_answer.lower()
    strong_lower  = strong_answer_includes.lower()

    # Pull key phrases from strong_answer_includes (comma/semicolon separated)
    key_phrases = [p.strip() for p in re.split(r"[,;]", strong_lower) if len(p.strip()) > 4]

    matched   = [p for p in key_phrases if any(word in answer_lower for word in p.split() if len(word) > 3)]
    unmatched = [p for p in key_phrases if p not in matched]

    # Strength: what they did cover
    if len(student_answer.split()) < 10:
        strength = "You attempted an answer — a good starting point for building your response."
    elif matched:
        covered = matched[0].strip()
        strength = f"Your answer touched on '{covered}', which is a key element of a strong response."
    else:
        strength = "You provided a response and engaged with the question directly."

    # Improve: what's missing
    if unmatched:
        missing = unmatched[0].strip()
        improve = f"Strengthen your answer by also covering '{missing}' — this is what interviewers look for here."
    elif len(student_answer.split()) < 20:
        improve = "Add more detail and a specific example from your experience to make your answer more compelling."
    else:
        improve = "Consider structuring your answer with a clear situation, action, and result to make it more memorable."

    return {"strength": strength, "improve": improve}


# ── Public entry point ─────────────────────────────────────────────────────────

def get_answer_feedback(question: str, strong_answer_includes: str,
                        student_answer: str) -> dict:
    """
    Evaluate the student's answer. Tries LLM first; falls back to offline
    keyword analysis if the API is unavailable.
    Returns {"strength": str, "improve": str}.
    """
    try:
        system = (
            "You are an experienced IT hiring manager conducting a mock interview. "
            "You give honest, constructive, and encouraging feedback. "
            "Your feedback is always specific — you reference what the candidate actually said."
        )

        user = f"""Evaluate the candidate's answer to this interview question.

Question: {question}

What a strong answer includes: {strong_answer_includes}

Candidate's answer: {student_answer}

Respond with EXACTLY two lines in this format (no other text):
Strength: [one sentence describing what the candidate did well]
Improve: [one sentence describing the single most important thing to improve or add]
"""

        client = _get_client()
        response = client.chat.completions.create(
            model=_get_model(),
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": user},
            ],
            temperature=0.5,
            max_tokens=200,
        )

        raw = response.choices[0].message.content.strip()

        strength = ""
        improve  = ""
        for line in raw.splitlines():
            if re.match(r"^Strength\s*:", line, re.IGNORECASE):
                strength = re.sub(r"^Strength\s*:\s*", "", line, flags=re.IGNORECASE).strip()
            elif re.match(r"^Improve\s*:", line, re.IGNORECASE):
                improve = re.sub(r"^Improve\s*:\s*", "", line, flags=re.IGNORECASE).strip()

        if not strength:
            strength = raw
        if not improve:
            improve = "Consider adding more specific detail to strengthen your answer."

        return {"strength": strength, "improve": improve}

    except Exception:
        # API unavailable — use offline keyword-based feedback
        return _offline_feedback(question, strong_answer_includes, student_answer)
