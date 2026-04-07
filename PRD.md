# Product Requirements Document (PRD)

## Project Title
**Salary Prediction Application** – End-to-End ML Pipeline from Data to Deployment

## Version
1.0 (Week 1 Assignment – AIE Program)

## Deadline
**Friday, 06:00 AM** (as specified in the assignment PDF)

## 1. Objective / Mission
Build and deploy a **Salary Prediction Application** for data science jobs.

The application:
- Takes inputs such as experience level, employment type, company size, job title, and other relevant features.
- Predicts the expected salary (in USD) using a **trained Decision Tree model** served via a self-built and deployed API.
- Passes the prediction + input data to a **local LLM** (via Ollama) acting as a data analyst. The LLM generates a **written narrative** with insights and **at least one visualization** (chart or graph) explaining the salary landscape.
- Stores all results in **Supabase**.
- Displays everything on a live, interactive **Streamlit dashboard** that users can explore.

The project follows a **pre-generation architecture**:
- Local pipeline generates predictions + LLM analysis once (or on demand).
- Results are stored in cloud storage (Supabase).
- Deployed consumption layer (dashboard) reads only from Supabase.

A **standalone deployed FastAPI** endpoint (same model) must also be provided independently.

**Key Goal**: Demonstrate a complete ML pipeline — data cleaning → modeling → API → LLM augmentation → persistence → dashboard — while following best practices and understanding every line of code.

## 2. Scope
### In Scope
- Dataset cleaning and preparation (Kaggle: Data Science Job Salaries).
- Training a **Decision Tree Regressor** (sklearn) with proper folder structure and evaluation.
- FastAPI endpoint (GET or POST) with input validation (Pydantic) for salary prediction.
- Python script that systematically calls the API, covers a wide range of realistic input combinations, and handles errors gracefully.
- Local Ollama integration for narrative generation + at least one visualization per prediction (storytelling quality is important).
- Custom Supabase schema for storing predictions, narratives, and visualizations.
- Streamlit dashboard that consumes **only** from Supabase, with filters, displays of predictions, narratives, and charts. Graceful handling of missing data.
- Standalone deployment of the FastAPI API (independent of local pipeline).
- Clean Git workflow using only Git CLI (`git add`, `git commit`, `git push` — no GitHub Desktop).
- Comprehensive README.md.

### Out of Scope
- Real-time inference in the dashboard (pre-generation only).
- Running Ollama or heavy LLM calls in the deployed dashboard.
- User authentication or advanced security.
- Production-scale traffic or monitoring.

## 3. Architecture
**Pre-generation Architecture** (Local Pipeline):

Local Pipeline
├── Input combinations → FastAPI (deployed or local) → Salary Prediction
├── Prediction + inputs → Local Ollama (LLM Analyst) → Narrative + Visualization
└── Results → Supabase (PostgreSQL + optional Storage for images)


**Deployed Consumption Layer**:
- **Streamlit Dashboard** → Reads only from Supabase (caching recommended).
- **Standalone FastAPI** → Independent deployment serving the same Decision Tree model.

**Technology Stack** (Best Free Choices – 2026):
- **Model & Backend**: Python, scikit-learn, FastAPI, Pydantic, joblib
- **LLM**: Ollama (local, free)
- **Database & Storage**: **Supabase** (Free Hobby tier – 500 MB DB, 1 GB storage, unlimited API requests, sufficient for this project)
- **Dashboard**: **Streamlit** + Streamlit Community Cloud (completely free for public apps)
- **FastAPI Deployment** (best free options ranked):
  1. **Render.com** (Hobby free tier – 512 MB RAM, 0.1 CPU, spins down when idle, Git-based deploy, easy for Python/FastAPI)
  2. **Railway** or **Leapcell** (generous free tiers, no credit card needed for basic usage)
  3. **Fly.io** (good free allowance) or Hugging Face Spaces (if keeping it very lightweight)
