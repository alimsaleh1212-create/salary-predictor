# Data Science Salary Prediction Application

End-to-end ML pipeline: predict data science salaries, generate LLM-powered insights, and display results on a live dashboard.

**Week 1 Assignment — AIE Bootcamp**

---

## Live Deliverables

| Service | URL |
|---|---|
| FastAPI Prediction Endpoint | _Add Railway URL after deployment_ |
| Streamlit Dashboard | _Add Railway URL after deployment_ |

---

## Architecture

```
Local Pipeline
──────────────────────────────────────────────────────────
Upload CSV (Streamlit UI)
  → Strict Validation
  → POST /predict (FastAPI on Railway)
  → Random Forest Prediction
  → Local Dockerized Ollama (gemma4:e2b)
  → Manager + Employee Insights + Chart
  → Store in Supabase

Deployed Layer (Railway)
──────────────────────────────────────────────────────────
FastAPI  (/predict)          ← standalone prediction service
Streamlit Dashboard          ← reads only from Supabase
```

---

## Model Performance

| Metric | Value |
|---|---|
| Test MAE | $27,687 |
| Test RMSE | $39,819 |
| Test R² | 0.5863 |
| Algorithm | Random Forest Regressor |
| Train / Test Split | 80 / 20 |
| Cross-Validation | 5-fold GridSearchCV |

---

## Project Structure

```
├── api/                    # FastAPI app (deployed on Railway)
│   ├── main.py             # /predict + /health endpoints
│   ├── models.py           # Pydantic schemas
│   └── predictor.py        # Model loading & inference
├── src/
│   ├── preprocessing.py    # Raw CSV → model features (inference-time)
│   ├── ollama_client.py    # LLM insight generation + chart
│   └── supabase_client.py  # DB read/write helpers
├── streamlit_app/
│   ├── upload_ui.py        # Local CSV upload & analysis pipeline
│   └── dashboard.py        # Deployed read-only dashboard
├── notebooks/
│   ├── 01_Exploratory_Data_Analysis.ipynb
│   ├── 02_Data_Cleaning_and_Feature_Engineering.ipynb
│   └── 03_Model_Training_RF.ipynb
├── data/
│   ├── raw/ds_salaries.csv
│   └── processed/ds_salaries_cleaned.csv
├── models/
│   └── random_forest_model.joblib
├── demo_samples/
│   └── new_records.csv     # 50 synthetic records for testing
├── Dockerfile              # FastAPI deployment
├── Dockerfile.dashboard    # Dashboard deployment
├── railway.toml            # Railway config for FastAPI
└── pyproject.toml          # Dependencies (uv)
```

---

## Local Setup

### Prerequisites
- Python 3.11+
- [uv](https://docs.astral.sh/uv/) package manager
- Docker (for Ollama)
- Supabase account

### 1. Clone & install dependencies

```bash
git clone <repo-url>
cd project1_salary_prediction
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Supabase credentials
```

### 3. Create Supabase table

Run this SQL in your Supabase SQL editor:

```sql
CREATE TABLE salary_predictions (
  id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  created_at           timestamptz DEFAULT now(),
  batch_id             uuid,
  work_year            int,
  experience_level     text,
  employment_type      text,
  job_title            text,
  employee_residence   text,
  remote_ratio         int,
  company_location     text,
  company_size         text,
  predicted_salary_usd numeric,
  manager_insights     text,
  employee_insights    text,
  chart_base64         text
);
```

### 4. Start Ollama (Docker)

```bash
docker run -d -p 11434:11434 --name ollama ollama/ollama
```

> The `gemma4:e2b` model is assumed to already be pulled locally.

### 5. Start the FastAPI server

```bash
uv run uvicorn api.main:app --reload
# API docs at http://localhost:8000/docs
```

### 6. Run the upload UI

```bash
uv run streamlit run streamlit_app/upload_ui.py
```

Upload `demo_samples/new_records.csv` to test the full pipeline.

### 7. Run the dashboard locally

```bash
uv run streamlit run streamlit_app/dashboard.py
```

---

## API Reference

### `GET /health`
Returns `{"status": "ok"}`.

### `POST /predict`
Predict salary for a single record.

**Request body:**
```json
{
  "work_year": 2023,
  "experience_level": "SE",
  "employment_type": "FT",
  "job_title": "Data Scientist",
  "employee_residence": "US",
  "remote_ratio": 100,
  "company_location": "US",
  "company_size": "M"
}
```

**Response:**
```json
{"predicted_salary_usd": 166572.02}
```

### `POST /predict/batch`
Same schema but wrapped: `{"records": [...]}`. Returns `{"predictions": [...]}`.

---

## Deployment (Railway)

### FastAPI
1. Push repo to GitHub
2. Create new Railway project → Deploy from GitHub repo
3. Railway auto-detects `railway.toml` and `Dockerfile`
4. No env vars needed for the API itself (model is bundled)

### Streamlit Dashboard
1. Create a second Railway service in the same project
2. Set `DOCKERFILE_PATH` to `Dockerfile.dashboard`
3. Add env vars: `SUPABASE_URL`, `SUPABASE_KEY`

---

## CSV Upload Requirements

| Field | Allowed Values |
|---|---|
| `experience_level` | `EN`, `MI`, `SE`, `EX` |
| `employment_type` | `FT`, `PT`, `CT`, `FL` |
| `remote_ratio` | `0`, `50`, `100` |
| `company_size` | `S`, `M`, `L` |
| `employee_residence` | 2-letter ISO country code |
| `company_location` | 2-letter ISO country code |

Minimum **1 record**. No missing values allowed — entire batch is rejected on any violation.
