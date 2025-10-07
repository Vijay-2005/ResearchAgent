FROM python:3.10-slim

WORKDIR /app

# Install system dependencies, Dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit>=1.27.0

# Verify pip installations
RUN pip list

# Copy the rest of the application
COPY . .

# Set up environment for production
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000
ENV PORT=8000

# Print Python version and packages for debugging
RUN python -c "import sys; print(f'Python version: {sys.version}')"

# Expose the API port
EXPOSE 8000

# Run the FastAPI application using production ASGI server
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]