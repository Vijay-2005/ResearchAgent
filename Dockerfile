FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit>=1.27.0

# Copy the rest of the application
COPY . .

# Make shell scripts executable
RUN chmod +x init_env.sh

# Set up environment for production
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000
ENV STREAMLIT_SERVER_PORT=8501
ENV PORT=10000

# Expose the ports the apps run on
EXPOSE 8000 8501 10000

# Run environment setup and then the application
CMD ["/bin/bash", "-c", "./init_env.sh && python serve.py"]
