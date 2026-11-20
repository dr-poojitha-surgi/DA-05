# Career Readiness Coach — Streamlit App Plan

## Top-Level Overview

Build a two-page Streamlit web app called **Career Readiness Coach** that:
1. Accepts student data via an input form (pre-populated from the sample CSVs but fully editable, so any student can use it).
2. Uses an LLM prompt (via the `ibm-watsonx-ai` SDK or `openai` SDK) to generate a tailored, high-quality resume matched to the selected job posting.
3. Displays the generated resume under the student's name with a polished.
4. Routes to a second page where job-relevant interview questions are shown one at a time, the student types an answer, and the LLM returns structured feedback.

The dataset files ship as seed data only — the app is generic and works for any student who fills in the form.

---

## Architecture Diagram

```
Page 1 — Resume Builder
  ┌─────────────────────────────────────────┐
  │  Sidebar: Input Form                    │
  │  ─ Student Profile fields               │
  │  ─ Skills (dynamic add/remove rows)     │
  │  ─ Certifications (dynamic rows)        │
  │  ─ Projects (dynamic rows)              │
  │  ─ Job Posting selector / free-text     │
  │  ─ [Generate Resume] button             │
  └────────────────┬────────────────────────┘
                   │ LLM prompt
  ┌────────────────▼────────────────────────┐
  │  Main Area                              │
  │  ─ Student name (large heading)         │
  │  ─ Generated resume (styled markdown)   │
  │  ─ [Go to Interview Practice →] button  │
  └─────────────────────────────────────────┘

Page 2 — Interview Practice
  ┌─────────────────────────────────────────┐
  │  Back button                            │
  │  Progress bar  (Q n of N)               │
  │  Question card (category badge)         │
  │  Text-area for answer                   │
  │  [Submit Answer] button                 │
  │  Feedback panel (strength / improve)    │
  │  [Next Question →] button               │
  └─────────────────────────────────────────┘
```

---

## File Structure

```
DA-05/
├── app.py                        # Streamlit entry point, page routing
├── pages/
│   ├── 01_resume_builder.py      # Page 1 logic
│   └── 02_interview_practice.py  # Page 2 logic
├── components/
│   ├── resume_generator.py       # LLM prompt builder + call for resume
│   └── interview_coach.py        # LLM prompt builder + call for feedback
├── data/
│   ├── student_profile.csv
│   ├── skills_and_certifications.csv
│   ├── projects.csv
│   ├── job_postings.csv
│   └── interview_questions.csv
├── utils/
│   └── data_loader.py            # CSV → Python dict helpers
├── styles/
│   └── theme.css                 # Custom CSS injected via st.markdown
├── requirements.txt
└── README.md
```

---

## Sub-Tasks

---

### Sub-Task 1 — Project Scaffold & Data Layer

**Intent:** Create the repo skeleton, install dependencies, and write the data-loading utilities so all subsequent sub-tasks have a stable foundation.

**Expected Outcomes:**
- `requirements.txt` lists all dependencies.
- `utils/data_loader.py` exposes functions to load each CSV into clean Python dicts/lists.
- Running `streamlit run app.py` opens a blank app without errors.
- The `data/` folder contains all five CSVs copied from the source location.

