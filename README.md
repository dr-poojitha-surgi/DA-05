# Career Readiness Coach

> **2026 Ivy Tech IT Challenge — Case 5**  
> *Turn coursework into a resume and ace the interview.*

---

## What It Does

A two-page Streamlit web app that helps soon-to-be graduates transform their coursework, projects, and skills into a polished, job-tailored resume — and then practice interview questions with AI-powered feedback.

| Page | What you do |
|---|---|
| **Resume Builder** | Enter your profile, skills, certifications, projects, and pick a job posting. Click **Generate Resume** to get an ATS-optimised, one-page resume written by an AI recruiter persona. |
| **Interview Practice** | Work through interview questions filtered to your target job. Type your answer, get instant feedback (Strength + Improve), then review a full summary at the end. |

---

## Setup

### 1. Clone & install
```bash
pip install -r requirements.txt
```

### 2. Set your API key
```bash
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

> **IBM watsonx users:** Set `OPENAI_BASE_URL` and `OPENAI_MODEL` in `.env` to point at your watsonx endpoint.

### 3. Run
```bash
streamlit run app.py
```

---

## Project Structure

```
DA-05/
├── app.py                        # Entry point (redirects to page 1)
├── pages/
│   ├── 01_resume_builder.py      # Resume input form + generation
│   └── 02_interview_practice.py  # Interview Q&A + feedback
├── components/
│   ├── resume_generator.py       # LLM resume prompt + API call
│   └── interview_coach.py        # LLM feedback prompt + API call
├── data/                         # Seed CSV files
├── utils/
│   ├── data_loader.py            # CSV loaders
│   └── style_loader.py           # CSS injection helper
├── styles/theme.css              # Custom UI styles
├── .streamlit/config.toml        # Streamlit theme
└── requirements.txt
```

---

## AI & IBM Bob Usage

This prototype was designed and built with **IBM Bob** as the AI development partner:
- Bob analysed the five seed datasets (student profile, skills, projects, job postings, interview questions) to inform the data model and input form design.
- Bob authored the LLM prompt engineering strategy for both the resume generator (recruiter persona, keyword matching) and the interview coach (structured Strength/Improve feedback).
- The app uses an **OpenAI-compatible LLM client**, which works with IBM watsonx AI endpoints via `base_url` override — aligning with the A-Ivy responsible AI principle of using approved, institution-managed models.

---

## Sample Data

The `data/` folder contains anonymised sample data for a fictional student, **Alex Rivera** (IT student, one semester from graduation). This data is used to pre-populate the form for demo purposes only. Real student data is never stored or transmitted beyond the LLM API call.

---

## Metric This Moves

**Job placement within six months** — by giving students a recruiter-quality resume and targeted interview practice before they graduate.
