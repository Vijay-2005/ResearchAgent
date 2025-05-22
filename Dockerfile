FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit>=1.27.0

# Copy the rest of the application
COPY . .

# Set up environment for production
ENV PORT=8000
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000

# Expose the ports the apps run on
EXPOSE 8000 8501

# Create a .env file with API keys at build time
RUN echo "TAVILY_API_KEY=${TAVILY_API_KEY}" > .env
RUN echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env
RUN echo "LANGCHAIN_TRACING_V2=true" >> .env
RUN echo "LANGCHAIN_PROJECT=knowledge-navigator" >> .env

# Create startup script to run both servers
RUN echo '#!/bin/bash' > start.sh
RUN echo 'python app.py & streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0' >> start.sh
RUN chmod +x start.sh

# Command to run both applications
CMD ["./start.sh"]