**Todo List:**
1. Copy the five CSV files from `c:\Users\pooji\OneDrive\files\team-05\data\` into `DA-05/data/`.
2. Create `requirements.txt` with: `streamlit`, `pandas`, `python-dotenv`, and one LLM client (`ibm-watsonx-ai` or `openai` — use `openai` as the default shim since it is simpler and IBM watsonx exposes an OpenAI-compatible endpoint).
3. Create `utils/data_loader.py` with five functions: `load_student_profile()`, `load_skills_and_certifications()`, `load_projects()`, `load_job_postings()`, `load_interview_questions()` — each reads the matching CSV and returns a list of dicts.
4. Create `app.py` as a minimal Streamlit entry point that sets page config (title, icon, wide layout) and renders a placeholder heading.
5. Create empty `pages/01_resume_builder.py` and `pages/02_interview_practice.py`.
6. Create a `.env.example` with `OPENAI_API_KEY=` (or watsonx equivalent).

**Relevant Context:**
- CSVs are in `c:\Users\pooji\OneDrive\files\team-05\data\`
- `student_profile.csv` uses a `field / value` structure (key-value rows) — `load_student_profile()` must pivot it into a single dict `{field: value}`.
- All other CSVs are standard tabular (one row per record).

**Status:** `[ ] pending`

---

### Sub-Task 2 — Resume Builder Page (UI + Input Form)

**Intent:** Build the full input form in the sidebar and the main-area display shell on Page 1, pre-populated with the sample student data so the demo works out of the box.

**Expected Outcomes:**
- Sidebar renders all input sections: Student Profile, Skills, Certifications, Projects, Job Posting.
- Each section is pre-populated from the CSV seed data.
- Skills and Projects support dynamic add-row behaviour (st.button to add a blank row stored in `st.session_state`).
- Job Posting section shows a dropdown of the five sample postings; selecting one auto-fills a read-only preview; there is also a "Custom job posting" option that reveals a free-text area.
- A "Generate Resume" primary button is visible at the bottom of the sidebar.
- Main area shows a placeholder ("Your resume will appear here") before generation.

**Todo List:**
1. In `pages/01_resume_builder.py`, initialise `st.session_state` keys for all form data using the loaded seed data as defaults.
2. Build the Student Profile section: `name`, `program`, `expected_graduation`, `gpa`, `location`, `work_experience`, `goal` — each as a labelled `st.text_input` or `st.text_area`.
3. Build the Skills section as a dynamic table: each row has `item`, `level` text inputs; Add Skill / Remove last buttons update `st.session_state`.
4. Build the Certifications section the same way (filtered from skills_and_certifications where `type == Certification`).
5. Build the Projects section: each row has `title`, `my_role`, `tools`, `result`; dynamic add/remove.
6. Build the Job Posting section: dropdown + preview + custom option.
7. Add "Generate Resume" button (primary style).
8. Main area: student name as `st.title`, resume placeholder below.

**Relevant Context:**
- `student_profile.csv` fields: `name`, `program`, `expected_graduation`, `gpa`, `location`, `work_experience`, `goal`.
- `skills_and_certifications.csv` columns: `item`, `type`, `level`, `evidence`.
- `projects.csv` columns: `project_id`, `title`, `course`, `team_or_solo`, `my_role`, `tools`, `result`.
- `job_postings.csv` columns: `job_id`, `title`, `employer`, `location`, `type`, `duties`, `required`, `preferred`.

**Status:** `[ ] pending`

---

### Sub-Task 3 — LLM Resume Generation

**Intent:** Wire the "Generate Resume" button to an LLM call that takes all form inputs and the selected job posting and returns a formatted, hirable resume as markdown.

**Expected Outcomes:**
- `components/resume_generator.py` exports `generate_resume(student, skills, certifications, projects, job_posting) -> str`.
- The function builds a structured prompt that instructs the LLM to act as an expert recruiter and produce a tailored resume.
- The resume is returned as markdown and rendered in the main area using `st.markdown`.
- A `st.spinner` shows while the LLM is working.
- The generated resume is stored in `st.session_state["resume"]` so the Interview page can reference it.
- Error handling: if the API key is missing or the call fails, a friendly `st.error` is shown.

**Todo List:**
1. Create `components/resume_generator.py` with `build_resume_prompt()` and `generate_resume()`.
2. `build_resume_prompt()` assembles a system message ("You are a senior technical recruiter with 15+ years of experience...") and a user message containing all student data and the job posting, with explicit instructions: match keywords from the posting, lead with strongest qualifications, use action verbs, keep to one page, output clean markdown.
3. `generate_resume()` calls the LLM via the OpenAI-compatible client, sets `temperature=0.4` for consistent output.
4. In `pages/01_resume_builder.py`, on button click: call `generate_resume()`, store in `st.session_state["resume"]`, re-render the main area.
5. Display the resume inside a styled container (white card, subtle shadow via CSS).
6. Add a "Go to Interview Practice →" `st.button` below the resume (only visible once a resume has been generated), and use `st.switch_page` to navigate.

**Relevant Context:**
- Prompt must reference the job's `required` and `preferred` columns to tailor keyword matching.
- The resume should include sections: Contact, Objective, Education, Skills, Certifications, Projects, Work Experience.

**Status:** `[ ] pending`

---

### Sub-Task 4 — Interview Practice Page

**Intent:** Build Page 2 that surfaces relevant interview questions filtered to the selected job posting, lets the student type answers, and returns LLM feedback per answer.

**Expected Outcomes:**
- Page loads the full interview question bank (18 questions) from `interview_questions.csv`.
- Questions are filtered/ranked by relevance to the job posting stored in `st.session_state` (match on `skill_tag`).
- Questions are shown one at a time with a progress bar.
- Each question card shows: question text, category badge (General / Behavioral / Technical / Scenario) with colour coding.
- Student types answer in a `st.text_area`.
- "Submit Answer" triggers an LLM call to `components/interview_coach.py` which returns: a **Strength** sentence and an **Improve** sentence based on `strong_answer_includes`.
- Feedback is displayed in a two-column card (green for strength, amber for improve).
- "Next Question →" advances to the next question; after the last question a summary screen shows all questions, the student's answers, and all feedback.

**Todo List:**
1. Create `components/interview_coach.py` with `get_answer_feedback(question, strong_answer_includes, student_answer) -> dict` returning `{"strength": str, "improve": str}`.
2. Build the feedback prompt: system = senior interviewer persona; user message contains the question, what a strong answer includes, and the student's answer; instruct to return exactly two sentences labelled Strength and Improve.
3. In `pages/02_interview_practice.py`, initialise session state: `q_index`, `answers`, `feedbacks`, filtered question list.
4. Filter questions by matching `skill_tag` values to job posting's `required` + `preferred` text; keep all questions if no match found (fallback).
5. Render progress bar using `st.progress(q_index / total)`.
6. Render question card with category badge (use coloured `st.badge` or CSS-styled `st.markdown`).
7. On "Submit Answer": call `get_answer_feedback()`, store in `st.session_state["feedbacks"]`, display feedback panel.
8. On "Next Question →": increment `q_index`, clear the text area.
9. After last question: render summary table with question, answer, strength, improve columns.
10. Add a "← Back to Resume" button that uses `st.switch_page` to return to Page 1.

**Relevant Context:**
- `interview_questions.csv` columns: `question_id`, `question`, `category`, `skill_tag`, `strong_answer_includes`.
- Categories for colour coding: General=blue, Behavioral=purple, Technical=teal, Scenario=orange.

**Status:** `[ ] pending`

---

### Sub-Task 5 — Styling & UX Polish

**Intent:** Apply a cohesive, simplistic visual design across both pages so the app looks professional and aesthetically pleasing.

**Expected Outcomes:**
- Custom CSS injected via `st.markdown` (loaded from `styles/theme.css`) applies a clean sans-serif font, soft background colour, card-style containers, and consistent spacing.
- Student name on Page 1 renders as a large, prominent heading with a subtle accent underline.
- Resume renders inside a white card with a soft drop shadow, mimicking a real resume document.
- Interview question cards have a light border-left accent bar matching the category colour.
- Feedback panel uses a two-tone design (green left / amber right).
- Buttons use consistent primary/secondary styling.
- Sidebar has a slightly darker background to separate it visually from the main content area.
- App is mobile-friendly (uses Streamlit's responsive column system).
- A minimal Ivy Tech / Career Coach brand mark (text-based logo) appears in the sidebar header.

**Todo List:**
1. Create `styles/theme.css` with: Google Fonts import (Inter), background colours, card styles, badge styles, button overrides, heading styles.
2. Create a `utils/style_loader.py` helper `inject_css()` that reads `theme.css` and injects it via `st.markdown(..., unsafe_allow_html=True)`.
3. Call `inject_css()` at the top of both page files.
4. Wrap the resume output in a `<div class="resume-card">` HTML block.
5. Add category-coloured left-border to interview question cards.
6. Test layout at narrow viewport by reviewing column widths.

**Relevant Context:**
- Streamlit's native theming (`[theme]` in `.streamlit/config.toml`) sets base colours; custom CSS overrides specific components.
- Use `primaryColor`, `backgroundColor`, `secondaryBackgroundColor`, `textColor` in `.streamlit/config.toml` as the base, then CSS for cards and badges.

**Status:** `[ ] pending`

---

### Sub-Task 6 — Configuration, README & Final Wiring

**Intent:** Make the app runnable from a fresh clone with minimal setup, and document it properly for the submission.

**Expected Outcomes:**
- `.streamlit/config.toml` sets the theme palette.
- `.env.example` documents required environment variables.
- `README.md` has: project description, setup steps (`pip install -r requirements.txt`, set `OPENAI_API_KEY`, `streamlit run app.py`), and a brief section on how IBM Bob / AI was used.
- Both pages import and work end-to-end without errors.
- `requirements.txt` is pinned to working versions.

**Todo List:**
1. Create `.streamlit/config.toml` with a clean light theme (primary blue-indigo, white background, light grey secondary).
2. Update `README.md` with full project description, setup instructions, and AI/IBM Bob usage note.
3. Final pass: confirm all `st.session_state` keys used across pages are consistent.
4. Confirm `st.switch_page` paths match the actual file paths under `pages/`.
5. Add a `requirements.txt` with pinned versions tested locally.

**Relevant Context:**
- Streamlit multi-page apps use the `pages/` folder convention; filenames become page names.
- `st.switch_page("pages/02_interview_practice.py")` is the correct navigation call.

**Status:** `[ ] pending`

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| LLM client | OpenAI-compatible (`openai` package) | Works with OpenAI, IBM watsonx, and any compatible endpoint via base_url override |
| Multi-page routing | Streamlit native `pages/` folder | Zero extra dependencies, clean URLs |
| Session state | `st.session_state` dict | Only built-in state mechanism in Streamlit |
| Form data storage | `st.session_state` lists of dicts | Enables dynamic add/remove rows |
| Resume format | Markdown rendered via `st.markdown` | Preserves structure, easy to style |
| Interview filtering | Keyword match on skill_tag vs job posting text | Simple, no extra ML needed |
| Styling approach | CSS injected + `.streamlit/config.toml` | Deepest styling control available in Streamlit |
