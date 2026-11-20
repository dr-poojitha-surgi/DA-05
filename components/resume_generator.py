"""
resume_generator.py
Builds the LLM prompt and calls the API to generate a tailored resume.
Falls back to an offline template-based resume if the API is unavailable.
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

def _pick_objective(student: dict, job: dict) -> str:
    """Craft a one-sentence objective tailored to the job title."""
    name  = student.get("name", "The candidate")
    goal  = student.get("goal", "an entry-level IT role")
    title = job.get("title", "IT professional")
    prog  = student.get("program", "Information Technology")
    grad  = student.get("expected_graduation", "")
    grad_note = f", graduating {grad}" if grad else ""
    return (
        f"{prog} student{grad_note} seeking a **{title}** position. "
        f"Brings hands-on project experience, strong customer service skills, "
        f"and a commitment to {goal.lower().rstrip('.')}."
    )


def _action_verb(role_text: str) -> str:
    """Return a strong action verb appropriate for the role description."""
    text = role_text.lower()
    if any(w in text for w in ["configure", "set up", "install", "deploy"]):
        return "Configured"
    if any(w in text for w in ["wrote", "write", "document", "guide"]):
        return "Authored"
    if any(w in text for w in ["sort", "analyz", "pivot", "data"]):
        return "Analyzed"
    if any(w in text for w in ["support", "help", "assist"]):
        return "Supported"
    if any(w in text for w in ["lead", "manage", "coordin"]):
        return "Led"
    return "Delivered"


def _build_offline_resume(student: dict, skills: list, certifications: list,
                           projects: list, job: dict) -> str:
    """
    Assemble a professional, ATS-friendly resume in Markdown using only
    the supplied student data and job posting — no API required.
    """
    name     = student.get("name", "Candidate")
    location = student.get("location", "")
    program  = student.get("program", "")
    grad     = student.get("expected_graduation", "")
    gpa      = student.get("gpa", "")
    work_exp = student.get("work_experience", "")
    job_title   = job.get("title", "IT Role")
    employer    = job.get("employer", "")
    job_loc     = job.get("location", "")
    job_type    = job.get("type", "")
    required    = job.get("required", "")
    preferred   = job.get("preferred", "")

    # Slug for LinkedIn placeholder
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    # --- Objective ---
    objective = _pick_objective(student, job)

    # --- Education ---
    edu_lines = [f"**{program}**"]
    if grad:
        edu_lines.append(f"Expected Graduation: {grad}")
    if gpa:
        edu_lines.append(f"GPA: {gpa}")
    edu_block = "\n\n".join(edu_lines)

    # --- Certifications ---
    cert_lines = [f"- **{c['item']}** — {c['level']}" for c in certifications if c.get("item")]
    cert_block = "\n".join(cert_lines) if cert_lines else "- Actively pursuing relevant certifications"

    # --- Technical Skills ---
    # Separate strong/comfortable from beginner; list stronger ones first
    strong  = [s for s in skills if s.get("level", "").lower() in ("strong", "comfortable")]
    beginner = [s for s in skills if s.get("level", "").lower() == "beginner"]
    ordered = strong + beginner
    skill_names = [s["item"] for s in ordered if s.get("item")]
    # Inject job keywords that appear in required/preferred but aren't already listed
    job_keywords_raw = (required + " " + preferred).lower()
    extras = []
    for kw in ["active directory", "microsoft 365", "google workspace", "ticketing", "powershell", "dns"]:
        if kw in job_keywords_raw and not any(kw in s.lower() for s in skill_names):
            extras.append(kw.title())
    all_skills = skill_names + extras
    skill_block = " · ".join(all_skills)

    # --- Projects ---
    proj_lines = []
    for p in projects:
        if not p.get("title"):
            continue
        verb   = _action_verb(p.get("my_role", ""))
        title  = p["title"]
        role   = p.get("my_role", "")
        tools  = p.get("tools", "")
        result = p.get("result", "")
        line = f"**{title}**"
        if tools:
            line += f" *(Tools: {tools})*"
        line += f"\n- {verb} {role.rstrip('.')}."
        if result:
            line += f" Result: {result.rstrip('.')}."
        proj_lines.append(line)
    proj_block = "\n\n".join(proj_lines)

    # --- Work Experience ---
    work_lines = []
    if work_exp:
        # Parse comma-separated sentences into bullets
        for sentence in re.split(r"[.;]", work_exp):
            sentence = sentence.strip()
            if len(sentence) > 8:
                work_lines.append(f"- {sentence}.")
    work_block = "\n".join(work_lines) if work_lines else "- Relevant work experience detailed upon request."

    # --- Assemble ---
    resume = f"""# {name}
{location} | {slug.replace("-", "")}@email.com | (555) 000-0000 | linkedin.com/in/{slug}

---

## Objective

{objective}

---

## Education

{edu_block}

---

## Certifications

{cert_block}

---

## Technical Skills

{skill_block}

---

## Projects

{proj_block}

---

## Work Experience

{work_block}
"""
    return resume.strip()


# ── Prompt builder (for LLM path) ─────────────────────────────────────────────

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


# ── Public entry point ─────────────────────────────────────────────────────────

def generate_resume(student: dict, skills: list, certifications: list,
                    projects: list, job_posting: dict) -> str:
    """
    Try LLM generation first; fall back to offline template on any API error.
    Returns a Markdown string either way — the caller never sees an exception.
    """
    try:
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
    except Exception:
        # API unavailable (no credits, no key, network error) — use offline builder
        return _build_offline_resume(student, skills, certifications, projects, job_posting)
