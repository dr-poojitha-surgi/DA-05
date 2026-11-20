"""
pages/02_interview_practice.py
Page 2 — Interview Practice
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.data_loader import load_interview_questions
from utils.style_loader import inject_css
from components.interview_coach import get_answer_feedback

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Interview Practice — Career Readiness Coach",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed",
)
inject_css()


# ── Category helpers ───────────────────────────────────────────────────────────
CATEGORY_CLASS = {
    "General":    "cat-general",
    "Behavioral": "cat-behavioral",
    "Technical":  "cat-technical",
    "Scenario":   "cat-scenario",
}
BADGE_CLASS = {
    "General":    "badge-general",
    "Behavioral": "badge-behavioral",
    "Technical":  "badge-technical",
    "Scenario":   "badge-scenario",
}


def _filter_questions(all_qs: list, job: dict) -> list:
    """
    Return questions whose skill_tag appears in the job's required or preferred text.
    Falls back to all questions if no matches found.
    """
    if not job:
        return all_qs
    job_text = (
        (job.get("required", "") or "") + " " +
        (job.get("preferred", "") or "") + " " +
        (job.get("duties", "") or "")
    ).lower()

    matched = []
    unmatched = []
    for q in all_qs:
        tag = (q.get("skill_tag") or "").lower()
        if tag == "all" or any(word in job_text for word in tag.split()):
            matched.append(q)
        else:
            unmatched.append(q)

    # Always include General questions; pad with unmatched if fewer than 6 matched
    result = matched if matched else all_qs
    if len(result) < 6:
        result = result + unmatched[: 6 - len(result)]
    return result


# ── Load seed data ─────────────────────────────────────────────────────────────
@st.cache_data
def _all_questions():
    return load_interview_questions()


# ── Session state initialisation ──────────────────────────────────────────────
def _init_state():
    all_qs = _all_questions()
    job    = st.session_state.get("interview_job", {})

    if "filtered_questions" not in st.session_state:
        st.session_state.filtered_questions = _filter_questions(all_qs, job)
    if "q_index" not in st.session_state:
        st.session_state.q_index = 0
    if "answers" not in st.session_state:
        st.session_state.answers = {}
    if "feedbacks" not in st.session_state:
        st.session_state.feedbacks = {}
    if "interview_done" not in st.session_state:
        st.session_state.interview_done = False
    if "current_answer" not in st.session_state:
        st.session_state.current_answer = ""
    if "feedback_pending" not in st.session_state:
        st.session_state.feedback_pending = False


_init_state()

questions  = st.session_state.filtered_questions
q_index    = st.session_state.q_index
total      = len(questions)


# ══════════════════════════════════════════════════════════════════════════════
# HEADER BAR
# ══════════════════════════════════════════════════════════════════════════════
col_back, col_title = st.columns([1, 5])
with col_back:
    if st.button("← Resume", key="back_btn"):
        st.switch_page("pages/01_resume_builder.py")
with col_title:
    st.markdown(
        "<h2 style='margin:0;padding:0;font-size:1.35rem;color:#0f1f35;font-weight:700;'>🎤 Interview Practice</h2>",
        unsafe_allow_html=True,
    )

job = st.session_state.get("interview_job", {})
if job.get("title"):
    st.caption(f"Preparing for: **{job['title']}** at {job.get('employer', '')}")

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY SCREEN (after last question)
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.interview_done:
    st.markdown(
        "<h3 style='color:#0f1f35;margin-bottom:0.3rem;'>🏁 Practice Complete!</h3>"
        "<p style='color:#64748b;margin-top:0;'>Here's a summary of your answers and feedback.</p>",
        unsafe_allow_html=True,
    )

    rows_html = ""
    for i, q in enumerate(questions):
        qid      = q["question_id"]
        answer   = st.session_state.answers.get(qid, "—")
        fb       = st.session_state.feedbacks.get(qid, {})
        strength = fb.get("strength", "—")
        improve  = fb.get("improve", "—")
        rows_html += f"""
        <tr>
          <td style="font-weight:600;color:#0f1f35;width:30%">{q['question']}</td>
          <td style="color:#334155;width:25%">{answer}</td>
          <td style="color:#15803d;width:22%">{strength}</td>
          <td style="color:#b45309;width:23%">{improve}</td>
        </tr>
        """

    st.markdown(
        f"""
        <table class="summary-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Your Answer</th>
              <th>✅ Strength</th>
              <th>💡 Improve</th>
            </tr>
          </thead>
          <tbody>
            {rows_html}
          </tbody>
        </table>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Practice Again", use_container_width=True, type="primary"):
            for key in ("q_index", "answers", "feedbacks", "interview_done", "current_answer", "feedback_pending"):
                st.session_state.pop(key, None)
            st.rerun()
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# ACTIVE QUESTION SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if q_index >= total:
    st.session_state.interview_done = True
    st.rerun()

