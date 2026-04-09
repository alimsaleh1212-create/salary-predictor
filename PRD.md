# Product Requirements Document (PRD)

## Project Title
**Data Science Salary Prediction Application** – End-to-End ML Pipeline

## Version
1.3 (Updated with Model Metrics Display Requirement)

## Deadline
**Friday, 06:00 AM** (Week 1 Assignment – AIE Program)

## 1. Objective / Mission
Build and deploy a **Salary Prediction Application** for data science roles that provides actionable insights for both managers and employees.

The application will:
- Use a **Random Forest Regressor** model trained on the Kaggle Data Science Job Salaries dataset.
- Serve predictions through a **FastAPI** endpoint deployed on **Railway**.
- Allow users to upload a CSV file containing new/synthetic data (minimum 50 records) via a simple Streamlit UI.
- For each record: Call the FastAPI prediction endpoint → Pass results to a **local Dockerized Ollama** (using `gemma4:e2b` model) to generate dual-perspective insights:
  - **Manager perspective**: Recommendations on features to *decrease* salary costs.
  - **Employee perspective**: Recommendations on features to *increase* salary.
- Generate at least **one visualization** (chart) per analysis.
- Store all results (predictions, narratives, and charts) in **Supabase**.
- Provide a **separate Streamlit Dashboard** (deployed on Railway) that reads from Supabase to display all historical predictions, insights, comparative visualizations, and **model performance metrics**.

The system follows a **pre-generation architecture** with clear separation between the local generation pipeline and the deployed consumption layer.

## 2. Scope

### In Scope
- Data cleaning and preparation of the original dataset.
- Training a **Random Forest Regressor** with 80/20 train-test split and 5-fold cross-validation.
- FastAPI backend with proper input validation serving the trained model.
- Simple responsive Streamlit front-end UI for uploading CSV and triggering batch prediction + analysis.
- Integration with **local Dockerized Ollama** using the `gemma4:e2b` model.
- Well-designed Supabase schema to store predictions and insights.
- Separate deployed Streamlit Dashboard on Railway that consumes data exclusively from Supabase and displays model metrics.
- Deployment of FastAPI on **Railway** (standalone).

### Out of Scope
- Real-time LLM inference in deployed apps (Ollama remains local/Dockerized).
- User authentication or advanced security features.
- Training inside the deployed environment.

## 3. Architecture

**Local Generation Pipeline**:
CSV Upload (Streamlit UI)
→ Strict Validation → Call FastAPI (/predict) → Random Forest Prediction
→ Send inputs + prediction to Local Dockerized Ollama (gemma4:e2b)
→ Generate Manager + Employee Insights + Visualization
→ Store everything in Supabase


**Deployed Layer**:
- **FastAPI** (on Railway) – Standalone prediction endpoint.
- **Streamlit Dashboard** (on Railway) – Read-only from Supabase.

**Technology Stack**:
- **Model**: scikit-learn RandomForestRegressor
- **API**: FastAPI + Pydantic (deployed on **Railway**)
- **LLM**: Ollama in Docker with `gemma4:e2b`
- **Database**: **Supabase** (Free Hobby tier)
- **UI + Dashboard**: Streamlit
- **Deployment**: Railway (for both FastAPI and Streamlit Dashboard)

## 4. Functional Requirements

### 4.1 Model Training
- Use **Random Forest Regressor**.
- 80% train / 20% test split.
- 5-fold cross-validation for validation.
- Save model using `joblib`.
- **Final Model Performance on Test Set**:
  - Test MAE: **$27,687**
  - Test RMSE: **$39,819**
  - Test R²: **0.5863**

### 4.2 FastAPI Endpoint (Deployed on Railway)
- Endpoint: `POST /predict` (supports single record or batch).
- Strong input validation using Pydantic.
- Return predicted `salary_in_usd`.

### 4.3 Streamlit Front-End UI (CSV Uploader)
- Responsive and clean UI.
- File uploader for CSV containing new/synthetic data (**minimum 50 records**).
- Button: **"Predict & Analyze"**.

**CRITICAL REQUIREMENTS – CSV VALIDATION & ERROR HANDLING**:

> **⚠️ VERY IMPORTANT NOTES (Strict Rules – Non-Negotiable)**

> 1. **CSV Validation Must Be Extremely Strict**
>    - The uploaded CSV **must contain all required columns** exactly as used in model training.
>    - **No missing values (NaN or empty cells)** are allowed in any row or column.
>    - All categorical values must match the exact categories present in the training data (case-sensitive).
>    - If any row contains missing values or invalid data, the **entire upload must be rejected** with a clear, user-friendly error message.
>    - Implement comprehensive validation before any prediction calls are made.

> 2. **Error Handling Must Be Robust and Comprehensive**
>    - **No unhandled exceptions** anywhere in the application.
>    - Every API call, Ollama interaction, Supabase operation, and file processing must be wrapped in proper try/except blocks.
>    - Provide clear feedback to the user in the Streamlit UI for any failure.
>    - The application must never crash or show raw Python tracebacks to the user.

> 3. **Batch Processing Safety**
>    - Process records safely with progress bar.
>    - Continue processing on individual record failures and clearly report successes/failures.

### 4.3.1 Allowed Values for CSV Upload (Derived from Training Data)

The uploaded CSV must use the **raw dataset format** (same structure as `ds_salaries.csv`). The preprocessing pipeline maps raw fields to model features internally.

**Required columns**: `work_year`, `experience_level`, `employment_type`, `job_title`, `employee_residence`, `remote_ratio`, `company_location`, `company_size`

**Validation rules enforced before any prediction call**:
1. All required columns present (exact names, no extras required).
2. No `NaN` or empty cells in any row — entire batch rejected if found.
3. `experience_level`, `employment_type`, `remote_ratio`, `company_size` must be exact matches — entire batch rejected on any mismatch, with the offending rows and values listed in the error message.
4. `employee_residence` and `company_location` must be 2-letter ISO codes from the allowed lists above — entire batch rejected on any mismatch.
5. Minimum 50 records.

### 4.4 LLM Analysis (Local Dockerized Ollama – gemma4:e2b)
- Use `gemma4:e2b` model.
- Prompt must generate:
  - **Manager Insights**: Actionable advice on reducing salary costs.
  - **Employee Insights**: Actionable advice on increasing salary.
  - At least **one relevant visualization** (chart).

### 4.5 Supabase Schema
Recommended table (`salary_predictions`):

recommend best schema