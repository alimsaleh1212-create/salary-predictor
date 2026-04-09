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