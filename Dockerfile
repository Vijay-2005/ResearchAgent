FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit>=1.27.0

# Copy the rest of the application
COPY . .

# Set up environment for production
ENV PYTHONUNBUFFERED=1
ENV API_URL=http://localhost:8000
ENV STREAMLIT_SERVER_PORT=8501
# Render assigned port will override this
ENV PORT=10000

# Expose the ports the apps run on
EXPOSE 8000 8501 10000

# Create a .env file with API keys at build time
# Note: In production, use Render environment variables instead
RUN echo "TAVILY_API_KEY=${TAVILY_API_KEY}" > .env
RUN echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env
RUN echo "LANGCHAIN_TRACING_V2=true" >> .env
RUN echo "LANGCHAIN_PROJECT=knowledge-navigator" >> .env
RUN echo "API_URL=http://localhost:8000" >> .env

# Create a more reliable startup script
RUN echo '#!/bin/bash' > start.sh
RUN echo 'echo "Starting Knowledge Navigator on PORT=${PORT:-10000}"' >> start.sh
RUN echo 'python app.py --port 8000 &' >> start.sh
RUN echo 'APP_PID=$!' >> start.sh
RUN echo 'echo "API server started with PID $APP_PID"' >> start.sh
RUN echo 'echo "Waiting for API to start..."' >> start.sh
RUN echo 'sleep 10' >> start.sh
RUN echo 'echo "Starting Streamlit UI..."' >> start.sh
RUN echo 'streamlit run streamlit_app.py --server.port=${PORT:-10000} --server.address=0.0.0.0' >> start.sh
RUN chmod +x start.sh

# Command to run the services
# On Render, use the serve.py script which provides better process management
CMD ["python", "serve.py"]
