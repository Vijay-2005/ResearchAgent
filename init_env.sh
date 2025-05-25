#!/bin/bash
# init_env.sh - Run this at container startup to prepare environment

# Print environment variables for debugging (without exposing full API keys)
echo "==================== ENVIRONMENT DEBUG ===================="
echo "Current environment variables available:"
for var in $(env | grep -e TAVILY -e OPENAI -e LANGCHAIN -e ANTHROPIC | cut -d '=' -f1); do
  val=$(eval echo \$$var)
  if [ ${#val} -gt 10 ]; then
    echo "$var: ${val:0:5}...${val: -5}"
  else
    echo "$var: Not set or too short"
  fi
done
echo "=========================================================="

# Create a .env file with the environment variables
echo "Creating .env file from environment variables"
echo "TAVILY_API_KEY=${TAVILY_API_KEY}" > .env
echo "OPENAI_API_KEY=${OPENAI_API_KEY}" >> .env
echo "LANGCHAIN_TRACING_V2=${LANGCHAIN_TRACING_V2:-true}" >> .env
echo "LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT:-langgraph-example}" >> .env
echo "API_URL=http://localhost:8000" >> .env
# Make sure PORT is set
echo "PORT=${PORT:-8000}" >> .env

# Verify the .env file was created correctly (without exposing full API keys)
echo "Verifying .env file:"
while IFS= read -r line; do
  var=$(echo "$line" | cut -d '=' -f1)
  val=$(echo "$line" | cut -d '=' -f2-)
  if [ ${#val} -gt 10 ]; then
    echo "$var: ${val:0:5}...${val: -5}"
  else
    echo "$var: $val"
  fi
done < .env

echo "Environment prepared successfully"
