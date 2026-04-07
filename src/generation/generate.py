"""Generate diverse input combinations and call the deployed FastAPI.

Uses itertools.product to systematically cover realistic input combinations,
calls the FastAPI endpoint with error handling and logging, and collects
all predictions for downstream LLM analysis.
"""