current_q = questions[q_index]
qid       = current_q["question_id"]
category  = current_q.get("category", "General")
q_class   = CATEGORY_CLASS.get(category, "cat-general")
badge_cls = BADGE_CLASS.get(category, "badge-general")

# ── Progress ──────────────────────────────────────────────────────────────────
progress_val = q_index / total
st.markdown(
    f'<div class="progress-label">Question {q_index + 1} of {total}</div>',
    unsafe_allow_html=True,
)
st.progress(progress_val)
st.markdown("<br>", unsafe_allow_html=True)

# ── Question card ─────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="q-card {q_class}">
      <span class="badge {badge_cls}">{category}</span>
      <div class="q-text">{current_q['question']}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Answer text area ──────────────────────────────────────────────────────────
answer_key = f"answer_{qid}"
user_answer = st.text_area(
    "Your answer",
    value=st.session_state.answers.get(qid, ""),
    height=150,
    key=answer_key,
    placeholder="Type your answer here… be as detailed as you can.",
    label_visibility="collapsed",
)

# ── Action buttons ────────────────────────────────────────────────────────────
col_sub, col_next = st.columns([2, 1])
with col_sub:
    submit_clicked = st.button("✅ Submit Answer", use_container_width=True, type="primary", key="submit_btn")
with col_next:
    # Only show Next if already submitted
    already_submitted = qid in st.session_state.feedbacks
    next_label = "Finish →" if q_index == total - 1 else "Next Question →"
    next_clicked = st.button(next_label, use_container_width=True, disabled=not already_submitted, key="next_btn")

# ── Handle submit ─────────────────────────────────────────────────────────────
if submit_clicked:
    if not user_answer.strip():
        st.warning("Please type an answer before submitting.")
    else:
        st.session_state.answers[qid] = user_answer.strip()
        with st.spinner("Getting feedback…"):
            try:
                fb = get_answer_feedback(
                    question=current_q["question"],
                    strong_answer_includes=current_q.get("strong_answer_includes", ""),
                    student_answer=user_answer.strip(),
                )
                st.session_state.feedbacks[qid] = fb
            except Exception as exc:
                st.session_state.feedbacks[qid] = {
                    "strength": "Could not retrieve feedback.",
                    "improve":  f"Check your API key: {exc}",
                }
        st.rerun()

# ── Handle next ───────────────────────────────────────────────────────────────
if next_clicked:
    st.session_state.q_index += 1
    if st.session_state.q_index >= total:
        st.session_state.interview_done = True
    st.rerun()

# ── Display feedback (if already submitted) ───────────────────────────────────
if qid in st.session_state.feedbacks:
    fb = st.session_state.feedbacks[qid]
    st.markdown(
        f"""
        <div class="feedback-row">
          <div class="feedback-strength">
            <div class="feedback-label">✅ Strength</div>
            <div class="feedback-body">{fb.get('strength', '')}</div>
          </div>
          <div class="feedback-improve">
            <div class="feedback-label">💡 Improve</div>
            <div class="feedback-body">{fb.get('improve', '')}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Hint about strong answer
    with st.expander("💬 What a strong answer includes", expanded=False):
        st.markdown(f"*{current_q.get('strong_answer_includes', '')}*")