- **Version Control**: Git CLI only
- **Visualization**: Matplotlib / Seaborn / Plotly (generated via LLM or in dashboard)

**Data Flow**:
Local script → Deployed FastAPI → Ollama → Supabase → Streamlit Dashboard

## 4. Functional Requirements

### 4.1 Data Preparation
- Download dataset from Kaggle.
- Clean data (handle missing values, encode categoricals, ensure `salary_in_usd` target).
- Exploratory analysis in notebook (optional but recommended).

### 4.2 Model Training
- Train `DecisionTreeRegressor`.
- Save model with `joblib`.
- Follow clean folder structure (`models/`, `src/`, etc.).
- Basic evaluation (MAE, RMSE).

### 4.3 FastAPI Endpoint
- Input validation for all features (experience_level, employment_type, company_size, job_title, etc.).
- Preprocessing must match training pipeline.
- Return predicted salary in USD.
- Deployed as a **standalone** public URL.

### 4.4 Generation Script
- Generate diverse, realistic input combinations (use `itertools.product` or similar).
- Call FastAPI safely (try/except, logging).
- No unhandled errors.

### 4.5 LLM Analysis (Ollama)
- Prompt must produce:
  - Insightful narrative (2–4 paragraphs) with storytelling quality.
  - At least one visualization (Python code for chart or generated image).
- Store narrative text and chart (base64, image path, or Supabase Storage URL).

### 4.6 Supabase Integration
- Design schema (`salary_predictions` table) with columns for inputs, predicted_salary, narrative, chart_data/image_url, timestamp, etc.
- Insert results from local script.
- Support dashboard queries and filters.

### 4.7 Streamlit Dashboard
- Connect to Supabase (use `supabase-py` or st.connection).
- Filters (experience level, job title, company size, etc.).
- Display table, individual predictions with narratives, and visualizations.
- Aggregate charts (e.g., average salary by experience).
- Handle missing data gracefully.
- Deployed on Streamlit Community Cloud.

## 5. Non-Functional Requirements
- **Understand every line** (no vibe coding).
- All code must be readable with comments.
- Error handling and graceful degradation.
- Supabase free tier limits respected (keep data volume small).
- Dashboard should be interactive and insightful.
- Git history clean and professional.

## 6. Deliverables
- **Live Streamlit web app URL**
- **Deployed FastAPI endpoint URL** (standalone)
- **Well-presented README.md** (architecture, setup, run instructions, folder structure, explanations)
- Git repository (Git CLI only)

## 7. Deployment Strategy (Free Tier Optimized)
- **Supabase**: Free Hobby plan (create one project).
- **Streamlit**: Deploy directly from GitHub to Streamlit Community Cloud (free).
- **FastAPI**: Render.com Hobby tier (recommended first choice – simple Git deploy, supports Python). Alternatives: Railway or Leapcell.
- Store Supabase URL and anon key in `.env` (never commit secrets). Use `st.secrets` for Streamlit.

## 8. Risks & Mitigations
- Supabase storage/egress limits → Keep number of generated predictions reasonable (~50–200) and use small images or text-based charts when possible.
- FastAPI deployment spin-down (free tiers) → Acceptable for demo.
- Ollama visualization consistency → Strong, structured prompting + fallback to dashboard-generated charts.
- Preprocessing mismatch → Centralize preprocessing code.

## 9. Success Criteria
- FastAPI returns accurate predictions.
- LLM narratives are useful and contain at least one visualization.
- Dashboard loads data from Supabase, supports interaction, and looks professional.
- All deliverables submitted on time.
- Ability to explain every part of the code.

## Approval / Next Steps
This PRD aligns 100% with the Week 1 Assignment PDF.

Ready for implementation.  
**Start with**: Dataset download + cleaning → Model training → FastAPI.

---

**Created for**: Week 1 Salary Prediction Assignment  
**Date**: April 2026