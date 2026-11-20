"""
resume_generator.py
Builds the LLM prompt and calls the API to generate a tailored resume.
"""

import os
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


def build_resume_prompt(student: dict, skills: list, certifications: list,
                        projects: list, job_posting: dict) -> tuple[str, str]:
    """Return (system_message, user_message) for the resume generation call."""

    system = (
        "You are a senior technical recruiter and career coach with 15+ years of experience "
        "placing candidates in IT, networking, and technology support roles. "
        "You are an expert at crafting concise, impactful resumes that pass applicant tracking "
        "systems and impress hiring managers. You write in clear, action-verb-led language, "
        "tailor every bullet point to the specific job posting, and present each candidate's "
        "academic and project experience as professional-grade work. "
        "Output ONLY the resume content in clean Markdown — no preamble, no commentary."
    )

    skills_block = "\n".join(
        f"  - {s['item']} (Level: {s['level']})" for s in skills
    )
    certs_block = "\n".join(
        f"  - {c['item']}: {c['level']}" for c in certifications
    )
    projects_block = "\n".join(
        f"  - **{p['title']}** | Role: {p['my_role']} | Tools: {p['tools']} | Result: {p['result']}"
        for p in projects
    )

    job_block = (
        f"Title: {job_posting.get('title', '')}\n"
        f"Employer: {job_posting.get('employer', '')}\n"
        f"Location: {job_posting.get('location', '')}\n"
        f"Type: {job_posting.get('type', '')}\n"
        f"Duties: {job_posting.get('duties', '')}\n"
        f"Required: {job_posting.get('required', '')}\n"
        f"Preferred: {job_posting.get('preferred', '')}"
    )

    user = f"""Create a one-page professional resume for this candidate tailored to the job posting below.

=== CANDIDATE DATA ===
Name: {student.get('name', '')}
Program: {student.get('program', '')}
Expected Graduation: {student.get('expected_graduation', '')}
GPA: {student.get('gpa', '')}
Location: {student.get('location', '')}
Work Experience: {student.get('work_experience', '')}
Career Goal: {student.get('goal', '')}

Skills:
{skills_block}

Certifications:
{certs_block}

Projects:
{projects_block}

=== TARGET JOB POSTING ===
{job_block}

=== INSTRUCTIONS ===
- Use the exact keywords and phrases from the job's Required and Preferred sections.
- Structure the resume with these sections IN THIS ORDER:
  # [Full Name]
  [City, State] | [email placeholder] | [phone placeholder] | LinkedIn: linkedin.com/in/[slug]
  ## Objective
  ## Education
  ## Certifications
  ## Technical Skills
  ## Projects
  ## Work Experience
- Lead every bullet with a strong action verb.
- Quantify achievements where the data supports it.
- Keep it to one page worth of content.
- Do NOT invent facts; only use what is in the candidate data.
- Output clean Markdown only.
"""

    return system, user


def generate_resume(student: dict, skills: list, certifications: list,
                    projects: list, job_posting: dict) -> str:
    """Call the LLM and return the generated resume as a Markdown string."""
    system, user = build_resume_prompt(student, skills, certifications, projects, job_posting)
    client = _get_client()
    response = client.chat.completions.create(
        model=_get_model(),
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=0.4,
        max_tokens=1200,
    )
    return response.choices[0].message.content.strip()
