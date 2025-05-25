"""
This file provides an ASGI application for production deployment
For use with Gunicorn, Uvicorn, etc.
"""

from app import app as application

# This makes the app available as "asgi.application" for Gunicorn, Uvicorn, etc.
# Direct usage: uvicorn asgi:application
