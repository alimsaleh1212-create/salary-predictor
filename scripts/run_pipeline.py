"""Master orchestration script for the salary prediction pipeline.

Coordinates the full pre-generation workflow: calling the FastAPI API for
predictions, generating LLM narratives and visualizations via Ollama, and
persisting all results to Supabase.
"""
