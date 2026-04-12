"""
Vercel Serverless Entry Point
This forwards the `/api/*` Vercel traffic into the FastAPI `app`.
"""
from app.main import app
