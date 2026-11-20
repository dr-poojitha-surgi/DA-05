"""
pages/01_resume_builder.py
Page 1 — Resume Builder
"""

import sys, os, re as _re
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.data_loader import (
    load_student_profile, load_skills_and_certifications,
    load_projects, load_job_postings,
)
from utils.style_loader import inject_css
from components.resume_generator import generate_resume

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Career Readiness Coach",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()


# ── Helpers ────────────────────────────────────────────────────────────────────
def _escape_inline(text: str) -> str:
    """Escape HTML and render **bold** and *italic* inline markdown."""
    import html as _h
    text = _h.escape(text)
    text = _re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = _re.sub(r"\*(.+?)\*",     r"<em>\1</em>",         text)
    return text


def _md_to_html(md: str) -> str:
    """Minimal markdown→HTML for resume rendering inside the styled card div."""
    lines = md.split("\n")
    out = []
    in_ul = False
    for line in lines:
        raw = line
        if raw.startswith("### "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h3>{_escape_inline(raw[4:])}</h3>")
        elif raw.startswith("## "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h2>{_escape_inline(raw[3:])}</h2>")
        elif raw.startswith("# "):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<h1>{_escape_inline(raw[2:])}</h1>")
        elif raw.startswith("- ") or raw.startswith("* "):
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{_escape_inline(raw[2:])}</li>")
        elif raw.strip() in ("---", "***", "___"):
            if in_ul: out.append("</ul>"); in_ul = False
            out.append("<hr>")
        elif raw.strip() == "":
            if in_ul: out.append("</ul>"); in_ul = False
            out.append("")
        else:
            if in_ul: out.append("</ul>"); in_ul = False
            out.append(f"<p>{_escape_inline(raw)}</p>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


# ── Seed data (loaded once) ────────────────────────────────────────────────────
@st.cache_data
def _seed():
    profile  = load_student_profile()
    snc      = load_skills_and_certifications()
    skills   = [r for r in snc if r["type"] == "Skill"]
    certs    = [r for r in snc if r["type"] == "Certification"]
    jobs     = load_job_postings()
    projects = load_projects()
    return profile, skills, certs, jobs, projects


seed_profile, seed_skills, seed_certs, seed_jobs, seed_projects = _seed()


# ── Session-state initialisation ───────────────────────────────────────────────
def _init_state():
    if "profile" not in st.session_state:
        st.session_state.profile = dict(seed_profile)
    if "skills" not in st.session_state:
        st.session_state.skills = [{"item": s["item"], "level": s["level"]} for s in seed_skills]
    if "certs" not in st.session_state:
        st.session_state.certs = [{"item": c["item"], "level": c["level"]} for c in seed_certs]
    if "projects" not in st.session_state:
        st.session_state.projects = [
            {
                "title":   p["title"],
                "my_role": p["my_role"],
                "tools":   p["tools"],
                "result":  p["result"],
            }
            for p in seed_projects
        ]
    if "job_index" not in st.session_state:
        st.session_state.job_index = 0
    if "custom_job" not in st.session_state:
        st.session_state.custom_job = ""
    if "resume" not in st.session_state:
        st.session_state.resume = ""
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = dict(seed_jobs[0])
    if "interview_job" not in st.session_state:
        st.session_state.interview_job = dict(seed_jobs[0])


_init_state()


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Input Form
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # Brand mark
    st.markdown(
        """
        <div class="brand-mark">
          <div class="brand-icon">🎓</div>
          <div class="brand-text">
            <div class="brand-title">Career Readiness Coach</div>
            <div class="brand-sub">Ivy Tech · 2030 Initiative</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Student Profile ──────────────────────────────────────────────────────
    st.markdown("### 👤 Student Profile")
    p = st.session_state.profile
    p["name"]                = st.text_input("Full Name",           value=p.get("name", ""),                key="p_name")
    p["program"]             = st.text_input("Program / Major",     value=p.get("program", ""),             key="p_prog")
    p["expected_graduation"] = st.text_input("Expected Graduation", value=p.get("expected_graduation", ""), key="p_grad")
    p["gpa"]                 = st.text_input("GPA",                 value=p.get("gpa", ""),                 key="p_gpa")
    p["location"]            = st.text_input("Location",            value=p.get("location", ""),            key="p_loc")
    p["work_experience"]     = st.text_area ("Work Experience",     value=p.get("work_experience", ""),     key="p_work", height=80)
    p["goal"]                = st.text_area ("Career Goal",         value=p.get("goal", ""),                key="p_goal", height=70)

    st.markdown("---")

    # ── Skills ───────────────────────────────────────────────────────────────
    st.markdown("### 🛠 Skills")
    skills_to_remove = None
    for i, skill in enumerate(st.session_state.skills):
        c1, c2, c3 = st.columns([3, 2, 1])
        with c1:
            skill["item"]  = st.text_input("Skill", value=skill["item"],  key=f"sk_item_{i}", label_visibility="collapsed", placeholder="Skill name")
        with c2:
            skill["level"] = st.text_input("Level", value=skill["level"], key=f"sk_lvl_{i}",  label_visibility="collapsed", placeholder="Level")
        with c3:
            if st.button("✕", key=f"sk_rm_{i}", help="Remove skill"):
                skills_to_remove = i
    if skills_to_remove is not None:
        st.session_state.skills.pop(skills_to_remove)
        st.rerun()
    if st.button("＋ Add Skill", key="add_skill"):
        st.session_state.skills.append({"item": "", "level": ""})
        st.rerun()

    st.markdown("---")

    # ── Certifications ───────────────────────────────────────────────────────
    st.markdown("### 🏅 Certifications")
    certs_to_remove = None
    for i, cert in enumerate(st.session_state.certs):
        c1, c2, c3 = st.columns([3, 3, 1])
        with c1:
            cert["item"]  = st.text_input("Certification", value=cert["item"],  key=f"ct_item_{i}", label_visibility="collapsed", placeholder="Certification name")
        with c2:
            cert["level"] = st.text_input("Status",        value=cert["level"], key=f"ct_lvl_{i}",  label_visibility="collapsed", placeholder="Status / year")
        with c3:
            if st.button("✕", key=f"ct_rm_{i}", help="Remove cert"):
                certs_to_remove = i
    if certs_to_remove is not None:
        st.session_state.certs.pop(certs_to_remove)
        st.rerun()
    if st.button("＋ Add Certification", key="add_cert"):
        st.session_state.certs.append({"item": "", "level": ""})
        st.rerun()

    st.markdown("---")

    # ── Projects ─────────────────────────────────────────────────────────────
    st.markdown("### 📂 Projects")
    proj_to_remove = None
    for i, proj in enumerate(st.session_state.projects):
        with st.expander(proj["title"] or f"Project {i+1}", expanded=False):
            proj["title"]   = st.text_input("Title",    value=proj["title"],   key=f"pr_title_{i}")
            proj["my_role"] = st.text_area ("My Role",  value=proj["my_role"], key=f"pr_role_{i}",  height=60)
            proj["tools"]   = st.text_input("Tools",    value=proj["tools"],   key=f"pr_tools_{i}")
            proj["result"]  = st.text_input("Result",   value=proj["result"],  key=f"pr_res_{i}")
            if st.button("🗑 Remove Project", key=f"pr_rm_{i}"):
                proj_to_remove = i
    if proj_to_remove is not None:
        st.session_state.projects.pop(proj_to_remove)
        st.rerun()
    if st.button("＋ Add Project", key="add_proj"):
        st.session_state.projects.append({"title": "", "my_role": "", "tools": "", "result": ""})
        st.rerun()

    st.markdown("---")

    # ── Job Posting ──────────────────────────────────────────────────────────
    st.markdown("### 💼 Target Job Posting")
    job_options = [f"{j['title']} — {j['employer']}" for j in seed_jobs] + ["✏️ Custom job posting…"]
    selected_label = st.selectbox("Select a job", job_options, index=st.session_state.job_index, key="job_select")
    idx = job_options.index(selected_label)
    st.session_state.job_index = idx

    if idx < len(seed_jobs):
        j = seed_jobs[idx]
        st.session_state.selected_job = dict(j)
        st.caption(f"📍 {j['location']} · {j['type']}")
        st.caption(f"**Required:** {j['required']}")
        if j.get("preferred"):
            st.caption(f"**Preferred:** {j['preferred']}")
    else:
        custom_text = st.text_area(
            "Paste job posting text",
            value=st.session_state.custom_job,
            height=130,
            key="custom_job_text",
            placeholder="Paste the full job description here…",
        )
        st.session_state.custom_job = custom_text
        st.session_state.selected_job = {
            "title":     "Custom Role",
            "employer":  "Custom Employer",
            "location":  "",
            "type":      "",
            "duties":    custom_text,
            "required":  custom_text,
            "preferred": "",
        }

    st.markdown("---")

    # ── Generate button ──────────────────────────────────────────────────────
    generate_clicked = st.button("✨ Generate Resume", use_container_width=True, type="primary")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════════════════════════
name_display = st.session_state.profile.get("name", "") or "Your Name"

# Student name heading
st.markdown(
    f"""
    <div class="student-name-heading">{name_display}</div>
    <div class="student-name-subline"></div>
    """,
    unsafe_allow_html=True,
)

# ── Handle generation ─────────────────────────────────────────────────────────
if generate_clicked:
    if not st.session_state.profile.get("name", "").strip():
        st.warning("Please enter a student name before generating.")
    else:
        with st.spinner("Crafting your resume…"):
            try:
                resume_md = generate_resume(
                    student=st.session_state.profile,
                    skills=st.session_state.skills,
                    certifications=st.session_state.certs,
                    projects=st.session_state.projects,
                    job_posting=st.session_state.selected_job,
                )
                st.session_state.resume = resume_md
                st.session_state.interview_job = dict(st.session_state.selected_job)
                # Reset interview state so a new session starts fresh
                for key in ("q_index", "answers", "feedbacks", "filtered_questions", "interview_done"):
                    st.session_state.pop(key, None)
            except Exception as exc:
                st.error(f"❌ Could not generate resume. Check your API key and try again.\n\n`{exc}`")

# ── Display resume or placeholder ────────────────────────────────────────────
if st.session_state.resume:
    st.markdown(
        f'<div class="resume-card">{_md_to_html(st.session_state.resume)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_btn, _ = st.columns([2, 3, 2])
    with col_btn:
        if st.button("🎤 Practice Interview Questions →", use_container_width=True, type="primary"):
            st.switch_page("pages/02_interview_practice.py")
else:
    st.markdown(
        """
        <div class="placeholder-card">
          <div class="ph-icon">📄</div>
          <div class="ph-text">Your tailored resume will appear here</div>
          <div class="ph-sub">Fill in the form on the left, choose a job posting,<br>then click <strong>✨ Generate Resume</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
