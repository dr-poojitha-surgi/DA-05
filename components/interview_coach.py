"""
interview_coach.py
Builds the LLM prompt and calls the API to evaluate a student's interview answer.
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
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _get_model() -> str:
    return os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_answer_feedback(question: str, strong_answer_includes: str,
                        student_answer: str) -> dict:
    """
    Evaluate the student's answer and return:
        {"strength": str, "improve": str}
    Both values are single sentences.
    """
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
    improve = ""
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
