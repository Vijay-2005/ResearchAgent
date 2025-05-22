from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from app import app as knowledge_app

# Mount static files
knowledge_app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Add API routes
app = knowledge_app
