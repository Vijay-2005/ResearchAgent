#!/bin/bash
# init_env.sh - Run this at container startup to prepare environment

# Create a .env file with the environment variables
echo "Creating .env file from environment variables"
echo "TAVILY_API_KEY=${TAVILY_API_KEY}" > .env
echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env
echo "LANGCHAIN_TRACING_V2=${LANGCHAIN_TRACING_V2:-true}" >> .env
echo "LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT:-langgraph-example}" >> .env
echo "API_URL=http://localhost:8000" >> .env

echo "Environment prepared successfully"
