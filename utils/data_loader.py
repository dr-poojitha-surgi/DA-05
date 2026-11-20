"""
data_loader.py
Utilities to load the five seed CSVs into Python structures.
"""

import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def _csv(filename: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, filename))


def load_student_profile() -> dict:
    """Return student profile as {field: value} dict."""
    df = _csv("student_profile.csv")
    return dict(zip(df["field"], df["value"]))


def load_skills_and_certifications() -> list[dict]:
    """Return list of dicts with keys: item, type, level, evidence."""
    return _csv("skills_and_certifications.csv").fillna("").to_dict(orient="records")


def load_projects() -> list[dict]:
    """Return list of project dicts."""
    return _csv("projects.csv").fillna("").to_dict(orient="records")


def load_job_postings() -> list[dict]:
    """Return list of job posting dicts."""
    return _csv("job_postings.csv").fillna("").to_dict(orient="records")


def load_interview_questions() -> list[dict]:
    """Return list of interview question dicts."""
    return _csv("interview_questions.csv").fillna("").to_dict(orient="records")
